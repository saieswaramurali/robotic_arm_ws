# mobile_arm_description

Simulation description for the mobile manipulator: a four-wheel skid-steer-style base carrying the UR5e arm.

## Dependencies

- `arm_description`
- `arm_ros2_control`
- `xacro`
- `robot_state_publisher`
- `joint_state_publisher`
- `ros_gz_sim`, `ros_gz_bridge`
- `rviz2`

## Launch Files

### `display.launch.py`

RViz-only display of the combined mobile arm.

```bash
ros2 launch mobile_arm_description display.launch.py
```

### `gazebo.launch.py`

Simple Gazebo Sim spawn without the full ros2_control bringup.

```bash
ros2 launch mobile_arm_description gazebo.launch.py
```

## Main Interfaces

Publishes through launched nodes:

- `/robot_description`
- `/joint_states`
- `/tf`
- `/tf_static`

Gazebo model provides:

- `/cmd_vel` input through Gazebo DiffDrive
- `/odom`
- `/scan`

## Notes

Use this package for model files only. Use `mobile_arm_bringup` for the controlled simulation.
