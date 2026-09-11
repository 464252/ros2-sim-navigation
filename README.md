# ROS2 仿真导航巡逻机器人 | Nav2 + 雷达导航 + 动态避障

## 项目简介

基于 ROS2 Humble 的仿真巡逻机器人，使用 Gazebo 仿真环境，覆盖 SLAM 建图、Nav2 自主导航、激光雷达定位、动态避障、区域识别、语音播报、拍照巡检的完整链路。

## 功能模块

| 模块 | 说明 |
|------|------|
| Gazebo 仿真环境 | 模拟房间、走廊、障碍物，提供激光雷达和相机数据 |
| Nav2 自主导航 | AMCL 定位 + DWB 局部规划 + Navfn 全局规划 |
| 雷达导航 | YDLidar 仿真插件，发布 /scan 话题，用于 SLAM 和定位 |
| 动态避障 | DWB 控制器实时检测障碍物，自动绕行 |
| SLAM 建图 | slam_toolbox 在线建图，生成栅格地图 |
| 区域识别 | 通过 TF 获取机器人位置，判断当前所在区域 |
| 语音播报 | edge-tts 合成中文语音，到达区域自动播报 |
| 拍照巡检 | 到达巡逻点后自动拍照，按时间+区域命名保存 |

## 系统架构

```
应用层     巡逻节点(导航+拍照+区域识别)  语音服务节点(edge-tts)
              │                              │
建图导航层  Cartographer/SLAM    Nav2(AMCL+DWB+Navfn)
              │                              │
驱动层      雷达驱动    里程计→TF    机器人模型    相机驱动
              │                              │
硬件层      YDLidar    STM32(仿真)    扬声器    ESP32-CAM(仿真)
```

## 包结构

```
src/
├── autopartol_robot/        # 巡逻主节点（导航+拍照+区域识别+语音播报）
├── autopatol_interfaces/    # 自定义语音服务接口
├── fishbot_application/      # 应用层工具
├── fishbot_description/     # 机器人 URDF 模型 + Gazebo 仿真世界
├── fishbot_navigation2/      # Nav2 导航配置 + 地图
├── nav2_custom_controller/  # 自定义局部控制器（学习用）
├── nav2_custom_planner/     # 自定义全局规划器（学习用）
└── README.md
```

## 依赖安装

```bash
# ROS2 Humble 相关
sudo apt install ros-humble-navigation2 ros-humble-nav2-bringup
sudo apt install ros-humble-slam-toolbox
sudo apt install ros-humble-turtlebot3-gazebo
sudo apt install ros-humble-ros2-control ros-humble-ros2-controllers

# Python 依赖
pip install edge-tts opencv-python

# 系统依赖
sudo apt install mpv
```

## 启动顺序

```bash
# 1. 启动 Gazebo 仿真环境
ros2 launch fishbot_description gazebo_sim.launch.py

# 2. SLAM 建图（新环境需要先建图）
ros2 launch slam_toolbox online_async_launch.py use_sim_time:=true
# 遥控走一圈后保存地图
ros2 run nav2_map_server map_saver_cli -f ~/map

# 3. 启动 Nav2 导航
ros2 launch fishbot_navigation2 navigation2.launch.py map:=~/map.yaml

# 4. 启动巡逻节点（导航+语音播报+拍照）
ros2 launch autopartol_robot autopatol.launch.py
```

## 核心配置

### 巡逻点（partol_config.yaml）
```yaml
target_points: [
  0.0, 0.0, 0.0,       # 原点
  5.2, 3.0, 1.57,       # 客厅
  -6.0, 3.3, 1.57,      # 卧室
  0.0, 0.0, 0.0,        # 返回原点
]
point_names: ["原点", "客厅", "卧室", "返回起点"]
```

### 区域定义
```yaml
area_names: ["客厅", "卧室", "走廊"]
area_bounds: [
  -3.24,  9.34,  -1.09,  5.42,    # 客厅
   3.41,  9.51,  -8.94, -1.23,    # 卧室
  -12.2, -1.79, -9.2,  -1.6,     # 走廊
]
```

### 拍照设置
```yaml
photo_angles: [0.0]        # 只拍前方，[0.0, 1.57, 3.14, -1.57] 拍四方向
photo_wait_time: 0.5       # 拍照前等待时间
```

## 关键技术

- **Nav2 导航栈**：AMCL 自适应蒙特卡洛定位 + DWB 局部规划器 + Navfn 全局规划器
- **动态避障**：DWB 实时扫描局部代价地图，遇到障碍自动减速绕行
- **TF 坐标变换**：map → odom → base_footprint → 激光雷达/相机
- **语音合成**：edge-tts 调用微软语音服务，线程安全设计避免 asyncio 冲突
- **配置化设计**：巡逻点、区域、拍照角度全部 yaml 可配，无需改代码

## 作者

正在找机器人运维/故障排查方向的工作，欢迎交流。
