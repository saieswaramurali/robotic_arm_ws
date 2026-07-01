from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    kinematics_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("arm_bringup"), "launch", "kinematics_control.launch.py"]
            )
        ),
        launch_arguments={
            "bridge_camera": LaunchConfiguration("bridge_camera"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
        }.items(),
    )

    spawn_cylinder = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-file",
            PathJoinSubstitution(
                [FindPackageShare("arm_description"), "models", "pick_cylinder", "model.sdf"]
            ),
            "-name",
            "pick_cylinder",
            "-x",
            LaunchConfiguration("object_x"),
            "-y",
            LaunchConfiguration("object_y"),
            "-z",
            "0.06",
            "-allow_renaming",
            "false",
        ],
        output="screen",
    )

    pick_place_demo = Node(
        package="arm_pick_place",
        executable="predefined_pick_place_node",
        output="screen",
        parameters=[
            {
                "object_x": ParameterValue(LaunchConfiguration("object_x"), value_type=float),
                "object_y": ParameterValue(LaunchConfiguration("object_y"), value_type=float),
                "pick_z": ParameterValue(LaunchConfiguration("pick_z"), value_type=float),
                "approach_z": ParameterValue(LaunchConfiguration("approach_z"), value_type=float),
                "place_x": ParameterValue(LaunchConfiguration("place_x"), value_type=float),
                "place_y": ParameterValue(LaunchConfiguration("place_y"), value_type=float),
                "place_z": ParameterValue(LaunchConfiguration("place_z"), value_type=float),
                "retreat_z": ParameterValue(LaunchConfiguration("retreat_z"), value_type=float),
                "tool_qx": ParameterValue(LaunchConfiguration("tool_qx"), value_type=float),
                "tool_qy": ParameterValue(LaunchConfiguration("tool_qy"), value_type=float),
                "tool_qz": ParameterValue(LaunchConfiguration("tool_qz"), value_type=float),
                "tool_qw": ParameterValue(LaunchConfiguration("tool_qw"), value_type=float),
                "move_duration": ParameterValue(
                    LaunchConfiguration("move_duration"), value_type=float
                ),
                "use_sim_time": ParameterValue(
                    LaunchConfiguration("use_sim_time"), value_type=bool
                ),
            }
        ],
        condition=IfCondition(LaunchConfiguration("run_demo")),
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("bridge_camera", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("run_demo", default_value="true"),
            DeclareLaunchArgument("object_x", default_value="0.38"),
            DeclareLaunchArgument("object_y", default_value="0.18"),
            DeclareLaunchArgument("pick_z", default_value="0.125"),
            DeclareLaunchArgument("approach_z", default_value="0.30"),
            DeclareLaunchArgument("place_x", default_value="0.38"),
            DeclareLaunchArgument("place_y", default_value="-0.08"),
            DeclareLaunchArgument("place_z", default_value="0.125"),
            DeclareLaunchArgument("retreat_z", default_value="0.30"),
            DeclareLaunchArgument("tool_qx", default_value="0.0"),
            DeclareLaunchArgument("tool_qy", default_value="1.0"),
            DeclareLaunchArgument("tool_qz", default_value="0.0"),
            DeclareLaunchArgument("tool_qw", default_value="0.0"),
            DeclareLaunchArgument("move_duration", default_value="3.5"),
            kinematics_control,
            TimerAction(period=4.0, actions=[spawn_cylinder]),
            TimerAction(period=12.0, actions=[pick_place_demo]),
        ]
    )
