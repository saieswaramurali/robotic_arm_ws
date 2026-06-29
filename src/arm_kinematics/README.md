# arm_kinematics

KDL-based forward/inverse kinematics and simple trajectory planning for the UR5e arm.

## Dependencies

- `rclcpp`
- `arm_interfaces`
- `geometry_msgs`
- `sensor_msgs`
- `trajectory_msgs`
- `control_msgs`
- `rclcpp_action`
- `kdl_parser`, `urdf`, `orocos_kdl`

## Launch Files

### `trajectory_planner.launch.py`

Starts `trajectory_planner_node`.

```bash
ros2 launch arm_kinematics trajectory_planner.launch.py
```

Useful mobile-arm override:

```bash
ros2 launch arm_kinematics trajectory_planner.launch.py base_link:=arm_base_link tip_link:=arm_tool0 trajectory_topic:=/arm_controller/joint_trajectory
```

## Executables

- `trajectory_planner_node`
- `move_to_pose_cli`

## Interfaces

Subscribes:

- `/joint_states`

Publishes:

- `/end_effector_pose`
- `/arm_controller/joint_trajectory`

Services:

- `/compute_fk` (`arm_interfaces/srv/GetFk`)
- `/solve_ik` (`arm_interfaces/srv/SolveIk`)
- `/move_to_pose` (`arm_interfaces/srv/MoveToPose`)

## Examples

Move to a pose through the service:

```bash
ros2 service call /move_to_pose arm_interfaces/srv/MoveToPose "{target_pose: {header: {frame_id: base_link}, pose: {position: {x: 0.35, y: 0.0, z: 0.3}, orientation: {x: 0.0, y: 1.0, z: 0.0, w: 0.0}}}, duration: 3.0, seed: [], execute: true}"
```
