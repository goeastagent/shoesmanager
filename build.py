#!/usr/bin/env python3
"""
Shoes Management System - Universal Build Tool

Cross-platform build script that handles environment setup, 
database initialization, and executable building.
"""

import os
import sys
import subprocess
import shutil
import platform
from pathlib import Path

def print_header():
    """Print build tool header"""
    print("=" * 60)
    print("    Shoes Management System - Universal Build Tool")
    print("=" * 60)
    print()

def check_python_version():
    """Check if Python version is compatible"""
    print("🐍 Checking Python version...")
    
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print(f"❌ Python {version.major}.{version.minor} is not supported.")
        print("   Please install Python 3.8 or higher.")
        return False
    
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} is compatible.")
    return True

def check_project_structure():
    """Check if we're in the correct project directory"""
    print("📁 Checking project structure...")
    
    required_files = [
        "app/ui/tk_app.py",
        "app/models.py",
        "app/db.py",
        "requirements.txt"
    ]
    
    for file_path in required_files:
        if not Path(file_path).exists():
            print(f"❌ Required file not found: {file_path}")
            print("   Please run this script from the project root directory.")
            return False
    
    print("✅ Project structure verified.")
    return True

def setup_virtual_environment():
    """Setup virtual environment"""
    print("🔧 Setting up virtual environment...")
    
    venv_path = Path("venv")
    
    # Check if virtual environment already exists
    if venv_path.exists():
        print("✅ Virtual environment already exists.")
        return True
    
    # Create virtual environment
    try:
        subprocess.check_call([sys.executable, "-m", "venv", "venv"])
        print("✅ Virtual environment created successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to create virtual environment: {e}")
        return False

def get_pip_command():
    """Get the correct pip command for the platform"""
    if platform.system() == "Windows":
        return str(Path("venv/Scripts/pip"))
    else:
        return str(Path("venv/bin/pip"))

def get_python_command():
    """Get the correct python command for the platform"""
    if platform.system() == "Windows":
        return str(Path("venv/Scripts/python"))
    else:
        return str(Path("venv/bin/python"))

def install_dependencies():
    """Install project dependencies"""
    print("📦 Installing dependencies...")
    
    pip_cmd = get_pip_command()
    python_cmd = get_python_command()
    
    try:
        # Upgrade pip first
        subprocess.check_call([python_cmd, "-m", "pip", "install", "--upgrade", "pip"])
        
        # Install requirements
        subprocess.check_call([pip_cmd, "install", "-r", "requirements.txt"])
        print("✅ Dependencies installed successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to install dependencies: {e}")
        return False

def initialize_database():
    """Initialize database with sample data"""
    print("🗄️ Initializing database...")
    
    python_cmd = get_python_command()
    
    try:
        subprocess.check_call([python_cmd, "init_database_safe.py"])
        print("✅ Database initialized successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def build_executable():
    """Build executable using PyInstaller"""
    print("🔨 Building executable...")
    
    python_cmd = get_python_command()
    
    try:
        # Use the optimized build script
        subprocess.check_call([python_cmd, "build_windows_optimized.py"])
        print("✅ Executable built successfully.")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def run_gui():
    """Run the GUI application"""
    print("🚀 Running GUI application...")
    
    python_cmd = get_python_command()
    
    try:
        subprocess.check_call([python_cmd, "-m", "app.ui.tk_app"])
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to run GUI: {e}")
        return False
    except KeyboardInterrupt:
        print("\n👋 GUI closed by user.")
        return True

def show_menu():
    """Show interactive menu"""
    while True:
        print("\n" + "=" * 60)
        print("    Shoes Management System - Build Menu")
        print("=" * 60)
        print()
        print("1. 🚀 Complete Setup (Environment + Database + Build)")
        print("2. 🔧 Setup Environment Only")
        print("3. 🗄️ Initialize Database Only")
        print("4. 🔨 Build Executable Only")
        print("5. ▶️ Run GUI Application")
        print("6. 📋 Show Status")
        print("7. ❌ Exit")
        print()
        
        choice = input("Select an option (1-7): ").strip()
        
        if choice == "1":
            return "complete"
        elif choice == "2":
            return "setup"
        elif choice == "3":
            return "database"
        elif choice == "4":
            return "build"
        elif choice == "5":
            return "run"
        elif choice == "6":
            return "status"
        elif choice == "7":
            return "exit"
        else:
            print("❌ Invalid choice. Please select 1-7.")

def show_status():
    """Show current status"""
    print("\n📋 Current Status:")
    print("-" * 40)
    
    # Check virtual environment
    venv_exists = Path("venv").exists()
    print(f"Virtual Environment: {'✅ Exists' if venv_exists else '❌ Not found'}")
    
    # Check database
    db_exists = Path("inventory_management.db").exists()
    print(f"Database: {'✅ Exists' if db_exists else '❌ Not found'}")
    
    # Check executable
    exe_exists = Path("dist/ShoesManager.exe").exists()
    print(f"Executable: {'✅ Exists' if exe_exists else '❌ Not found'}")
    
    # Check dependencies
    if venv_exists:
        pip_cmd = get_pip_command()
        try:
            result = subprocess.run([pip_cmd, "list"], capture_output=True, text=True)
            if "sqlalchemy" in result.stdout:
                print("Dependencies: ✅ Installed")
            else:
                print("Dependencies: ❌ Not installed")
        except:
            print("Dependencies: ❓ Unknown")
    else:
        print("Dependencies: ❓ Virtual environment not found")

def main():
    """Main function"""
    print_header()
    
    # Check Python version
    if not check_python_version():
        return False
    
    # Check project structure
    if not check_project_structure():
        return False
    
    # Show menu if no command line arguments
    if len(sys.argv) == 1:
        action = show_menu()
    else:
        action = sys.argv[1].lower()
    
    if action == "exit":
        print("👋 Goodbye!")
        return True
    
    if action == "status":
        show_status()
        return True
    
    success = True
    
    if action in ["complete", "setup"]:
        success &= setup_virtual_environment()
        success &= install_dependencies()
    
    if action in ["complete", "database"]:
        success &= initialize_database()
    
    if action in ["complete", "build"]:
        success &= build_executable()
    
    if action == "run":
        success &= run_gui()
    
    if success:
        print("\n" + "=" * 60)
        print("🎉 Operation completed successfully!")
        print("=" * 60)
        
        if action == "complete":
            print("\n📁 Files created:")
            print("   - dist/ShoesManager.exe (Executable)")
            print("   - dist/USER_GUIDE.txt (User Guide)")
            print("   - inventory_management.db (Database)")
            print("\n🚀 You can now run the executable or use the GUI!")
    else:
        print("\n❌ Operation failed. Please check the error messages above.")
    
    return success

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n👋 Build interrupted by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1)
