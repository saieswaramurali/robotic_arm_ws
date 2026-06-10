from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="arm_description",
            executable="00_display_scene",
            name="view_scene",
            output="screen",
        ),
    ])
