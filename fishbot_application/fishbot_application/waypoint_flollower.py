#########多点导航#########
from geometry_msgs.msg import PoseStamped
from nav2_simple_commander.robot_navigator import BasicNavigator
import rclpy

def main():
    rclpy.init()
    nav = BasicNavigator()
    nav.waitUntilNav2Active() #等待导航可用

    goal_poses = []
    # 航点1
    goal_pose = PoseStamped()
    goal_pose.header.frame_id = "map"
    goal_pose.header.stamp = nav.get_clock().now().to_msg()
    goal_pose.pose.position.x = 2.0
    goal_pose.pose.position.y = 0.0
    goal_pose.pose.orientation.w = 1.0
    goal_poses.append(goal_pose)

    # 航点2
    goal_pose1 = PoseStamped()
    goal_pose1.header.frame_id = "map"
    goal_pose1.header.stamp = nav.get_clock().now().to_msg()
    goal_pose1.pose.position.x = 4.0
    goal_pose1.pose.position.y = 0.0
    goal_pose1.pose.orientation.w = 1.0
    goal_poses.append(goal_pose1)

    # 航点3
    goal_pose2 = PoseStamped()
    goal_pose2.header.frame_id = "map"
    goal_pose2.header.stamp = nav.get_clock().now().to_msg()
    goal_pose2.pose.position.x = 0.0
    goal_pose2.pose.position.y = 0.0
    goal_pose2.pose.orientation.w = 1.0
    goal_poses.append(goal_pose2)


    nav.followWaypoints(goal_poses)

    while not nav.isTaskComplete():
        feedback = nav.getFeedback()
        nav.get_logger().info(f'路点编号:{feedback.current_waypoint}')

    result = nav.getResult()
    nav.get_logger().info(f'导航结果:{result}')

    # rclpy.shutdown() # 必须放到main最后

if __name__ == '__main__':
    main()