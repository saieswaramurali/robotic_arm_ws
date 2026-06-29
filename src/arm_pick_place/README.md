# arm_pick_place

Predefined cylinder pick-place task logic for the arm.

## Dependencies

- `rclcpp`
- `arm_interfaces`
- `geometry_msgs`
- `trajectory_msgs`

## Executables

### `predefined_pick_place_node`

Runs a hard-coded pick-place sequence using the `/move_to_pose` service and gripper trajectory topic.

```bash
ros2 run arm_pick_place predefined_pick_place_node
```

## Interfaces

Clients:

- `/move_to_pose` (`arm_interfaces/srv/MoveToPose`)

Publishes:

- `/gripper_controller/joint_trajectory`

## Parameters

Common parameters:

- `object_x`, `object_y`
- `pick_z`, `approach_z`
- `place_x`, `place_y`, `place_z`
- `retreat_z`
- `move_duration`

## Example

```bash
ros2 run arm_pick_place predefined_pick_place_node --ros-args -p object_x:=0.38 -p object_y:=0.18 -p place_y:=-0.08
```
