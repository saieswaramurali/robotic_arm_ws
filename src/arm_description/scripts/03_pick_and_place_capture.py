#!/usr/bin/env python3
"""Source wrapper for pick-and-place camera capture."""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from arm_description.demo.pick_and_place_capture import main


if __name__ == "__main__":
    main()
