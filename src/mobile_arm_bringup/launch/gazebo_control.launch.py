from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition, UnlessCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")
    description_file = LaunchConfiguration("description_file")
    controllers_file = LaunchConfiguration("controllers_file")
    gz_args = LaunchConfiguration("gz_args")
    name = LaunchConfiguration("name")
    arm_prefix = LaunchConfiguration("arm_prefix")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")
    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    z = LaunchConfiguration("z")
    roll = LaunchConfiguration("roll")
    pitch = LaunchConfiguration("pitch")
    yaw = LaunchConfiguration("yaw")
    launch_rviz = LaunchConfiguration("launch_rviz")
    rviz_config_file = LaunchConfiguration("rviz_config_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_trajectory_controllers = LaunchConfiguration("use_trajectory_controllers")
    use_sim_time_param = ParameterValue(use_sim_time, value_type=bool)

    robot_description_content = ParameterValue(
        Command(
            [
                PathJoinSubstitution([FindExecutable(name="xacro")]),
                " ",
                description_file,
                " ",
                "ur_type:=",
                ur_type,
                " ",
                "name:=",
                name,
                " ",
                "arm_prefix:=",
                arm_prefix,
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
                "force_abs_paths:=true",
                " ",
                "controllers_file:=",
                controllers_file,
                " ",
                "use_ros2_control:=true",
                " ",
                "include_gz_camera_sensors:=false",
            ]
        ),
        value_type=str,
    )

    robot_description = {"robot_description": robot_description_content}

    gz_sim = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("ros_gz_sim"), "launch", "gz_sim.launch.py"]
            )
        ),
        launch_arguments={"gz_args": gz_args, "on_exit_shutdown": "true"}.items(),
    )

    spawn_robot = Node(
        package="ros_gz_sim",
        executable="create",
        arguments=[
            "-topic",
            "/robot_description",
            "-name",
            name,
            "-x",
            x,
            "-y",
            y,
            "-z",
            z,
            "-R",
            roll,
            "-P",
            pitch,
            "-Y",
            yaw,
            "-allow_renaming",
            "true",
        ],
        output="screen",
    )

    bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/cmd_vel@geometry_msgs/msg/Twist@gz.msgs.Twist",
            "/odom@nav_msgs/msg/Odometry[gz.msgs.Odometry",
            "/tf@tf2_msgs/msg/TFMessage[gz.msgs.Pose_V",
        ],
        output="screen",
    )

    joint_state_broadcaster_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["joint_state_broadcaster", "--controller-manager", "/controller_manager"],
        output="screen",
    )

    arm_controller_spawner_active = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager"],
        output="screen",
        condition=IfCondition(use_trajectory_controllers),
    )

    gripper_controller_spawner_active = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "--controller-manager", "/controller_manager"],
        output="screen",
        condition=IfCondition(use_trajectory_controllers),
    )

    arm_controller_spawner_inactive = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["arm_controller", "--controller-manager", "/controller_manager", "--inactive"],
        output="screen",
        condition=UnlessCondition(use_trajectory_controllers),
    )

    gripper_controller_spawner_inactive = Node(
        package="controller_manager",
        executable="spawner",
        arguments=["gripper_controller", "--controller-manager", "/controller_manager", "--inactive"],
        output="screen",
        condition=UnlessCondition(use_trajectory_controllers),
    )

    position_controller_spawner = Node(
        package="controller_manager",
        executable="spawner",
        arguments=[
            "arm_position_controller",
            "gripper_position_controller",
            "--controller-manager",
            "/controller_manager",
        ],
        output="screen",
        condition=UnlessCondition(use_trajectory_controllers),
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config_file],
        parameters=[{"use_sim_time": use_sim_time_param}],
        output="screen",
        condition=IfCondition(launch_rviz),
    )

    gazebo_resource_path = [
        PathJoinSubstitution([FindPackageShare("mobile_arm_description"), ".."]),
        ":",
        PathJoinSubstitution([FindPackageShare("arm_description"), ".."]),
        ":",
        EnvironmentVariable("GZ_SIM_RESOURCE_PATH", default_value=""),
    ]

    ignition_resource_path = [
        PathJoinSubstitution([FindPackageShare("mobile_arm_description"), ".."]),
        ":",
        PathJoinSubstitution([FindPackageShare("arm_description"), ".."]),
        ":",
        EnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", default_value=""),
    ]

    return LaunchDescription(
        [
            DeclareLaunchArgument("ur_type", default_value="ur5e"),
            DeclareLaunchArgument("name", default_value="mobile_arm"),
            DeclareLaunchArgument("arm_prefix", default_value="arm_"),
            DeclareLaunchArgument("safety_limits", default_value="true"),
            DeclareLaunchArgument("safety_pos_margin", default_value="0.15"),
            DeclareLaunchArgument("safety_k_position", default_value="20"),
            DeclareLaunchArgument("x", default_value="0.0"),
            DeclareLaunchArgument("y", default_value="0.0"),
            DeclareLaunchArgument("z", default_value="0.0"),
            DeclareLaunchArgument("roll", default_value="0.0"),
            DeclareLaunchArgument("pitch", default_value="0.0"),
            DeclareLaunchArgument("yaw", default_value="0.0"),
            DeclareLaunchArgument("launch_rviz", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument("use_trajectory_controllers", default_value="false"),
            DeclareLaunchArgument(
                "gz_args",
                default_value=[
                    "-r ",
                    PathJoinSubstitution(
                        [FindPackageShare("mobile_arm_description"), "worlds", "empty.sdf"]
                    ),
                ],
            ),
            DeclareLaunchArgument(
                "description_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("mobile_arm_description"),
                        "urdf",
                        "mobile_arm.urdf.xacro",
                    ]
                ),
            ),
            DeclareLaunchArgument(
                "controllers_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("mobile_arm_bringup"),
                        "config",
                        "mobile_arm_controllers.yaml",
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
            SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", gazebo_resource_path),
            SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", ignition_resource_path),
            gz_sim,
            Node(
                package="robot_state_publisher",
                executable="robot_state_publisher",
                parameters=[robot_description, {"use_sim_time": use_sim_time_param}],
                output="screen",
            ),
            Node(
                package="demo_nodes_cpp",
                executable="parameter_blackboard",
                name="robot_description_control_server",
                parameters=[robot_description],
                output="screen",
            ),
            bridge,
            rviz,
            TimerAction(period=2.0, actions=[spawn_robot]),
            TimerAction(
                period=5.0,
                actions=[
                    joint_state_broadcaster_spawner,
                    arm_controller_spawner_active,
                    gripper_controller_spawner_active,
                    arm_controller_spawner_inactive,
                    gripper_controller_spawner_inactive,
                    position_controller_spawner,
                ],
            ),
        ]
    )
