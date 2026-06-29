from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import EnvironmentVariable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    testbed_world_file = LaunchConfiguration("testbed_world_file")
    name = LaunchConfiguration("name")
    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    z = LaunchConfiguration("z")
    yaw = LaunchConfiguration("yaw")
    launch_rviz = LaunchConfiguration("launch_rviz")
    use_trajectory_controllers = LaunchConfiguration("use_trajectory_controllers")

    gazebo_resource_path = [
        PathJoinSubstitution([FindPackageShare("mobile_arm_description"), ".."]),
        ":",
        PathJoinSubstitution([FindPackageShare("arm_description"), ".."]),
        ":",
        PathJoinSubstitution([FindPackageShare("mobile_arm_bringup"), ".."]),
        ":",
        EnvironmentVariable("GZ_SIM_RESOURCE_PATH", default_value=""),
    ]

    ignition_resource_path = [
        PathJoinSubstitution([FindPackageShare("mobile_arm_description"), ".."]),
        ":",
        PathJoinSubstitution([FindPackageShare("arm_description"), ".."]),
        ":",
        PathJoinSubstitution([FindPackageShare("mobile_arm_bringup"), ".."]),
        ":",
        EnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", default_value=""),
    ]

    mobile_arm_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("mobile_arm_bringup"),
                    "launch",
                    "gazebo_control.launch.py",
                ]
            )
        ),
        launch_arguments={
            "gz_args": ["-r ", testbed_world_file],
            "name": name,
            "x": x,
            "y": y,
            "z": z,
            "yaw": yaw,
            "launch_rviz": launch_rviz,
            "use_trajectory_controllers": use_trajectory_controllers,
        }.items(),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument(
                "testbed_world_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("mobile_arm_bringup"),
                        "worlds",
                        "testbed_playground_gz.sdf",
                    ]
                ),
                description="Path to the Gazebo Sim-friendly testbed SDF world.",
            ),
            DeclareLaunchArgument("name", default_value="mobile_arm"),
            DeclareLaunchArgument("x", default_value="0.0"),
            DeclareLaunchArgument("y", default_value="0.0"),
            DeclareLaunchArgument("z", default_value="0.0"),
            DeclareLaunchArgument("yaw", default_value="0.0"),
            DeclareLaunchArgument("launch_rviz", default_value="true"),
            DeclareLaunchArgument("use_trajectory_controllers", default_value="false"),
            SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", gazebo_resource_path),
            SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", ignition_resource_path),
            mobile_arm_control,
        ]
    )
