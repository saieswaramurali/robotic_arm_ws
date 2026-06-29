#include <array>
#include <chrono>
#include <memory>
#include <string>
#include <vector>

#include <geometry_msgs/msg/pose_stamped.hpp>
#include <rclcpp/rclcpp.hpp>
#include <trajectory_msgs/msg/joint_trajectory.hpp>
#include <trajectory_msgs/msg/joint_trajectory_point.hpp>

#include "arm_interfaces/srv/move_to_pose.hpp"

using namespace std::chrono_literals;

namespace
{

using MoveToPose = arm_interfaces::srv::MoveToPose;

constexpr std::array<const char *, 11> kGripperJoints = {
  "robotiq_palm_finger_1_joint",
  "robotiq_finger_1_joint_1",
  "robotiq_finger_1_joint_2",
  "robotiq_finger_1_joint_3",
  "robotiq_palm_finger_2_joint",
  "robotiq_finger_2_joint_1",
  "robotiq_finger_2_joint_2",
  "robotiq_finger_2_joint_3",
  "robotiq_finger_middle_joint_1",
  "robotiq_finger_middle_joint_2",
  "robotiq_finger_middle_joint_3",
};

std::vector<double> openGripper()
{
  return {0.0, 0.05, 0.05, -0.05, 0.0, 0.05, 0.05, -0.05, 0.05, 0.05, -0.05};
}

std::vector<double> closedGripper()
{
  return {0.1, 0.75, 0.75, -0.75, -0.1, 0.75, 0.75, -0.75, 0.75, 0.75, -0.75};
}

}  // namespace

class PredefinedPickPlaceNode : public rclcpp::Node
{
public:
  PredefinedPickPlaceNode()
  : Node("predefined_pick_place_node")
  {
    move_client_ = create_client<MoveToPose>("/move_to_pose");
    gripper_pub_ = create_publisher<trajectory_msgs::msg::JointTrajectory>(
      "/gripper_controller/joint_trajectory", 10);

    object_x_ = declare_parameter<double>("object_x", 0.38);
    object_y_ = declare_parameter<double>("object_y", 0.18);
    pick_z_ = declare_parameter<double>("pick_z", 0.125);
    approach_z_ = declare_parameter<double>("approach_z", 0.30);
    place_x_ = declare_parameter<double>("place_x", 0.38);
    place_y_ = declare_parameter<double>("place_y", -0.08);
    place_z_ = declare_parameter<double>("place_z", 0.125);
    retreat_z_ = declare_parameter<double>("retreat_z", 0.30);
    tool_qx_ = declare_parameter<double>("tool_qx", 0.0);
    tool_qy_ = declare_parameter<double>("tool_qy", 1.0);
    tool_qz_ = declare_parameter<double>("tool_qz", 0.0);
    tool_qw_ = declare_parameter<double>("tool_qw", 0.0);
    move_duration_ = declare_parameter<double>("move_duration", 3.5);
  }

  bool run()
  {
    RCLCPP_INFO(get_logger(), "Waiting for /move_to_pose service");
    if (!move_client_->wait_for_service(30s)) {
      RCLCPP_ERROR(get_logger(), "Service /move_to_pose is not available");
      return false;
    }

    RCLCPP_INFO(get_logger(), "Starting predefined cylinder pick-place sequence");
    publishGripper(openGripper(), 2.0);
    sleepFor(2s);

    if (!moveTo("pre-pick", object_x_, object_y_, approach_z_)) {
      return false;
    }
    if (!moveTo("pick", object_x_, object_y_, pick_z_)) {
      return false;
    }

    publishGripper(closedGripper(), 2.0);
    sleepFor(2s);

    if (!moveTo("lift", object_x_, object_y_, retreat_z_)) {
      return false;
    }
    if (!moveTo("pre-place", place_x_, place_y_, retreat_z_)) {
      return false;
    }
    if (!moveTo("place", place_x_, place_y_, place_z_)) {
      return false;
    }

    publishGripper(openGripper(), 2.0);
    sleepFor(2s);

    if (!moveTo("retreat", place_x_, place_y_, retreat_z_)) {
      return false;
    }

    RCLCPP_INFO(get_logger(), "Predefined pick-place sequence finished");
    return true;
  }

private:
  void sleepFor(std::chrono::seconds duration)
  {
    rclcpp::sleep_for(duration);
  }

  void publishGripper(const std::vector<double> & positions, double duration)
  {
    trajectory_msgs::msg::JointTrajectory trajectory;
    trajectory.header.stamp = now();
    for (const char * joint : kGripperJoints) {
      trajectory.joint_names.push_back(joint);
    }

    trajectory_msgs::msg::JointTrajectoryPoint point;
    point.positions = positions;
    point.time_from_start.sec = static_cast<int32_t>(duration);
    trajectory.points.push_back(point);
    gripper_pub_->publish(trajectory);
  }

  bool moveTo(const std::string & label, double x, double y, double z)
  {
    auto request = std::make_shared<MoveToPose::Request>();
    request->target_pose.header.frame_id = "base_link";
    request->target_pose.pose.position.x = x;
    request->target_pose.pose.position.y = y;
    request->target_pose.pose.position.z = z;
    request->target_pose.pose.orientation.x = tool_qx_;
    request->target_pose.pose.orientation.y = tool_qy_;
    request->target_pose.pose.orientation.z = tool_qz_;
    request->target_pose.pose.orientation.w = tool_qw_;
    request->duration = move_duration_;
    request->execute = true;

    RCLCPP_INFO(
      get_logger(),
      "Move %s: x=%.3f y=%.3f z=%.3f q=(%.2f, %.2f, %.2f, %.2f)",
      label.c_str(), x, y, z, tool_qx_, tool_qy_, tool_qz_, tool_qw_);
    auto future = move_client_->async_send_request(request);
    const auto result = rclcpp::spin_until_future_complete(
      shared_from_this(), future, std::chrono::seconds(20));
    if (result != rclcpp::FutureReturnCode::SUCCESS) {
      RCLCPP_ERROR(get_logger(), "Move %s timed out", label.c_str());
      return false;
    }

    const auto response = future.get();
    if (!response->success) {
      RCLCPP_ERROR(get_logger(), "Move %s failed: %s", label.c_str(), response->message.c_str());
      return false;
    }

    RCLCPP_INFO(get_logger(), "Move %s ok: %s", label.c_str(), response->message.c_str());
    sleepFor(std::chrono::seconds(static_cast<int>(move_duration_) + 1));
    return true;
  }

  rclcpp::Client<MoveToPose>::SharedPtr move_client_;
  rclcpp::Publisher<trajectory_msgs::msg::JointTrajectory>::SharedPtr gripper_pub_;
  double object_x_{0.38};
  double object_y_{0.18};
  double pick_z_{0.125};
  double approach_z_{0.30};
  double place_x_{0.38};
  double place_y_{-0.08};
  double place_z_{0.125};
  double retreat_z_{0.30};
  double tool_qx_{0.0};
  double tool_qy_{1.0};
  double tool_qz_{0.0};
  double tool_qw_{0.0};
  double move_duration_{3.5};
};

int main(int argc, char ** argv)
{
  rclcpp::init(argc, argv);
  const auto node = std::make_shared<PredefinedPickPlaceNode>();
  const bool success = node->run();
  rclcpp::shutdown();
  return success ? 0 : 1;
}
