#!/usr/bin/env python3
"""
Shoes Management System - Quick Run Script

Simple script to quickly run the GUI application.
"""

import sys
import subprocess
from pathlib import Path

def main():
    """Main function"""
    print("🚀 Starting Shoes Management System...")
    
    # Check if we're in the right directory
    if not Path("app/ui/tk_app.py").exists():
        print("❌ Please run from project root directory.")
        print("   Expected: app/ui/tk_app.py")
        return False
    
    # Check if virtual environment exists
    venv_path = Path("venv")
    if not venv_path.exists():
        print("❌ Virtual environment not found!")
        print("   Please run: python build.py")
        return False
    
    # Get Python command
    if sys.platform == "win32":
        python_cmd = str(Path("venv/Scripts/python"))
    else:
        python_cmd = str(Path("venv/bin/python"))
    
    try:
        # Run the GUI
        subprocess.check_call([python_cmd, "-m", "app.ui.tk_app"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run GUI: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 Application closed by user.")
        return True

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        sys.exit(1)
