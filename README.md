# robotic_arm_ws

Short ROS 2 workspace for a MuJoCo-based UR5e robotic arm setup.

## Includes

- `src/arm_description`: ROS 2 package with launch files, Python demos, and MuJoCo MJCF assets
- pick-and-place scenes
- wrist RGB-D capture demo
- RViz config placeholder in `src/arm_description/config/rviz/`

## Quick Start

```bash
python3 -m pip install -r src/arm_description/requirements.txt
colcon build --packages-select arm_description
source install/setup.bash
ros2 launch arm_description display.launch.py
```

Other useful launch files:

- `ros2 launch arm_description view_pick_and_place.launch.py`
- `ros2 launch arm_description view_pick_and_place_tables.launch.py`
- `ros2 launch arm_description wrist_rgbd.launch.py`

## Credits

- UR5e MuJoCo assets are derived from MuJoCo Menagerie by Google DeepMind.
- The bundled Robotiq 2F-85 gripper assets are also from MuJoCo Menagerie.
- The UR5e source model traces back to ROS-Industrial / Universal Robots descriptions.

See [src/arm_description/README.md](/home/sai/Desktop/ros_ws/robotic_arm_ws/src/arm_description/README.md) and the license files under `src/arm_description/description/mjcf/` for details.
