"""Open the base UR5e scene in the MuJoCo viewer."""

from __future__ import annotations

import mujoco
import mujoco.viewer

from ..scene_loader import load_model, reset_keyframe


def main() -> None:
    _, model, data = load_model("scene.xml")

    print(f"nq (generalized positions): {model.nq}")
    print(f"nv (generalized velocities): {model.nv}")
    print(f"nu (actuators / control inputs): {model.nu}")
    print(f"timestep: {model.opt.timestep} s")

    print("\nJoints:")
    for i in range(model.njnt):
        print(f"  [{i}] {model.joint(i).name}")

    print("\nActuators:")
    for i in range(model.nu):
        print(f"  [{i}] {model.actuator(i).name}")

    reset_keyframe(model, data, "home")

    print("\nEnd-effector ('attachment_site') position at home:",
          data.site("attachment_site").xpos)

    mujoco.viewer.launch(model, data)
