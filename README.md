# robotic_arm_ws

ROS 2 workspace for a UR5e robot description package.

The current workspace contains:

- `src/arm_description`: UR5e Xacro/URDF description, Webots Robotiq 3F gripper, simple wrist RGB-D camera block, RViz config, and launch files for RViz and Gazebo Sim.
- `src/arm_ros2_control`: ROS 2 controller configuration.
- `src/arm_bringup`: Gazebo Sim launch orchestration for the controlled arm.
- `src/arm_interfaces`: Custom service interfaces for FK, IK, and move-to-pose calls.
- `src/arm_kinematics`: KDL-based FK, IK, and trajectory planning service node.
- `src/arm_pick_place`: Predefined pick-and-place task logic for a known cylinder pose.

## What Works Now

- Build the `arm_description` package with `colcon`.
- View the UR5e model in RViz with `display.launch.py`.
- Spawn the same UR5e model into Gazebo Sim with `gazebo.launch.py`.
- Start Gazebo Sim ROS 2 control with position commands and position/velocity/effort state interfaces.
- Control the UR5e arm and Webots Robotiq 3F gripper through direct position controllers by default.
- Keep trajectory controllers available as inactive controllers for later switching.
- Read simulated wrist-camera RGB, depth image, camera info, and depth point cloud topics from Gazebo Sim.
- Call a KDL motion service to solve IK and publish a joint trajectory to move `tool0` in the `base_link` frame.

This workspace does not currently include a real hardware interface, MuJoCo scene, or pick-and-place demo.

## Requirements

The launch files expect a ROS 2 Humble environment with these packages available:

- `xacro`
- `robot_state_publisher`
- `joint_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `ros_gz_sim`
- `ros_gz_bridge`
- `ros2_control`
- `ros2_controllers`
- `gz_ros2_control`
- `forward_command_controller`
- `tf2_ros`
- `orocos_kdl`
- `kdl_parser`

## Build

```bash
cd ~/Desktop/ros_ws/robotic_arm_ws
colcon build --packages-select arm_description arm_ros2_control arm_interfaces arm_kinematics arm_pick_place arm_bringup
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

By default, Gazebo starts with `arm_description/worlds/arm_camera.sdf`, which includes the Gazebo Sensors system needed for camera topics. The robot is spawned from `/robot_description`.

## Gazebo ROS 2 Control

Launch Gazebo Sim with ROS 2 control:

```bash
ros2 launch arm_bringup gazebo_control.launch.py
```

This spawns the robot in Gazebo Sim, loads `gz_ros2_control`, and starts `joint_state_broadcaster`, `arm_position_controller`, and `gripper_position_controller`.

The trajectory controllers are still loaded, but inactive by default:

```bash
ros2 control list_controllers
```

Expected controller state:

```text
joint_state_broadcaster          active
arm_position_controller          active
gripper_position_controller      active
arm_controller                   inactive
gripper_controller               inactive
```

Move the arm with direct joint-position commands:

```bash
ros2 topic pub /arm_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.3, -1.1, 0.8, -1.4, 0.4, 0.0]}"
```

Observe state:

```bash
ros2 topic echo /joint_states
ros2 control list_hardware_interfaces
```

Gripper command joint order:

```text
[robotiq_palm_finger_1_joint, robotiq_finger_1_joint_1, robotiq_finger_1_joint_2, robotiq_finger_1_joint_3,
 robotiq_palm_finger_2_joint, robotiq_finger_2_joint_1, robotiq_finger_2_joint_2, robotiq_finger_2_joint_3,
 robotiq_finger_middle_joint_1, robotiq_finger_middle_joint_2, robotiq_finger_middle_joint_3]
```

Closed-ish gripper position:

```bash
ros2 topic pub /gripper_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.1, 0.8, 0.8, -0.8, -0.1, 0.8, 0.8, -0.8, 0.8, 0.8, -0.8]}"
```

Open-ish gripper position:

```bash
ros2 topic pub /gripper_position_controller/commands std_msgs/msg/Float64MultiArray \
  "{data: [0.0, 0.05, 0.05, -0.05, 0.0, 0.05, 0.05, -0.05, 0.05, 0.05, -0.05]}"
```

Switch to trajectory controllers when needed:

```bash
ros2 control switch_controllers \
  --deactivate arm_position_controller gripper_position_controller \
  --activate arm_controller gripper_controller
```

Switch back to direct position controllers:

```bash
ros2 control switch_controllers \
  --deactivate arm_controller gripper_controller \
  --activate arm_position_controller gripper_position_controller
```

## KDL Motion Pipeline

Start Gazebo ROS 2 control with the trajectory controller and KDL planner:

```bash
ros2 launch arm_bringup kinematics_control.launch.py
```

This launch starts Gazebo, activates:

```text
joint_state_broadcaster
arm_controller
gripper_controller
```

and leaves the direct position controllers inactive. The KDL node subscribes to `/joint_states`, publishes FK on `/end_effector_pose`, and publishes planned trajectories to `/arm_controller/joint_trajectory`.

Move the end effector, where the pose is expressed in `base_link`:

```bash
ros2 service call /move_to_pose arm_interfaces/srv/MoveToPose \
  "{target_pose: {header: {frame_id: 'base_link'}, pose: {position: {x: 0.35, y: 0.10, z: 0.45}, orientation: {x: 0.0, y: 0.0, z: 0.0, w: 1.0}}}, duration: 4.0, seed: [], execute: true}"
```

Useful services:

```text
/compute_fk
/solve_ik
/move_to_pose
```

## Predefined Cylinder Pick And Place

Launch Gazebo, the KDL motion pipeline, a cylinder object, and the fixed pick-place task:

```bash
ros2 launch arm_bringup pick_place_cylinder.launch.py
```

The cylinder starts at:

```text
x=0.38 y=0.18 z=0.06
```

The demo keeps a downward tool orientation, descends closer to the cylinder, closes the gripper, lifts, moves slightly to the robot's right side, descends near the table, opens the gripper, and retreats. To spawn the object without running the task:

```bash
ros2 launch arm_bringup pick_place_cylinder.launch.py run_demo:=false
```

View the simulated wrist camera:

```bash
rqt_image_view /wrist_camera/color/image
```

Camera topics:

```bash
ros2 topic list | grep wrist_camera
```

Useful camera topics:

```text
/wrist_camera/color/image
/wrist_camera/color/camera_info
/wrist_camera/depth/image
/wrist_camera/depth/camera_info
/wrist_camera/depth/points
```

In RViz, use the `Image` display for `/wrist_camera/color/image` and `PointCloud2` for `/wrist_camera/depth/points`.

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
- `gz_args:="-r /path/to/world.sdf"`
- `bridge_camera:=true`
- `launch_rviz:=true`
- `use_sim_time:=true`

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
├── worlds/
│   └── arm_camera.sdf
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

`arm_description/gazebo.launch.py` spawns the visual model, starts RViz by default, and bridges the wrist camera topics.

Use `arm_bringup/gazebo_control.launch.py` when you want controllers and joint state feedback from Gazebo. It starts direct position controllers by default.

## Credits And Sources

This workspace vendors or adapts description assets from these upstream projects:

| Asset | Upstream source | License | How it is used |
| --- | --- | --- | --- |
| UR5e robot description, config, and meshes | https://github.com/UniversalRobots/Universal_Robots_ROS2_Description and https://github.com/UniversalRobots/Universal_Robots_ROS2_Driver | BSD-3-Clause style ROS-Industrial/Universal Robots licensing upstream | Base UR5e model, meshes, joint limits, physical parameters, and Xacro structure. |
| Webots Robotiq 3F gripper | https://github.com/cyberbotics/webots_ros2 | Apache-2.0 | Robotiq 3F palm/finger meshes, joint layout, and UR5e gripper reference URDF style. |
| Intel RealSense D435i reference files | https://github.com/realsenseai/realsense-ros | Apache-2.0 | Retained reference Xacros and meshes. The active wrist camera is now a simple local RGB-D camera block with Gazebo sensors. |
| ROS 2 control and Gazebo integration patterns | ROS 2 `ros2_control`, `ros2_controllers`, `gz_ros2_control`, and `ros_gz` packages | Upstream ROS package licenses | Controller manager, direct position controllers, trajectory controllers, joint state broadcaster, and Gazebo Sim hardware plugin usage. |

Vendored license files are kept with the copied assets under `src/arm_description/meshes/vendor`. See `doc/assets.md` for the exact paths and notes.
