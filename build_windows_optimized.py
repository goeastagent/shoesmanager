#!/usr/bin/env python3
"""
Optimized Windows Executable Build Script

Enhanced build script for Windows environment with better compatibility
and English locale support.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Set environment variables for English locale and Windows compatibility
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'
os.environ['PYTHONIOENCODING'] = 'utf-8'

def setup_windows_environment():
    """Setup Windows environment for optimal build"""
    print("🔧 Setting up Windows environment...")
    
    # Set console code page to UTF-8
    try:
        subprocess.run(['chcp', '65001'], shell=True, check=True, capture_output=True)
        print("✅ Console code page set to UTF-8")
    except subprocess.CalledProcessError:
        print("⚠️ Could not set console code page")
    
    # Ensure Python path is correct
    python_path = sys.executable
    print(f"✅ Python path: {python_path}")

def check_pyinstaller():
    """Check and install PyInstaller"""
    try:
        import PyInstaller
        print("✅ PyInstaller is already installed.")
        return True
    except ImportError:
        print("❌ PyInstaller is not installed.")
        print("📦 Installing PyInstaller...")
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", 
                "pyinstaller>=6.0.0",
                "--upgrade"
            ])
            print("✅ PyInstaller installation completed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller installation failed: {e}")
            return False

def create_optimized_spec_file():
    """Create optimized PyInstaller spec file for Windows"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

import sys
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collect all data files
datas = [
    ('app/config.py', 'app'),
    ('app/models.py', 'app'),
    ('app/schemas.py', 'app'),
    ('app/repository.py', 'app'),
    ('app/db.py', 'app'),
    ('app/utils.py', 'app'),
    ('app/services', 'app/services'),
    ('app/migrations', 'app/migrations'),
    ('inventory_management.db', '.'),
    ('requirements.txt', '.'),
]

# Add SQLAlchemy data files
try:
    datas += collect_data_files('sqlalchemy')
except:
    pass

a = Analysis(
    ['app/ui/tk_app.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'sqlalchemy.ext.hybrid',
        'sqlalchemy.sql',
        'sqlalchemy.sql.functions',
        'sqlalchemy.dialects.sqlite',
        'pydantic',
        'pydantic_settings',
        'pydantic.validators',
        'pydantic.fields',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'tkinter.simpledialog',
        'decimal',
        'datetime',
        'uuid',
        'threading',
        'logging',
        'csv',
        'json',
        'pathlib',
        'typing',
        'alembic',
        'alembic.runtime',
        'alembic.operations',
        'typer',
        'tabulate',
        'dotenv',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'PIL',
        'cv2',
        'tensorflow',
        'torch',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='ShoesManager',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI application - hide console
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,
    version=None,
)
'''
    
    with open('ShoesManager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ Optimized ShoesManager.spec file created.")

def build_executable():
    """Build executable with Windows optimizations"""
    print("🔨 Building executable with Windows optimizations...")
    
    try:
        # Clean previous builds
        if Path("build").exists():
            shutil.rmtree("build")
        if Path("dist").exists():
            shutil.rmtree("dist")
        
        # Run PyInstaller with Windows-specific options
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "--log-level=INFO",
            "ShoesManager.spec"
        ])
        
        print("✅ Build completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_distribution():
    """Create optimized distribution package"""
    print("📦 Creating optimized distribution package...")
    
    # Create distribution directory
    dist_dir = Path("dist")
    if not dist_dir.exists():
        dist_dir.mkdir()
    
    # Copy executable
    exe_file = Path("dist/ShoesManager.exe")
    if exe_file.exists():
        print("✅ Executable file found in dist folder.")
        
        # Create user guide
        guide_content = """# Shoes Management System

## Quick Start
1. Double-click ShoesManager.exe to run
2. The application will start with the inventory management interface

## Features
- Inventory management (Add/Edit/Delete items)
- Barcode scanning for automatic data entry
- Sales processing by barcode
- CSV import/export functionality
- HTML report generation
- Search and filter capabilities

## System Requirements
- Windows 10 or higher
- No additional software required (all dependencies included)

## Troubleshooting
- If the application doesn't start, try running as administrator
- Add to antivirus exceptions if blocked
- Ensure Windows Defender allows the application

## Support
For technical support, contact the development team.

Version: 1.0
Build Date: """ + str(Path().cwd()) + """
"""
        
        with open("dist/USER_GUIDE.txt", "w", encoding="utf-8") as f:
            f.write(guide_content)
        
        print("✅ User guide created.")
    else:
        print("❌ Executable file not found!")

def main():
    """Main build process"""
    print("🚀 Starting optimized Windows build process...")
    print("=" * 60)
    
    # Check if running from correct directory
    if not Path("app/ui/tk_app.py").exists():
        print("❌ Please run from project root directory.")
        print("   Expected: app/ui/tk_app.py")
        return False
    
    # Setup Windows environment
    setup_windows_environment()
    
    # Check and install PyInstaller
    if not check_pyinstaller():
        return False
    
    # Create optimized spec file
    create_optimized_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create distribution
    create_distribution()
    
    print("=" * 60)
    print("🎉 Optimized build completed successfully!")
    print("📁 Executable: dist/ShoesManager.exe")
    print("📄 User Guide: dist/USER_GUIDE.txt")
    print("=" * 60)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("❌ Build process failed!")
        sys.exit(1)
    else:
        print("✅ Build process completed successfully!")
