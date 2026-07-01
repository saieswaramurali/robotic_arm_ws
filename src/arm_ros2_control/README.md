# arm_ros2_control

Controller configuration for the UR5e arm and Robotiq gripper.

## Dependencies

- `controller_manager`
- `joint_state_broadcaster`
- `joint_trajectory_controller`
- `forward_command_controller`
- `ros2_controllers`

## Main File

### `config/controllers.yaml`

Defines:

- `joint_state_broadcaster`
- `arm_controller`
- `gripper_controller`
- `arm_position_controller`
- `gripper_position_controller`

## Interfaces

Typical controller interfaces after bringup:

- Publishes:
  - `/joint_states`
  - `/dynamic_joint_states`
  - `/arm_controller/state`
  - `/gripper_controller/state`
- Subscribes:
  - `/arm_position_controller/commands`
  - `/gripper_position_controller/commands`
  - `/arm_controller/joint_trajectory`
  - `/gripper_controller/joint_trajectory`
- Actions:
  - `/arm_controller/follow_joint_trajectory`
  - `/gripper_controller/follow_joint_trajectory`

## Example Commands

Move arm with the forward position controller:

```bash
ros2 topic pub --once /arm_position_controller/commands std_msgs/msg/Float64MultiArray "{data: [0.0, -1.57, 0.0, -1.57, 0.0, 0.0]}"
```

List controllers:

```bash
ros2 control list_controllers
```
