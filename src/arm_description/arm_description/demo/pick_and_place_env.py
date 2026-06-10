"""Inspect a pick-and-place scene and open the viewer."""

from __future__ import annotations

import argparse

import mujoco
import mujoco.viewer

from ..scene_loader import load_model, reset_keyframe


def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--scene",
        default="pick_and_place_tables.xml",
        choices=["pick_and_place.xml", "pick_and_place_tables.xml"],
        help="Pick-and-place scene file to load.",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    _, model, data = load_model(args.scene)

    print(f"nq (generalized positions): {model.nq}")
    print(f"nu (actuators / control inputs): {model.nu}")
    print(f"ncam (cameras): {model.ncam}")

    print("\nCameras:")
    for i in range(model.ncam):
        print(f"  [{i}] {model.camera(i).name}")

    print("\nObjects (free bodies):")
    for i in range(model.njnt):
        if model.joint(i).type == mujoco.mjtJoint.mjJNT_FREE:
            body_id = model.joint(i).bodyid[0]
            print(f"  {model.body(body_id).name}")

    reset_keyframe(model, data, "start")

    print("\nReset to 'start' keyframe. Object positions:")
    for i in range(model.njnt):
        if model.joint(i).type == mujoco.mjtJoint.mjJNT_FREE:
            name = model.body(model.joint(i).bodyid[0]).name
            print(f"  {name:16s} {data.body(name).xpos.round(3)}")

    mujoco.viewer.launch(model, data)
