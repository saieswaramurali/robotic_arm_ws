from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="arm_description",
            executable="02_pick_and_place_env",
            name="view_pick_and_place_tables",
            output="screen",
            arguments=["--scene", "pick_and_place_tables.xml"],
        ),
    ])
