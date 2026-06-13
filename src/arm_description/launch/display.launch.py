from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")
    description_file = LaunchConfiguration("description_file")
    rviz_config_file = LaunchConfiguration("rviz_config_file")
    tf_prefix = LaunchConfiguration("tf_prefix")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")

    robot_description_content = Command(
        [
            PathJoinSubstitution([FindExecutable(name="xacro")]),
            " ",
            description_file,
            " ",
            "ur_type:=",
            ur_type,
            " ",
            "name:=ur",
            " ",
            "safety_limits:=",
            safety_limits,
            " ",
            "safety_pos_margin:=",
            safety_pos_margin,
            " ",
            "safety_k_position:=",
            safety_k_position,
            " ",
            "tf_prefix:=",
            tf_prefix,
        ]
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("ur_type", default_value="ur5e"),
            DeclareLaunchArgument("tf_prefix", default_value=""),
            DeclareLaunchArgument("safety_limits", default_value="true"),
            DeclareLaunchArgument("safety_pos_margin", default_value="0.15"),
            DeclareLaunchArgument("safety_k_position", default_value="20"),
            DeclareLaunchArgument(
                "description_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("arm_description"),
                        "urdf",
                        "ur.urdf.xacro",
                    ]
                ),
            ),
            DeclareLaunchArgument(
                "rviz_config_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("arm_description"),
                        "rviz",
                        "view_robot.rviz",
                    ]
                ),
            ),
            Node(package="joint_state_publisher_gui", executable="joint_state_publisher_gui"),
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[{"robot_description": robot_description_content}],
            ),
            Node(package="rviz2", executable="rviz2", arguments=["-d", rviz_config_file]),
        ]
    )
