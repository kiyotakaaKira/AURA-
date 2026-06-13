"""
AURA Installation Script
Run: python setup.py
"""

import subprocess
import sys
import os
from pathlib import Path

def run(cmd, description=""):
    print(f"  {description}..." if description else f"  Running: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr}")
        return False
    return True

def main():
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except AttributeError:
        pass
    
    print("═" * 50)
    print("AURA — Installation")
    print("═" * 50)
    
    # Create directories
    dirs = [
        "data/gestures",
        "data/user_history",
        "data/models",
        "data/profiles",
        "assets/fonts",
        "assets/sounds",
        "logs"
    ]
    for d in dirs:
        Path(d).mkdir(parents=True, exist_ok=True)
        print(f"  ✓ Created {d}/")
    
    # Install dependencies
    print("\nInstalling Python dependencies...")
    packages = [
        "mediapipe>=0.10.0",
        "opencv-python>=4.8.0",
        "pyautogui>=0.9.54",
        "numpy>=1.24.0",
        "pynput>=1.7.6",
        "PyYAML>=6.0",
        "scipy>=1.11.0",
        "filterpy>=1.4.5"
    ]
    
    if sys.platform == "win32":
        packages.append("pycaw>=20181228")
        packages.append("pywin32")
    
    for pkg in packages:
        success = run(f"{sys.executable} -m pip install \"{pkg}\" -q", f"Installing {pkg.split('>=')[0]}")
        print(f"  {'✓' if success else '✗'} {pkg.split('>=')[0]}")
    
    print("\n" + "═" * 50)
    print("Installation complete.")
    print("Run: python main.py")
    print("═" * 50)

if __name__ == "__main__":
    main()
