#!/usr/bin/env python3
"""
Build script for the PR-Agent UI.

This script builds the React frontend for the PR-Agent UI and ensures
all static assets are properly placed in the static directory.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

def main():
    """Build the PR-Agent UI."""
    # Get the directory of this script
    script_dir = Path(__file__).parent.absolute()
    ui_dir = script_dir / "ui"
    dist_dir = ui_dir / "dist"
    
    print(f"Building PR-Agent UI in {ui_dir}")
    
    # Check if Node.js is installed
    try:
        node_version = subprocess.check_output(["node", "--version"], text=True).strip()
        npm_version = subprocess.check_output(["npm", "--version"], text=True).strip()
        print(f"Node.js version: {node_version}")
        print(f"npm version: {npm_version}")
    except (subprocess.SubprocessError, FileNotFoundError):
        print("Error: Node.js and npm are required to build the UI.")
        print("Please install Node.js (v16 or later) and npm (v7 or later).")
        sys.exit(1)
    
    # Change to the UI directory
    os.chdir(ui_dir)
    
    # Install dependencies
    print("Installing dependencies...")
    try:
        subprocess.run(["npm", "install"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error installing dependencies: {e}")
        sys.exit(1)
    
    # Build the UI
    print("Building the UI...")
    try:
        subprocess.run(["npm", "run", "build"], check=True)
    except subprocess.SubprocessError as e:
        print(f"Error building the UI: {e}")
        sys.exit(1)
    
    # Ensure the dist directory exists
    dist_dir.mkdir(exist_ok=True)
    
    # Ensure the assets directory exists
    assets_dir = dist_dir / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Create a .gitkeep file in the assets directory to ensure it's tracked by git
    (assets_dir / ".gitkeep").touch()
    
    # Copy favicon if it doesn't exist in the output
    favicon_path = dist_dir / "favicon.ico"
    if not favicon_path.exists():
        src_favicon = ui_dir / "src" / "favicon.ico"
        if src_favicon.exists():
            print("Adding favicon.ico...")
            shutil.copy(src_favicon, favicon_path)
        else:
            print("Warning: No favicon found to copy.")
    
    print("Build completed successfully!")
    return 0

if __name__ == "__main__":
    sys.exit(main())
