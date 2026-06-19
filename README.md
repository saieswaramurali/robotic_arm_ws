# robotic_arm_ws

ROS 2 workspace for a UR5e robot description package.

The current workspace contains:

- `src/arm_description`: UR5e Xacro/URDF description, Webots Robotiq 3F gripper, simple wrist RGB-D camera block, RViz config, and launch files for RViz and Gazebo Sim.
- `src/arm_ros2_control`: ROS 2 controller configuration.
- `src/arm_bringup`: Gazebo Sim launch orchestration for the controlled arm.

## What Works Now

- Build the `arm_description` package with `colcon`.
- View the UR5e model in RViz with `display.launch.py`.
- Spawn the same UR5e model into Gazebo Sim with `gazebo.launch.py`.
- Start Gazebo Sim ROS 2 control with position commands and position/velocity/effort state interfaces.
- Control the UR5e arm and Webots Robotiq 3F gripper through trajectory controllers.
- Read simulated wrist-camera RGB and depth images from Gazebo Sim.

This workspace does not currently include a real hardware interface, MuJoCo scene, or pick-and-place demo.

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

This spawns the robot in Gazebo Sim, loads `gz_ros2_control`, and starts `joint_state_broadcaster`, `arm_controller`, and `gripper_controller`.

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

View the simulated wrist camera:

```bash
rqt_image_view /wrist_camera/color/image
```

Camera topics:

```bash
ros2 topic list | grep wrist_camera
```

Close the Webots Robotiq 3F gripper:

```bash
ros2 action send_goal /gripper_controller/follow_joint_trajectory \
  control_msgs/action/FollowJointTrajectory \
  "{trajectory: {joint_names: [robotiq_palm_finger_1_joint, robotiq_finger_1_joint_1, robotiq_finger_1_joint_2, robotiq_finger_1_joint_3, robotiq_palm_finger_2_joint, robotiq_finger_2_joint_1, robotiq_finger_2_joint_2, robotiq_finger_2_joint_3, robotiq_finger_middle_joint_1, robotiq_finger_middle_joint_2, robotiq_finger_middle_joint_3], points: [{positions: [0.1, 0.8, 0.8, -0.8, -0.1, 0.8, 0.8, -0.8, 0.8, 0.8, -0.8], time_from_start: {sec: 2}}]}}"
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
│   ├── ur5e/
│   └── vendor/
│       ├── realsense/
│       └── webots_robotiq_3f/
├── rviz/
│   └── view_robot.rviz
└── urdf/
    ├── realsense_d435i_mount.xacro
    ├── robotiq_3f_mount.xacro
    ├── ros2_control_mock_hardware.xacro
    ├── ros2_control_gz.xacro
    ├── ur.urdf.xacro
    ├── ur_gz_controlled.urdf.xacro
    ├── ur_macro.xacro
    ├── ur_mocked.urdf.xacro
    └── vendor/
        ├── realsense/
        └── webots_robotiq_3f/

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

## Credits And Sources

This workspace vendors or adapts description assets from these upstream projects:

| Asset | Upstream source | License | How it is used |
| --- | --- | --- | --- |
| UR5e robot description, config, and meshes | https://github.com/UniversalRobots/Universal_Robots_ROS2_Description and https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver | BSD-3-Clause style ROS-Industrial/Universal Robots licensing upstream | Base UR5e model, meshes, joint limits, physical parameters, and Xacro structure. |
| Webots Robotiq 3F gripper | https://github.com/cyberbotics/webots_ros2 | Apache-2.0 | Robotiq 3F palm/finger meshes, joint layout, and UR5e gripper reference URDF style. |
| Intel RealSense D435i reference files | https://github.com/realsenseai/realsense-ros | Apache-2.0 | Retained reference Xacros and meshes. The active wrist camera is now a simple local RGB-D camera block with Gazebo sensors. |
| ROS 2 control and Gazebo integration patterns | ROS 2 `ros2_control`, `ros2_controllers`, `gz_ros2_control`, and `ros_gz` packages | Upstream ROS package licenses | Controller manager, trajectory controllers, joint state broadcaster, and Gazebo Sim hardware plugin usage. |

Vendored license files are kept with the copied assets under `src/arm_description/meshes/vendor`. See `doc/assets.md` for the exact paths and notes.
