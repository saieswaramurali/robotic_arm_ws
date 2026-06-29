# mobile_arm_bringup

Simulation bringup for the mobile UR5e manipulator. This package launches Gazebo Sim, spawns the combined robot, starts arm ros2_control, bridges Gazebo topics, and includes the self-contained testbed world.

## Dependencies

- `mobile_arm_description`
- `arm_description`
- `arm_ros2_control`
- `controller_manager`
- `gz_ros2_control`
- `ros_gz_sim`, `ros_gz_bridge`
- `robot_state_publisher`
- `rviz2`

## Launch Files

### `gazebo_control.launch.py`

Use for the mobile arm in the default empty world.

```bash
ros2 launch mobile_arm_bringup gazebo_control.launch.py
```

### `testbed_gazebo_control.launch.py`

Use for the mobile arm in the included testbed world.

```bash
ros2 launch mobile_arm_bringup testbed_gazebo_control.launch.py
```

Spawn offset:

```bash
ros2 launch mobile_arm_bringup testbed_gazebo_control.launch.py x:=1.0 y:=2.0 yaw:=1.57
```

## Interfaces

Subscribes:

- `/cmd_vel`
- `/arm_position_controller/commands`
- `/gripper_position_controller/commands`
- `/arm_controller/joint_trajectory`
- `/gripper_controller/joint_trajectory`

Publishes:

- `/odom`
- `/scan`
- `/joint_states`
- `/tf`
- `/tf_static`
- `/wrist_camera/color/image`
- `/wrist_camera/depth/points`

Actions:

- `/arm_controller/follow_joint_trajectory`
- `/gripper_controller/follow_joint_trajectory`

## Examples

Drive:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.8}, angular: {z: 0.0}}"
```

Rotate:

```bash
ros2 topic pub --once /cmd_vel geometry_msgs/msg/Twist "{linear: {x: 0.0}, angular: {z: 1.5}}"
```

Move arm:

```bash
ros2 topic pub --once /arm_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]}"
```

Check scan:

```bash
ros2 topic hz /scan
```
