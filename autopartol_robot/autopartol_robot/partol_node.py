import math
import rclpy
from rclpy.node import Node
from rclpy.duration import Duration
from geometry_msgs.msg import PoseStamped, Pose
from nav2_simple_commander.robot_navigator import BasicNavigator, TaskResult
from tf2_ros import TransformListener, Buffer
from tf_transformations import quaternion_from_euler, euler_from_quaternion
from autopatol_interfaces.srv import SpeechText
from sensor_msgs.msg import Image  #消息接口
from cv_bridge import CvBridge #转换图像
import cv2 #保存图像

class PartolNode(BasicNavigator):
    def __init__(self, node_name='partol_node'):
        super().__init__(node_name)
        # 声明参数
        self.declare_parameter('initial_point', [0.0, 0.0, 0.0])
        self.declare_parameter('target_points', [0.0, 0.0, 0.0, 1.0, 1.0, 1.57])
        self.declare_parameter('img_save_path','')
        self.initial_point_ = self.get_parameter('initial_point').value
        self.target_points_ = self.get_parameter('target_points').value
        self.img_save_path_ = self.get_parameter('img_save_path').value
        self.buffer_ = Buffer()
        self.listener_ = TransformListener(self.buffer_, self)
        # 语音合成服务客户端
        self.speech_client_ = self.create_client(SpeechText, 'speech_text')
        self.cv_bridge_ = CvBridge()
        self.latext_img_ = Node
        self.img_sub_ = self.create_subscription(Image,'/camera_sensor/image_raw',self.img_callback,1)


    def img_callback(self,msg):
        self.latext_img_ = msg


    def record_img(self):
        if self.latext_img_ is not Node:
            pose = self.get_current_pose()
            cv_image = self.cv_bridge_.imgmsg_to_cv2(self.latext_img_)
            cv2.imwrite(
                f'{self.img_save_path_}img_{pose.translation.x:3.2f}_{pose.translation.y:3.2f}.png',
                cv_image)

            


    def get_pose_by_xyyaw(self, x, y, yaw):
        """通过 x、y、yaw 构造 PoseStamped"""
        pose = PoseStamped()
        pose.header.frame_id = 'map'
        pose.pose.position.x = float(x)
        pose.pose.position.y = float(y)
        # 欧拉角转四元数
        quat = quaternion_from_euler(0, 0, float(yaw))
        pose.pose.orientation.x = quat[0]
        pose.pose.orientation.y = quat[1]
        pose.pose.orientation.z = quat[2]
        pose.pose.orientation.w = quat[3]
        return pose

    def init_robot_pose(self):
        """初始化机器人位置"""
        init_pose = self.get_pose_by_xyyaw(
            self.initial_point_[0],
            self.initial_point_[1],
            self.initial_point_[2]
        )
        self.setInitialPose(init_pose)
        # 等待导航可用
        self.waitUntilNav2Active()

    def get_target_points(self):
        """获取目标点列表"""
        points = []
        for index in range(int(len(self.target_points_) / 3)):
            x = self.target_points_[index * 3]
            y = self.target_points_[index * 3 + 1]
            yaw = self.target_points_[index * 3 + 2]
            points.append([x, y, yaw])
        return points

    def nav_to_pose(self, target_point):
        """导航到目标点，实时显示剩余距离"""
        self.goToPose(target_point)
        while not self.isTaskComplete():
            feedback = self.getFeedback()
            if feedback:
                self.get_logger().info(
                    f'剩余距离: {feedback.distance_remaining:.2f}米'
                )
        result = self.getResult()
        if result == TaskResult.SUCCEEDED:
            self.get_logger().info('导航成功')
        elif result == TaskResult.CANCELED:
            self.get_logger().warn('导航取消')
        elif result == TaskResult.FAILED:
            self.get_logger().error('导航失败')

    def get_current_pose(self):
        """获取机器人当前位置"""
        while rclpy.ok():
            try:
                tf = self.buffer_.lookup_transform(
                    'map',
                    'base_footprint',
                    rclpy.time.Time(),
                    Duration(seconds=1.0)
                )
                return tf.transform
            except Exception as e:
                self.get_logger().warn(f'获取坐标变换失败: {str(e)}')

    def speech_text(self, text):
        """调用服务合成语音"""
        while not self.speech_client_.wait_for_service(timeout_sec=1.0):
            self.get_logger().info('等待语音合成服务上线...')
        request = SpeechText.Request()
        request.text = text
        future = self.speech_client_.call_async(request)
        rclpy.spin_until_future_complete(self, future, timeout_sec=5.0)
        if future.result() is not None:
            self.get_logger().info(f'语音合成结果: {future.result().result}')
        else:
            self.get_logger().warn('语音合成服务调用超时')

def main():
    rclpy.init()
    partol = PartolNode()
    partol.init_robot_pose()
    partol.speech_text('开始巡逻')
    while rclpy.ok():
        points = partol.get_target_points()
        for i, point in enumerate(points):
            x, y, yaw = point[0], point[1], point[2]
            # 不是第一个点，出发前说"准备前往下一目标点"
            if i > 0:
                partol.speech_text('准备前往下一目标点')
            target_pose = partol.get_pose_by_xyyaw(x, y, yaw)
            partol.nav_to_pose(target_pose)
            partol.speech_text(f'已到达目标点 {x} {y}, 正在准备记录图像')
            partol.record_img()
            partol.speech_text(f'图像记录完成')
    partol.speech_text('巡逻结束')
    partol.lifecycleShutdown()
    partol.destroy_node()
    rclpy.shutdown()

if __name__ == '__main__':
    main()