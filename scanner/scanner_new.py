#!/usr/bin/env python3
# /// script
# dependencies = [
#   "kubernetes",
#   "pydantic",
#   "jinja2",
#   "requests",
# ]
# ///
"""
LiDAR Archive Scanner and Job Enqueuer - Entry Point

This script provides a clean entry point to the modular scanner package.
"""

import sys
from pathlib import Path

# Add the scanner package to the Python path
scanner_package_path = Path(__file__).parent / "scanner"
sys.path.insert(0, str(scanner_package_path))

try:
    # Import dependencies
    from kubernetes import client, config
    import jinja2
    import requests
    import yaml
except ImportError:
    print(
        "Error: required modules not found. Run this script with 'uv run' to auto-install dependencies."
    )
    sys.exit(1)

if __name__ == "__main__":
    # Import and run the main CLI
    from scanner.cli import main

    main()
