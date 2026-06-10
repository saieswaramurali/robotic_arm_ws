"""Path helpers for source and installed package layouts."""

from __future__ import annotations

from pathlib import Path

try:
    from ament_index_python.packages import get_package_share_directory
except ImportError:  # pragma: no cover - ROS 2 is optional for direct source use.
    get_package_share_directory = None


PACKAGE_NAME = "arm_description"


def package_root() -> Path:
    return Path(__file__).resolve().parent.parent


def package_share() -> Path:
    if get_package_share_directory is not None:
        try:
            return Path(get_package_share_directory(PACKAGE_NAME))
        except Exception:
            pass
    return package_root()


def mjcf_dir() -> Path:
    return package_share() / "description" / "mjcf"


def scene_path(scene_file: str) -> Path:
    return mjcf_dir() / scene_file


def output_dir(name: str = "out") -> Path:
    return package_share() / name
