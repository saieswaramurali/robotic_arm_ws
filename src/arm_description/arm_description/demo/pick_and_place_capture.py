"""Capture RGB-D outputs from the pick-and-place scenes."""

from __future__ import annotations

import argparse

import numpy as np
import mujoco
from PIL import Image

from ..paths import output_dir
from ..scene_loader import ensure_output_dir, load_model


WIDTH = 640
HEIGHT = 480
CAMERAS = {"scene_rgbd": "pp_scene", "wrist_rgbd": "pp_wrist"}
SETTLE_STEPS = 200
DEPTH_NEAR = 0.1
DEPTH_FAR = 2.0


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scene",
        default="pick_and_place.xml",
        choices=["pick_and_place.xml", "pick_and_place_tables.xml"],
        help="Pick-and-place scene file to load.",
    )
    parser.add_argument(
        "--viewer",
        action="store_true",
        help="Open the MuJoCo viewer after writing captures.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    out_dir = ensure_output_dir(output_dir())
    _, model, data = load_model(args.scene)

    mujoco.mj_resetDataKeyframe(model, data, model.key("start").id)
    for _ in range(SETTLE_STEPS):
        mujoco.mj_step(model, data)

    renderer = mujoco.Renderer(model, height=HEIGHT, width=WIDTH)

    for cam, prefix in CAMERAS.items():
        assert mujoco.mj_name2id(model, mujoco.mjtObj.mjOBJ_CAMERA, cam) != -1, \
            f"camera '{cam}' not found"

        renderer.update_scene(data, camera=cam)
        rgb = renderer.render()
        Image.fromarray(rgb).save(out_dir / f"{prefix}_rgb.png")

        renderer.enable_depth_rendering()
        renderer.update_scene(data, camera=cam)
        depth = renderer.render()
        renderer.disable_depth_rendering()

        d = np.clip(depth, DEPTH_NEAR, DEPTH_FAR)
        vis = (255 * (1.0 - (d - DEPTH_NEAR) / (DEPTH_FAR - DEPTH_NEAR))).astype(np.uint8)
        Image.fromarray(vis).save(out_dir / f"{prefix}_depth.png")

        finite = depth[np.isfinite(depth)]
        print(f"{cam:11s} rgb={rgb.shape} depth[min={finite.min():.3f} "
              f"max={finite.max():.3f} mean={finite.mean():.3f}] m")

    print(f"wrote PNGs to {out_dir}")

    if args.viewer:
        import mujoco.viewer
        print("opening viewer (close the window to exit)...")
        mujoco.viewer.launch(model, data)
