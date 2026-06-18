# robotic_arm_ws

ROS 2 workspace for a UR5e robot description package.

The current workspace contains:

- `src/arm_description`: UR5e Xacro/URDF description, meshes, RViz config, and launch files for RViz and Gazebo Sim.
- `src/arm_ros2_control`: ROS 2 controller configuration.
- `src/arm_bringup`: Gazebo Sim launch orchestration for the controlled arm.

## What Works Now

- Build the `arm_description` package with `colcon`.
- View the UR5e model in RViz with `display.launch.py`.
- Spawn the same UR5e model into Gazebo Sim with `gazebo.launch.py`.
- Start Gazebo Sim ROS 2 control with position commands and position/velocity/effort state interfaces.

This workspace does not currently include a real hardware interface, gripper control, MuJoCo scene, or pick-and-place demo.

## Requirements

The launch files expect a ROS 2 Humble environment with these packages available:

- `xacro`
- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `ros_gz_sim`
- `ros2_control`
- `ros2_controllers`

## Build

```bash
cd ~/Desktop/ros_ws/robotic_arm_ws
colcon build --packages-select arm_description arm_ros2_control arm_bringup
source install/setup.bash
```

## RViz

Launch the robot in RViz with the joint state publisher GUI:

```bash
ros2 launch arm_description display.launch.py
```

The launch file publishes `robot_description`, starts `robot_state_publisher`, opens `joint_state_publisher_gui`, and loads `rviz/view_robot.rviz`.

## Gazebo Sim

Launch Gazebo Sim and spawn the robot from the same Xacro description:

```bash
ros2 launch arm_description gazebo.launch.py
```

Optional spawn pose:

```bash
ros2 launch arm_description gazebo.launch.py x:=0.5 y:=0.0 z:=0.0 yaw:=1.57
```

By default, Gazebo starts with `empty.sdf` and the robot is spawned from `/robot_description`.

## Gazebo ROS 2 Control

Launch Gazebo Sim with ROS 2 control:

```bash
ros2 launch arm_bringup gazebo_control.launch.py
```

This spawns the robot in Gazebo Sim, loads `gz_ros2_control`, and starts `joint_state_broadcaster` plus `arm_controller`.

Move the arm:

```bash
ros2 action send_goal /arm_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [shoulder_pan_joint, shoulder_lift_joint, elbow_joint, wrist_1_joint, wrist_2_joint, wrist_3_joint], points: [{positions: [0.5, -1.2, 0.8, -1.4, 0.4, 0.0], time_from_start: {sec: 3}}]}}"
```

Observe state:

```bash
ros2 topic echo /joint_states
ros2 control list_hardware_interfaces
```

## Useful Launch Arguments

Both RViz and Gazebo launches support:

- `ur_type:=ur5e`
- `tf_prefix:=`
- `safety_limits:=true`
- `safety_pos_margin:=0.15`
- `safety_k_position:=20`
- `description_file:=/path/to/file.xacro`

`gazebo.launch.py` also supports:

- `name:=ur`
- `x:=0.0`
- `y:=0.0`
- `z:=0.0`
- `roll:=0.0`
- `pitch:=0.0`
- `yaw:=0.0`
- `gz_args:="-r empty.sdf"`

## Package Layout

```text
src/arm_description/
├── CMakeLists.txt
├── package.xml
├── config/
│   ├── initial_positions.yaml
│   └── ur5e/
├── launch/
│   ├── display.launch.py
│   └── gazebo.launch.py
├── meshes/
├── rviz/
│   └── view_robot.rviz
└── urdf/
    ├── ros2_control_mock_hardware.xacro
    ├── ros2_control_gz.xacro
    ├── ur.urdf.xacro
    ├── ur_gz_controlled.urdf.xacro
    ├── ur_macro.xacro
    └── ur_mocked.urdf.xacro

src/arm_ros2_control/
├── CMakeLists.txt
├── package.xml
└── config/
    └── controllers.yaml

src/arm_bringup/
├── CMakeLists.txt
├── package.xml
└── launch/
    └── gazebo_control.launch.py
```

## Notes

`gazebo.launch.py` uses `force_abs_paths:=true` when processing the Xacro so Gazebo can resolve mesh files from the installed package path.

`arm_description/gazebo.launch.py` only spawns the visual model. Use `arm_bringup/gazebo_control.launch.py` when you want controllers and joint state feedback from Gazebo.
