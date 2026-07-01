# arm_interfaces

Custom service interfaces used by the arm kinematics and pick-place packages.

## Dependencies

- `geometry_msgs`
- `trajectory_msgs`
- `rosidl_default_generators`
- `rosidl_default_runtime`

## Services

### `GetFk.srv`

Request:

- `float64[] joints`

Response:

- `bool success`
- `string message`
- `geometry_msgs/PoseStamped pose`

### `SolveIk.srv`

Request:

- `geometry_msgs/PoseStamped target_pose`
- `float64[] seed`

Response:

- `bool success`
- `string message`
- `float64[] joints`
- `geometry_msgs/PoseStamped solved_pose`

### `MoveToPose.srv`

Request:

- `geometry_msgs/PoseStamped target_pose`
- `float64 duration`
- `float64[] seed`
- `bool execute`

Response:

- `bool success`
- `string message`
- `float64[] joints`
- `trajectory_msgs/JointTrajectory trajectory`

## Example

Show generated interface:

```bash
ros2 interface show arm_interfaces/srv/MoveToPose
```
