#!/usr/bin/env python3

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_mobile_arm_nav = get_package_share_directory("mobile_arm_nav")

    use_sim_time = LaunchConfiguration("use_sim_time")
    map_name = LaunchConfiguration("map")

    localization_params = {
        "use_sim_time": use_sim_time,
        "odom_frame": "odom",
        "map_frame": "map",
        "base_frame": "base_link",
        "scan_topic": "/scan",
        "mode": "localization",
        "map_file_name": [os.path.join(pkg_mobile_arm_nav, "maps", ""), map_name],
        "map_start_pose": [0.0, 0.0, 0.0],
    }

    return LaunchDescription(
        [
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("map", default_value="testbed_map"),
            Node(
                package="slam_toolbox",
                executable="localization_slam_toolbox_node",
                name="slam_toolbox",
                output="screen",
                parameters=[localization_params],
            ),
        ]
    )
