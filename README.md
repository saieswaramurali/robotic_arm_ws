# robotic_arm_ws

ROS 2 workspace for a UR5e robot description package.

The current workspace contains one active package:

- `src/arm_description`: UR5e Xacro/URDF description, meshes, RViz config, and launch files for RViz and Gazebo Sim.

## What Works Now

- Build the `arm_description` package with `colcon`.
- View the UR5e model in RViz with `display.launch.py`.
- Spawn the same UR5e model into Gazebo Sim with `gazebo.launch.py`.

This workspace is currently a robot description and visualization setup. It does not currently include a working Gazebo controller stack, gripper control, MuJoCo scene, or pick-and-place demo.

## Requirements

The launch files expect a ROS 2 Humble environment with these packages available:

- `xacro`
- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`
- `ros_gz_sim`

## Build

```bash
cd ~/Desktop/ros_ws/robotic_arm_ws
colcon build --packages-select arm_description
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
    ├── ur.urdf.xacro
    ├── ur_macro.xacro
    └── ur_mocked.urdf.xacro
```

## Notes

`gazebo.launch.py` uses `force_abs_paths:=true` when processing the Xacro so Gazebo can resolve mesh files from the installed package path.

For joint control in Gazebo, the next step is adding a Gazebo-compatible `ros2_control` hardware plugin and controller launch/configuration. The current Gazebo launch only spawns the model.
