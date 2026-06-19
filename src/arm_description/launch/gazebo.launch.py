from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, SetEnvironmentVariable, TimerAction
from launch.conditions import IfCondition
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import Command, EnvironmentVariable, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")
    description_file = LaunchConfiguration("description_file")
    gz_args = LaunchConfiguration("gz_args")
    name = LaunchConfiguration("name")
    tf_prefix = LaunchConfiguration("tf_prefix")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")
    x = LaunchConfiguration("x")
    y = LaunchConfiguration("y")
    z = LaunchConfiguration("z")
    roll = LaunchConfiguration("roll")
    pitch = LaunchConfiguration("pitch")
    yaw = LaunchConfiguration("yaw")
    bridge_camera = LaunchConfiguration("bridge_camera")
    launch_rviz = LaunchConfiguration("launch_rviz")
    rviz_config_file = LaunchConfiguration("rviz_config_file")
    use_sim_time = LaunchConfiguration("use_sim_time")
    use_sim_time_param = ParameterValue(use_sim_time, value_type=bool)

    robot_description_content = Command(
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
            " ",
            "force_abs_paths:=true",
        ]
    )

    robot_state_publisher = Node(
        package="robot_state_publisher",
        executable="robot_state_publisher",
        parameters=[
            {
                "robot_description": robot_description_content,
                "use_sim_time": use_sim_time_param,
            }
        ],
        output="screen",
    )

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

    camera_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/clock@rosgraph_msgs/msg/Clock[gz.msgs.Clock",
            "/wrist_camera/color@sensor_msgs/msg/Image[gz.msgs.Image",
            "/wrist_camera/depth@sensor_msgs/msg/Image[gz.msgs.Image",
            "/wrist_camera/depth/points@sensor_msgs/msg/PointCloud2[gz.msgs.PointCloudPacked",
        ],
        remappings=[
            ("/wrist_camera/color", "/wrist_camera/color/image"),
            ("/wrist_camera/depth", "/wrist_camera/depth/image"),
            ("/wrist_camera/depth/points", "/wrist_camera/depth/points"),
        ],
        output="screen",
        condition=IfCondition(bridge_camera),
    )

    color_camera_info_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/wrist_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        remappings=[
            ("/wrist_camera/camera_info", "/wrist_camera/color/camera_info"),
        ],
        output="screen",
        condition=IfCondition(bridge_camera),
    )

    depth_camera_info_bridge = Node(
        package="ros_gz_bridge",
        executable="parameter_bridge",
        arguments=[
            "/wrist_camera/camera_info@sensor_msgs/msg/CameraInfo[gz.msgs.CameraInfo",
        ],
        remappings=[
            ("/wrist_camera/camera_info", "/wrist_camera/depth/camera_info"),
        ],
        output="screen",
        condition=IfCondition(bridge_camera),
    )

    joint_state_publisher = Node(
        package="joint_state_publisher",
        executable="joint_state_publisher",
        parameters=[
            {
                "robot_description": robot_description_content,
                "use_sim_time": use_sim_time_param,
            }
        ],
        output="screen",
    )

    rviz = Node(
        package="rviz2",
        executable="rviz2",
        arguments=["-d", rviz_config_file],
        parameters=[{"use_sim_time": use_sim_time_param}],
        output="screen",
        condition=IfCondition(launch_rviz),
    )

    depth_points_frame_tf = Node(
        package="tf2_ros",
        executable="static_transform_publisher",
        arguments=[
            "--x",
            "0",
            "--y",
            "0",
            "--z",
            "0",
            "--roll",
            "0",
            "--pitch",
            "0",
            "--yaw",
            "0",
            "--frame-id",
            "wrist_camera_depth_frame",
            "--child-frame-id",
            "ur/wrist_3_link/wrist_camera_depth_sensor",
        ],
        parameters=[{"use_sim_time": use_sim_time_param}],
        output="screen",
        condition=IfCondition(bridge_camera),
    )

    gazebo_resource_path = [
        PathJoinSubstitution([FindPackageShare("arm_description"), ".."]),
        ":",
        EnvironmentVariable("GZ_SIM_RESOURCE_PATH", default_value=""),
    ]

    ignition_resource_path = [
        PathJoinSubstitution([FindPackageShare("arm_description"), ".."]),
        ":",
        EnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", default_value=""),
    ]

    return LaunchDescription(
        [
            DeclareLaunchArgument("ur_type", default_value="ur5e"),
            DeclareLaunchArgument("name", default_value="ur"),
            DeclareLaunchArgument("tf_prefix", default_value=""),
            DeclareLaunchArgument("safety_limits", default_value="true"),
            DeclareLaunchArgument("safety_pos_margin", default_value="0.15"),
            DeclareLaunchArgument("safety_k_position", default_value="20"),
            DeclareLaunchArgument("x", default_value="0.0"),
            DeclareLaunchArgument("y", default_value="0.0"),
            DeclareLaunchArgument("z", default_value="0.0"),
            DeclareLaunchArgument("roll", default_value="0.0"),
            DeclareLaunchArgument("pitch", default_value="0.0"),
            DeclareLaunchArgument("yaw", default_value="0.0"),
            DeclareLaunchArgument(
                "gz_args",
                default_value=[
                    "-r ",
                    PathJoinSubstitution(
                        [FindPackageShare("arm_description"), "worlds", "arm_camera.sdf"]
                    ),
                ],
            ),
            DeclareLaunchArgument("bridge_camera", default_value="true"),
            DeclareLaunchArgument("launch_rviz", default_value="true"),
            DeclareLaunchArgument("use_sim_time", default_value="true"),
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
            SetEnvironmentVariable("GZ_SIM_RESOURCE_PATH", gazebo_resource_path),
            SetEnvironmentVariable("IGN_GAZEBO_RESOURCE_PATH", ignition_resource_path),
            gz_sim,
            robot_state_publisher,
            joint_state_publisher,
            rviz,
            TimerAction(period=2.0, actions=[spawn_robot]),
            TimerAction(
                period=4.0,
                actions=[
                    camera_bridge,
                    color_camera_info_bridge,
                    depth_camera_info_bridge,
                    depth_points_frame_tf,
                ],
            ),
        ]
    )
