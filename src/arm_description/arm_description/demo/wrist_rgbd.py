"""Capture an RGB-D frame from the wrist camera."""

from __future__ import annotations

import numpy as np
import mujoco
from PIL import Image

from ..paths import output_dir
from ..scene_loader import ensure_output_dir, load_model, reset_keyframe


WIDTH = 640
HEIGHT = 480
CAMERA = "wrist_rgbd"


def main() -> None:
    out_dir = ensure_output_dir(output_dir())
    _, model, data = load_model("scene.xml")

    cam_id = mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, CAMERA)
    assert cam_id != -1, f"camera '{CAMERA}' not found in model"

    reset_keyframe(model, data, "home")
    renderer = mujoco.Renderer(model, height=HEIGHT, width=WIDTH)

    renderer.update_scene(data, camera=CAMERA)
    rgb = renderer.render()
    Image.fromarray(rgb).save(out_dir / "wrist_rgb.png")

    renderer.enable_depth_rendering()
    renderer.update_scene(data, camera=CAMERA)
    depth = renderer.render()
    renderer.disable_depth_rendering()

    np.save(out_dir / "wrist_depth.npy", depth)

    near, far = 0.1, 1.5
    d = np.clip(depth, near, far)
    vis = (255 * (1.0 - (d - near) / (far - near))).astype(np.uint8)
    Image.fromarray(vis).save(out_dir / "wrist_depth.png")

    finite = depth[np.isfinite(depth)]
    print(f"camera '{CAMERA}' id={cam_id}, fovy={model.cam_fovy[cam_id]:.1f} deg")
    print(f"rgb   shape={rgb.shape} dtype={rgb.dtype}")
    print(f"depth shape={depth.shape} dtype={depth.dtype} "
          f"min={finite.min():.3f} m  max={finite.max():.3f} m  "
          f"mean={finite.mean():.3f} m")
    print(f"wrote PNG/NPY to {out_dir}")
