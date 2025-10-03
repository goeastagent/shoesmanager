#!/usr/bin/env python3
"""
Windows Executable Build Script

Builds GUI application to Windows executable (.exe) using PyInstaller.
Optimized for English Windows environment.
"""

import os
import sys
import subprocess
import shutil
from pathlib import Path

# Set environment variables for English locale
os.environ['LANG'] = 'en_US.UTF-8'
os.environ['LC_ALL'] = 'en_US.UTF-8'

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
            subprocess.check_call([sys.executable, "-m", "pip", "install", "pyinstaller"])
            print("✅ PyInstaller installation completed!")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ PyInstaller installation failed: {e}")
            return False

def create_spec_file():
    """Create PyInstaller spec file"""
    spec_content = '''# -*- mode: python ; coding: utf-8 -*-

block_cipher = None

a = Analysis(
    ['app/ui/tk_app.py'],
    pathex=[],
    binaries=[],
    datas=[
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
    ],
    hiddenimports=[
        'sqlalchemy',
        'sqlalchemy.orm',
        'sqlalchemy.ext.declarative',
        'pydantic',
        'pydantic_settings',
        'tkinter',
        'tkinter.ttk',
        'tkinter.messagebox',
        'tkinter.filedialog',
        'decimal',
        'datetime',
        'uuid',
        'threading',
        'logging',
        'csv',
        'json',
        'pathlib',
        'typing',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
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
    console=False,  # GUI 애플리케이션이므로 콘솔 창 숨김
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # 아이콘 파일이 있다면 여기에 경로 지정
)
'''
    
    with open('ShoesManager.spec', 'w', encoding='utf-8') as f:
        f.write(spec_content)
    
    print("✅ ShoesManager.spec file has been created.")

def build_executable():
    """Build executable file"""
    print("🔨 Starting executable build...")
    
    try:
        # Run PyInstaller build
        subprocess.check_call([
            sys.executable, "-m", "PyInstaller",
            "--clean",
            "--noconfirm",
            "ShoesManager.spec"
        ])
        
        print("✅ Build completed successfully!")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Build failed: {e}")
        return False

def create_distribution():
    """Create distribution folder"""
    print("📦 Creating distribution folder...")
    
    dist_dir = Path("dist/ShoesManager")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Copy executable file
    exe_file = Path("dist/ShoesManager.exe")
    if exe_file.exists():
        shutil.copy2(exe_file, dist_dir.parent / "ShoesManager.exe")
        print("✅ Executable file copied to dist folder.")
    
    # Create README file
    readme_content = """# Shoes Management System (ShoesManager)

## How to Run
1. Double-click ShoesManager.exe to run the application.
2. The inventory management screen will be displayed when the program starts.

## Main Features
- Add/Edit/Delete inventory items
- Automatic information input via barcode scanning
- Sales processing by barcode
- CSV import/export
- HTML report generation

## System Requirements
- Windows 10 or higher
- .NET Framework 4.7.2 or higher (if needed)

## Troubleshooting
- If the program doesn't run, try running as administrator.
- If blocked by antivirus software, add to exceptions.

## Support
Contact the developer if you encounter any issues.
"""
    
    with open("dist/README.txt", "w", encoding="utf-8") as f:
        f.write(readme_content)
    
    print("✅ README.txt file has been created.")

def main():
    """Main function"""
    print("🚀 Starting Windows executable build...")
    print("=" * 50)
    
    # Check current directory
    if not Path("app/ui/tk_app.py").exists():
        print("❌ Please run from project root directory.")
        return False
    
    # Check and install PyInstaller
    if not check_pyinstaller():
        return False
    
    # Create spec file
    create_spec_file()
    
    # Build executable
    if not build_executable():
        return False
    
    # Create distribution folder
    create_distribution()
    
    print("=" * 50)
    print("🎉 Build completed successfully!")
    print("📁 Executable location: dist/ShoesManager.exe")
    print("📄 README file: dist/README.txt")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
