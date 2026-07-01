cmake_minimum_required(VERSION 3.8)
project(arm_kinematics)

if(CMAKE_COMPILER_IS_GNUCXX OR CMAKE_CXX_COMPILER_ID MATCHES "Clang")
  add_compile_options(-Wall -Wextra -Wpedantic)
endif()

# find dependencies
find_package(ament_cmake REQUIRED)
find_package(rclcpp REQUIRED)
find_package(arm_interfaces REQUIRED)
find_package(geometry_msgs REQUIRED)
find_package(sensor_msgs REQUIRED)
find_package(trajectory_msgs REQUIRED)
find_package(control_msgs REQUIRED)
find_package(rclcpp_action REQUIRED)
find_package(kdl_parser REQUIRED)
find_package(urdf REQUIRED)
find_package(orocos_kdl REQUIRED)
find_package(builtin_interfaces REQUIRED)

add_executable(trajectory_planner_node src/trajectory_planner_node.cpp)
ament_target_dependencies(trajectory_planner_node
  rclcpp
  arm_interfaces
  geometry_msgs
  sensor_msgs
  trajectory_msgs
  control_msgs
  rclcpp_action
  kdl_parser
  urdf
  orocos_kdl
)

add_executable(move_to_pose_cli src/move_to_pose_cli.cpp)
ament_target_dependencies(move_to_pose_cli
  rclcpp
  arm_interfaces
)

install(TARGETS
  trajectory_planner_node
  move_to_pose_cli
  DESTINATION lib/${PROJECT_NAME}
)

install(DIRECTORY
  launch
  DESTINATION share/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  # the following line skips the linter which checks for copyrights
  # comment the line when a copyright and license is added to all source files
  set(ament_cmake_copyright_FOUND TRUE)
  # the following line skips cpplint (only works in a git repo)
  # comment the line when this package is in a git repo and when
  # a copyright and license is added to all source files
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
