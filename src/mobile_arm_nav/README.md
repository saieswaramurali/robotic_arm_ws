# mobile_arm_nav

SLAM Toolbox and Nav2 configuration for the mobile arm.

## Dependencies

- `slam_toolbox`
- `nav2_map_server`
- `nav2_amcl`
- `nav2_controller`
- `nav2_planner`
- `nav2_bt_navigator`
- `nav2_lifecycle_manager`
- `nav2_costmap_2d`
- `rviz2`

## Launch Files

### `slam_mapping.launch.py`

Use while driving the robot to build a map.

```bash
ros2 launch mobile_arm_nav slam_mapping.launch.py
```

### `localization.launch.py`

Use SLAM Toolbox localization mode with a saved pose graph.

```bash
ros2 launch mobile_arm_nav localization.launch.py map:=testbed_map
```

### `navigation.launch.py`

Use Nav2 with map server and AMCL.

```bash
ros2 launch mobile_arm_nav navigation.launch.py
```

Use a custom map:

```bash
ros2 launch mobile_arm_nav navigation.launch.py map:=/absolute/path/to/map.yaml
```

## Interfaces

Subscribes:

- `/scan`
- `/odom`
- `/tf`
- `/tf_static`
- `/goal_pose`
- `/initialpose`

Publishes:

- `/map`
- `/cmd_vel`
- Nav2 costmap, plan, feedback, and lifecycle topics

Services:

- `/slam_toolbox/save_map`
- Nav2 lifecycle and costmap services

Actions:

- `/navigate_to_pose`
- `/navigate_through_poses`
- `/compute_path_to_pose`
- `/follow_path`

## Examples

Start testbed sim:

```bash
ros2 launch mobile_arm_bringup testbed_gazebo_control.launch.py
```

Start SLAM:

```bash
ros2 launch mobile_arm_nav slam_mapping.launch.py
```

Drive with teleop:

```bash
ros2 run teleop_twist_keyboard teleop_twist_keyboard
```

Save map:

```bash
ros2 run mobile_arm_nav save_map my_testbed_map
```

Start Nav2:

```bash
ros2 launch mobile_arm_nav navigation.launch.py
```
