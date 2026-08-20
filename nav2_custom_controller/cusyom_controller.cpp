#include "nav2_custom_controller/custom_controller.hpp"
#include "nav2_core/exceptions.hpp"
#include "nav2_util/geometry_utils.hpp"
#include "nav2_util/node_utils.hpp"
#include <algorithm>
#include <chrono>
#include <iostream>
#include <memory>
#include <string>
#include <thread>

namespace nav2_custom_controller {
void CustomController::configure(
    const rclcpp_lifecycle::LifecycleNode::WeakPtr &parent, std::string name,
    std::shared_ptr<tf2_ros::Buffer> tf,
    std::shared_ptr<nav2_costmap_2d::Costmap2DROS> costmap_ros) {
  node_ = parent.lock();
  costmap_ros_ = costmap_ros;
  tf_ = tf;
  plugin_name_ = name;

  // 声明并获取参数，设置最大线速度和最大角速度
  nav2_util::declare_parameter_if_not_declared(
      node_, plugin_name_ + ".max_linear_speed", rclcpp::ParameterValue(0.1));
  node_->get_parameter(plugin_name_ + ".max_linear_speed", max_linear_speed_);
  nav2_util::declare_parameter_if_not_declared(
      node_, plugin_name_ + ".max_angular_speed", rclcpp::ParameterValue(1.0));
  node_->get_parameter(plugin_name_ + ".max_angular_speed", max_angular_speed_);
}

void CustomController::cleanup() {
  RCLCPP_INFO(node_->get_logger(),
              "清理控制器：%s 类型为 nav2_custom_controller::CustomController",
              plugin_name_.c_str());
}

void CustomController::activate() {
  RCLCPP_INFO(node_->get_logger(),
              "激活控制器：%s 类型为 nav2_custom_controller::CustomController",
              plugin_name_.c_str());
}

void CustomController::deactivate() {
  RCLCPP_INFO(node_->get_logger(),
              "停用控制器：%s 类型为 nav2_custom_controller::CustomController",
              plugin_name_.c_str());
}

geometry_msgs::msg::TwistStamped CustomController::computeVelocityCommands(
    const geometry_msgs::msg::PoseStamped &pose,
    const geometry_msgs::msg::Twist &, nav2_core::GoalChecker *) {
  // 4.根据角度差计算线速度和角速度
  geometry_msgs::msg::TwistStamped cmd_vel;
  return cmd_vel;
}

void CustomController::setSpeedLimit(const double &speed_limit,
                                     const bool &percentage) {
  (void)percentage;
  (void)speed_limit;
}

void CustomController::setPlan(const nav_msgs::msg::Path &path) {
  global_plan_ = path;
}

geometry_msgs::msg::PoseStamped CustomController::getNearestTargetPose(
    const geometry_msgs::msg::PoseStamped &current_pose) {
  return current_pose;
}

double CustomController::calculateAngleDifference(
    const geometry_msgs::msg::PoseStamped &current_pose,
    const geometry_msgs::msg::PoseStamped &target_pose) {
  return 0.0f;
}
} // namespace nav2_custom_controller

#include "pluginlib/class_list_macros.hpp"
PLUGINLIB_EXPORT_CLASS(nav2_custom_controller::CustomController,nav2_core::Controller)