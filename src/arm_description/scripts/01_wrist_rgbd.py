#!/usr/bin/env python3
"""Source wrapper for wrist RGB-D capture."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arm_description.demo.wrist_rgbd import main


if __name__ == "__main__":
    main()
