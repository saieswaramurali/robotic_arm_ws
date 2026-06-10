from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="arm_description",
            executable="01_wrist_rgbd",
            name="wrist_rgbd_capture",
            output="screen",
        ),
    ])
