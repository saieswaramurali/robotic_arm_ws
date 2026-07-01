cmake_minimum_required(VERSION 3.8)
project(mobile_arm_description)

find_package(ament_cmake REQUIRED)

install(
  DIRECTORY config launch rviz urdf worlds
  DESTINATION share/${PROJECT_NAME}
)

install(
  PROGRAMS
    scripts/cmd_vel_limiter.py
    scripts/hold_arm_pose.py
    scripts/odom_speed_monitor.py
    scripts/publish_wheel_joint_states.py
  DESTINATION lib/${PROJECT_NAME}
)

if(BUILD_TESTING)
  find_package(ament_lint_auto REQUIRED)
  set(ament_cmake_copyright_FOUND TRUE)
  set(ament_cmake_cpplint_FOUND TRUE)
  ament_lint_auto_find_test_dependencies()
endif()

ament_package()
