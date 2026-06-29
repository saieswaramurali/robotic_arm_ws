# arm_bringup

Arm-only launch orchestration for Gazebo Sim, ros2_control, kinematics, and pick-place demos.

## Dependencies

- `arm_description`
- `arm_ros2_control`
- `arm_kinematics`
- `arm_pick_place`
- `controller_manager`
- `gz_ros2_control`
- `ros_gz_sim`, `ros_gz_bridge`
- `robot_state_publisher`

## Launch Files

### `gazebo_control.launch.py`

Use for arm-only Gazebo Sim with ros2_control controllers.

```bash
ros2 launch arm_bringup gazebo_control.launch.py
```

Use trajectory controllers:

```bash
ros2 launch arm_bringup gazebo_control.launch.py use_trajectory_controllers:=true
```

### `kinematics_control.launch.py`

Use when running the arm with the KDL trajectory planner.

```bash
ros2 launch arm_bringup kinematics_control.launch.py
```

### `pick_place_cylinder.launch.py`

Use for the predefined pick-place demo.

```bash
ros2 launch arm_bringup pick_place_cylinder.launch.py
```

## Main Interfaces

Publishes:

- `/joint_states`
- `/tf`
- `/tf_static`
- optional wrist camera topics

Subscribes:

- `/arm_position_controller/commands`
- `/gripper_position_controller/commands`
- `/arm_controller/joint_trajectory`
- `/gripper_controller/joint_trajectory`

Services:

- `/compute_fk`
- `/solve_ik`
- `/move_to_pose`

## Example

```bash
ros2 topic pub --once /arm_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]}"
```
