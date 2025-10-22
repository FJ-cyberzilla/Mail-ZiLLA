#!/usr/bin/env python3
"""
Animated Farewell Display
Displays the farewell message with animations
"""

import os
import time
from pathlib import Path


def animated_display(file_path):
    """Display farewell file with animation"""
    if not os.path.exists(file_path):
        print("Farewell file not found!")
        return

    with open(file_path, "r") as f:
        content = f.read()

    # Clear screen
    os.system("cls" if os.name == "nt" else "clear")

    # Typewriter effect
    for char in content:
        print(char, end="", flush=True)
        time.sleep(0.01)

    print("\n\n")


if __name__ == "__main__":
    farewell_file = Path.home() / "cyberzilla_farewell.txt"
    animated_display(farewell_file)
