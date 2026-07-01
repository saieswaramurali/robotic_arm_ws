from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import Command, FindExecutable, LaunchConfiguration, PathJoinSubstitution
from launch_ros.actions import Node
from launch_ros.parameter_descriptions import ParameterValue
from launch_ros.substitutions import FindPackageShare


def generate_launch_description():
    ur_type = LaunchConfiguration("ur_type")
    name = LaunchConfiguration("name")
    tf_prefix = LaunchConfiguration("tf_prefix")
    safety_limits = LaunchConfiguration("safety_limits")
    safety_pos_margin = LaunchConfiguration("safety_pos_margin")
    safety_k_position = LaunchConfiguration("safety_k_position")
    description_file = LaunchConfiguration("description_file")

    robot_description = ParameterValue(
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
                " ",
                "include_gz_camera_sensors:=false",
            ]
        ),
        value_type=str,
    )

    planner = Node(
        package="arm_kinematics",
        executable="trajectory_planner_node",
        name="trajectory_planner_node",
        output="screen",
        parameters=[
            {
                "robot_description": robot_description,
                "base_link": LaunchConfiguration("base_link"),
                "tip_link": LaunchConfiguration("tip_link"),
                "joint_state_topic": LaunchConfiguration("joint_state_topic"),
                "trajectory_topic": LaunchConfiguration("trajectory_topic"),
                "fk_topic": LaunchConfiguration("fk_topic"),
                "planning_steps": ParameterValue(
                    LaunchConfiguration("planning_steps"), value_type=int
                ),
                "use_sim_time": ParameterValue(
                    LaunchConfiguration("use_sim_time"), value_type=bool
                ),
            }
        ],
    )

    return LaunchDescription(
        [
            DeclareLaunchArgument("ur_type", default_value="ur5e"),
            DeclareLaunchArgument("name", default_value="ur"),
            DeclareLaunchArgument("tf_prefix", default_value=""),
            DeclareLaunchArgument("safety_limits", default_value="true"),
            DeclareLaunchArgument("safety_pos_margin", default_value="0.15"),
            DeclareLaunchArgument("safety_k_position", default_value="20"),
            DeclareLaunchArgument("base_link", default_value="base_link"),
            DeclareLaunchArgument("tip_link", default_value="tool0"),
            DeclareLaunchArgument("joint_state_topic", default_value="/joint_states"),
            DeclareLaunchArgument(
                "trajectory_topic",
                default_value="/arm_controller/joint_trajectory",
            ),
            DeclareLaunchArgument("fk_topic", default_value="/end_effector_pose"),
            DeclareLaunchArgument("planning_steps", default_value="100"),
            DeclareLaunchArgument("use_sim_time", default_value="false"),
            DeclareLaunchArgument(
                "description_file",
                default_value=PathJoinSubstitution(
                    [FindPackageShare("arm_description"), "urdf", "ur.urdf.xacro"]
                ),
            ),
            planner,
        ]
    )
