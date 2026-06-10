# arm_description

This package is the first ROS 2 landing zone for the current `robotic_arm_ws`.
It packages the existing UR5e MuJoCo model, scene assets, numbered demo
entrypoints, and launch files without forcing the kinematics and control logic
into ROS too early.

## Purpose

This package is responsible for:

- shipping the MuJoCo MJCF assets inside a ROS 2 package
- exposing launch files such as `display.launch.py`
- keeping numbered demo entrypoints that mirror the current standalone examples
- giving the later ROS 2 port a stable package to build on

This package is not yet the final home for controllers, planners, or perception
nodes. Those should be split into follow-up packages later.

## Layout

```text
arm_description/
  launch/                   ROS 2 launch entrypoints
  scripts/                  numbered source wrappers for direct execution
  description/mjcf/         MuJoCo scene and mesh assets
  config/rviz/              placeholder RViz config location
  arm_description/  importable Python package
```

## Python Dependencies

This package uses standard Python wheels that are not managed by `package.xml`.
Keep ROS dependencies in `package.xml`, and install the Python runtime packages
with `pip`.

You now have both options:

- workspace-wide install from [`requirements.txt`](../../../requirements.txt)
- package-local install from [`requirements.txt`](requirements.txt)

From the workspace root:

```bash
python3 -m pip install -r requirements.txt
```

From this package directory:

```bash
python3 -m pip install -r requirements.txt
```

Required Python packages today are:

- `mujoco`
- `numpy`
- `pillow`

## ROS 2 Build

From `robotic_arm_ws/ros2_ws`:

```bash
colcon build --packages-select arm_description
source install/setup.bash
```

## Launch Files

- `display.launch.py`
  - loads the base UR5e scene and opens the viewer
- `view_scene.launch.py`
  - same as `display.launch.py`, kept as an explicit scene-view entrypoint
- `view_pick_and_place.launch.py`
  - loads the floor pick-and-place scene
- `view_pick_and_place_tables.launch.py`
  - loads the three-table pick-and-place cell
- `wrist_rgbd.launch.py`
  - captures the wrist RGB-D outputs without opening the pick-and-place scenes

Example usage:

```bash
ros2 launch arm_description display.launch.py
ros2 launch arm_description view_pick_and_place_tables.launch.py
ros2 launch arm_description wrist_rgbd.launch.py
```

If you are running headless, use MuJoCo's EGL backend:

```bash
MUJOCO_GL=egl ros2 launch arm_description wrist_rgbd.launch.py
```

## Numbered Demo Entry Points

These are provided both as ROS-installed executables and as source wrappers:

- `00_display_scene`
- `01_wrist_rgbd`
- `02_pick_and_place_env`
- `03_pick_and_place_capture`

Direct source execution examples:

```bash
python ros2_ws/src/arm_description/scripts/00_display_scene.py
python ros2_ws/src/arm_description/scripts/02_pick_and_place_env.py --scene pick_and_place_tables.xml
```

## Credits

The UR5e MuJoCo model in `description/mjcf/` comes from
[MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) by
Google DeepMind, released under the BSD-3-Clause License.

The Robotiq 2F-85 gripper model in `description/mjcf/2f85/` also comes from
[MuJoCo Menagerie](https://github.com/google-deepmind/mujoco_menagerie) by
Google DeepMind, released under the BSD-2-Clause License (see
`description/mjcf/2f85/LICENSE`). The original gripper is the
[Robotiq 85mm 2-Finger Adaptive Gripper](https://robotiq.com/products/2f85-140-adaptive-robot-gripper)
by [Robotiq](https://robotiq.com/). It is merged into the UR5e model at the
wrist attachment site in `description/mjcf/ur5e.xml`.
