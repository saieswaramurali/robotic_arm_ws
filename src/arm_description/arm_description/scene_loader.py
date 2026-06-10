"""Reusable MuJoCo scene helpers."""

from __future__ import annotations

from pathlib import Path

import mujoco

from .paths import scene_path


def load_model(scene_file: str):
    scene = scene_path(scene_file)
    model = mujoco.MjModel.from_xml_path(str(scene))
    data = mujoco.MjData(model)
    return scene, model, data


def reset_keyframe(model, data, key_name: str) -> None:
    mujoco.mj_resetDataKeyframe(model, data, model.key(key_name).id)
    mujoco.mj_forward(model, data)


def ensure_output_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
