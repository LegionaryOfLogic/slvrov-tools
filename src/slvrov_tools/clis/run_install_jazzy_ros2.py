#!/usr/bin/env python3
# Caleb Hofschneider SLVROV 1/2025

import argparse
from ..misc_tools import safe_run

"https://github.com/LegionaryOfLogic/slvrov-tools/"

def main() -> None:
    
    parser = argparse.ArgumentParser(description="A script to download ROS2 Ubuntu images for ROV")

    parser.add_argument("name", type=str, choices=[], help="")



if __name__ == "__main__":
    main()
