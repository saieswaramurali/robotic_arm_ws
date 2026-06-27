#include <chrono>
#include <cstdlib>
#include <iostream>
#include <memory>
#include <string>

#include <rclcpp/rclcpp.hpp>

#include "arm_interfaces/srv/move_to_pose.hpp"

namespace
{

using MoveToPose = arm_interfaces::srv::MoveToPose;

double parseDouble(const char * value, const std::string & name)
{
  char * end = nullptr;
  const double parsed = std::strtod(value, &end);
  if (end == value || *end != '\0') {
    throw std::runtime_error("Invalid " + name + ": " + value);
  }
  return parsed;
}

void printUsage()
{
  std::cerr
    << "Usage:\n"
    << "  ros2 run arm_kinematics move_to_pose_cli x y z [qx qy qz qw] [duration] [execute]\n\n"
    << "Examples:\n"
    << "  ros2 run arm_kinematics move_to_pose_cli 0.35 0.10 0.45\n"
    << "  ros2 run arm_kinematics move_to_pose_cli 0.35 0.10 0.45 0 0 0 1 4 true\n";
}

}  // namespace

int main(int argc, char ** argv)
{
  if (!(argc == 4 || argc == 8 || argc == 9 || argc == 10)) {
    printUsage();
    return 2;
  }

  rclcpp::init(argc, argv);
  auto node = std::make_shared<rclcpp::Node>("move_to_pose_cli");
  auto client = node->create_client<MoveToPose>("/move_to_pose");

  if (!client->wait_for_service(std::chrono::seconds(5))) {
    std::cerr << "Service /move_to_pose is not available.\n";
    rclcpp::shutdown();
    return 1;
  }

  auto request = std::make_shared<MoveToPose::Request>();
  try {
    request->target_pose.header.frame_id = "base_link";
    request->target_pose.pose.position.x = parseDouble(argv[1], "x");
    request->target_pose.pose.position.y = parseDouble(argv[2], "y");
    request->target_pose.pose.position.z = parseDouble(argv[3], "z");
    request->target_pose.pose.orientation.x = 0.0;
    request->target_pose.pose.orientation.y = 0.0;
    request->target_pose.pose.orientation.z = 0.0;
    request->target_pose.pose.orientation.w = 1.0;
    request->duration = 4.0;
    request->execute = true;

    if (argc >= 8) {
      request->target_pose.pose.orientation.x = parseDouble(argv[4], "qx");
      request->target_pose.pose.orientation.y = parseDouble(argv[5], "qy");
      request->target_pose.pose.orientation.z = parseDouble(argv[6], "qz");
      request->target_pose.pose.orientation.w = parseDouble(argv[7], "qw");
    }
    if (argc >= 9) {
      request->duration = parseDouble(argv[8], "duration");
    }
    if (argc >= 10) {
      const std::string execute_arg = argv[9];
      request->execute =
        execute_arg == "true" || execute_arg == "1" || execute_arg == "yes";
    }
  } catch (const std::exception & error) {
    std::cerr << error.what() << "\n";
    printUsage();
    rclcpp::shutdown();
    return 2;
  }

  auto future = client->async_send_request(request);
  const auto result = rclcpp::spin_until_future_complete(node, future, std::chrono::seconds(15));
  if (result != rclcpp::FutureReturnCode::SUCCESS) {
    std::cerr << "Timed out waiting for /move_to_pose response.\n";
    rclcpp::shutdown();
    return 1;
  }

  const auto response = future.get();
  std::cout << "success: " << (response->success ? "true" : "false") << "\n";
  std::cout << "message: " << response->message << "\n";
  std::cout << "joints:";
  for (const double joint : response->joints) {
    std::cout << " " << joint;
  }
  std::cout << "\ntrajectory_points: " << response->trajectory.points.size() << "\n";

  rclcpp::shutdown();
  return response->success ? 0 : 1;
}
