# Quick Start

This workspace currently contains the `arm_description` ROS 2 package for a UR5e robot model.

Use this guide to build the package, view the robot in RViz, and spawn the same robot in Gazebo Sim.

## 1. Build

```bash
cd ~/Desktop/ros_ws/robotic_arm_ws
colcon build --packages-select arm_description
source install/setup.bash
```

## 2. View In RViz

```bash
ros2 launch arm_description display.launch.py
```

This starts:

- `robot_state_publisher`
- `joint_state_publisher_gui`
- `rviz2`

Move the sliders in `joint_state_publisher_gui` to inspect the robot joints in RViz.

## 3. Spawn In Gazebo Sim

```bash
ros2 launch arm_description gazebo.launch.py
```

This starts Gazebo Sim with `empty.sdf`, publishes the UR5e description, and spawns the robot from `/robot_description`.

To spawn the robot at a different pose:

```bash
ros2 launch arm_description gazebo.launch.py x:=0.5 y:=0.0 z:=0.0 yaw:=1.57
```

## 4. Useful Checks

Show launch arguments:

```bash
ros2 launch arm_description display.launch.py --show-args
ros2 launch arm_description gazebo.launch.py --show-args
```

Check that the Xacro can generate a URDF:

```bash
xacro install/arm_description/share/arm_description/urdf/ur.urdf.xacro \
  ur_type:=ur5e \
  name:=ur \
  safety_limits:=true \
  safety_pos_margin:=0.15 \
  safety_k_position:=20 \
  tf_prefix:= \
  force_abs_paths:=true
```

## Current Scope

What is available now:

- UR5e Xacro/URDF model
- UR5e meshes and config files
- RViz visualization launch
- Gazebo Sim spawn launch

What is not available yet:

- Gazebo joint control
- Controller manager launch for Gazebo
- Gripper model/control
- MuJoCo scene or pick-and-place demo

The next step for control is adding a Gazebo-compatible `ros2_control` setup and controller configuration.
