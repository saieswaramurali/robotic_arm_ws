from glob import glob
import os

from setuptools import find_packages, setup


package_name = "arm_description"
share_dir = os.path.join("share", package_name)


def package_files(directory):
    paths = []
    for root, _, filenames in os.walk(directory):
        if filenames:
            paths.append((os.path.join(share_dir, root), [os.path.join(root, f) for f in filenames]))
    return paths


setup(
    name=package_name,
    version="0.1.0",
    packages=find_packages(),
    data_files=[
        ("share/ament_index/resource_index/packages", [os.path.join("resource", package_name)]),
        (share_dir, ["package.xml", "README.md"]),
        (os.path.join(share_dir, "launch"), glob("launch/*.launch.py")),
        (os.path.join(share_dir, "scripts"), glob("scripts/*.py")),
    ] + package_files("description") + package_files("config"),
    install_requires=["setuptools"],
    zip_safe=False,
    maintainer="sai",
    maintainer_email="sai@example.com",
    description="UR5e MuJoCo assets, demo entrypoints, and launch files.",
    license="BSD-3-Clause",
    tests_require=["pytest"],
    entry_points={
        "console_scripts": [
            "00_display_scene = arm_description.demo.display_scene:main",
            "01_wrist_rgbd = arm_description.demo.wrist_rgbd:main",
            "02_pick_and_place_env = arm_description.demo.pick_and_place_env:main",
            "03_pick_and_place_capture = arm_description.demo.pick_and_place_capture:main",
        ],
    },
)
