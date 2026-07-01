# arm_description

UR5e arm description package. Contains Xacro/URDF, meshes, RViz config, Gazebo world/model assets, gripper mount, and wrist camera mount.

## Dependencies

- `xacro`
- `robot_state_publisher`
- `joint_state_publisher`, `joint_state_publisher_gui`
- `rviz2`
- `ros_gz_sim`, `ros_gz_bridge`
- `arm_ros2_control`

## Launch Files

### `display.launch.py`

Use for RViz-only model inspection with GUI joint sliders.

```bash
ros2 launch arm_description display.launch.py
```

### `gazebo.launch.py`

Use for spawning the arm-only model in Gazebo Sim without the full arm control bringup.

```bash
ros2 launch arm_description gazebo.launch.py
```

## Interfaces

Publishes through launched nodes:

- `/robot_description`
- `/joint_states`
- `/tf`
- `/tf_static`
- optional wrist camera bridge topics:
  - `/wrist_camera/color/image`
  - `/wrist_camera/depth/image`
  - `/wrist_camera/depth/points`

## Notes

Use this package only for description/display/simulation assets. Use `arm_bringup` when you need controllers.
