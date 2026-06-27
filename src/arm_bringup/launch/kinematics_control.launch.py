from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, IncludeLaunchDescription, TimerAction
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch.substitutions import LaunchConfiguration, PathJoinSubstitution
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    gazebo_control = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [FindPackageShare("arm_bringup"), "launch", "gazebo_control.launch.py"]
            )
        ),
        launch_arguments={
            "ur_type": LaunchConfiguration("ur_type"),
            "name": LaunchConfiguration("name"),
            "tf_prefix": LaunchConfiguration("tf_prefix"),
            "safety_limits": LaunchConfiguration("safety_limits"),
            "safety_pos_margin": LaunchConfiguration("safety_pos_margin"),
            "safety_k_position": LaunchConfiguration("safety_k_position"),
            "x": LaunchConfiguration("x"),
            "y": LaunchConfiguration("y"),
            "z": LaunchConfiguration("z"),
            "roll": LaunchConfiguration("roll"),
            "pitch": LaunchConfiguration("pitch"),
            "yaw": LaunchConfiguration("yaw"),
            "gz_args": LaunchConfiguration("gz_args"),
            "bridge_camera": LaunchConfiguration("bridge_camera"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
            "description_file": LaunchConfiguration("description_file"),
            "controllers_file": LaunchConfiguration("controllers_file"),
            "use_trajectory_controllers": "true",
        }.items(),
    )

    kdl_planner = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            PathJoinSubstitution(
                [
                    FindPackageShare("arm_kinematics"),
                    "launch",
                    "trajectory_planner.launch.py",
                ]
            )
        ),
        launch_arguments={
            "ur_type": LaunchConfiguration("ur_type"),
            "name": LaunchConfiguration("name"),
            "tf_prefix": LaunchConfiguration("tf_prefix"),
            "safety_limits": LaunchConfiguration("safety_limits"),
            "safety_pos_margin": LaunchConfiguration("safety_pos_margin"),
            "safety_k_position": LaunchConfiguration("safety_k_position"),
            "description_file": LaunchConfiguration("planner_description_file"),
            "base_link": LaunchConfiguration("base_link"),
            "tip_link": LaunchConfiguration("tip_link"),
            "joint_state_topic": LaunchConfiguration("joint_state_topic"),
            "trajectory_topic": LaunchConfiguration("trajectory_topic"),
            "fk_topic": LaunchConfiguration("fk_topic"),
            "planning_steps": LaunchConfiguration("planning_steps"),
            "use_sim_time": LaunchConfiguration("use_sim_time"),
        }.items(),
    )

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
            DeclareLaunchArgument("use_sim_time", default_value="true"),
            DeclareLaunchArgument(
                "description_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("arm_description"),
                        "urdf",
                        "ur_gz_controlled.urdf.xacro",
                    ]
                ),
            ),
            DeclareLaunchArgument(
                "controllers_file",
                default_value=PathJoinSubstitution(
                    [
                        FindPackageShare("arm_ros2_control"),
                        "config",
                        "controllers.yaml",
                    ]
                ),
            ),
            DeclareLaunchArgument(
                "planner_description_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("arm_description"), "urdf", "ur.urdf.xacro"]
                ),
            ),
            DeclareLaunchArgument("base_link", default_value="base_link"),
            DeclareLaunchArgument("tip_link", default_value="tool0"),
            DeclareLaunchArgument("joint_state_topic", default_value="/joint_states"),
            DeclareLaunchArgument(
                "trajectory_topic",
                default_value="/arm_controller/joint_trajectory",
            ),
            DeclareLaunchArgument("fk_topic", default_value="/end_effector_pose"),
            DeclareLaunchArgument("planning_steps", default_value="100"),
            gazebo_control,
            TimerAction(period=7.0, actions=[kdl_planner]),
        ]
    )
