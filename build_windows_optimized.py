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

def initialize_database():
    """Initialize database with fresh schema and sample data"""
    print("🗄️ Initializing database...")
    
    try:
        # Import required modules
        sys.path.insert(0, str(Path.cwd()))
        from app.db import db_manager
        from app.models import Base
        from app.repository import InventoryRepository
        from app.schemas import InventoryItemCreate
        from datetime import date, datetime
        from decimal import Decimal
        
        # Create fresh database
        db_file = Path("inventory_management_fresh.db")
        if db_file.exists():
            db_file.unlink()  # Remove existing file
        
        # Set database URL to fresh file
        original_url = db_manager.database_url
        db_manager.database_url = f"sqlite:///./{db_file.name}"
        
        # Create all tables
        Base.metadata.create_all(db_manager.engine)
        print("✅ Database tables created.")
        
        # Add sample data
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            
            # Sample inventory items
            sample_items = [
                {
                    "location": "A-01",
                    "purchase_date": date(2024, 1, 15),
                    "model_name": "Nike Air Max 270",
                    "name": "Nike Air Max 270 White",
                    "size": "US 9",
                    "barcode": "1234567890123",
                    "vendor": "Nike Store",
                    "price": Decimal("120.00"),
                    "notes": "Sample item for demonstration"
                },
                {
                    "location": "A-02", 
                    "purchase_date": date(2024, 1, 20),
                    "model_name": "Adidas Ultraboost 22",
                    "name": "Adidas Ultraboost 22 Black",
                    "size": "US 10",
                    "barcode": "2345678901234",
                    "vendor": "Adidas Store",
                    "price": Decimal("180.00"),
                    "notes": "Popular running shoe"
                },
                {
                    "location": "B-01",
                    "purchase_date": date(2024, 2, 1),
                    "model_name": "Converse Chuck Taylor",
                    "name": "Converse Chuck Taylor All Star",
                    "size": "US 8",
                    "barcode": "3456789012345",
                    "vendor": "Converse Store",
                    "price": Decimal("65.00"),
                    "notes": "Classic canvas shoe"
                }
            ]
            
            # Add sample items
            for item_data in sample_items:
                try:
                    item_schema = InventoryItemCreate(**item_data)
                    repository.create_with_barcode_update(item_schema)
                except Exception as e:
                    print(f"⚠️ Could not add sample item: {e}")
            
            print("✅ Sample data added to database.")
        
        # Restore original database URL
        db_manager.database_url = original_url
        
        # Copy fresh database to dist folder
        dist_db = Path("dist/inventory_management.db")
        if dist_db.exists():
            dist_db.unlink()
        shutil.copy2(db_file, dist_db)
        
        # Clean up temporary file
        db_file.unlink()
        
        print("✅ Fresh database created and copied to dist folder.")
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False

def create_distribution():
    """Create optimized distribution package"""
    print("📦 Creating optimized distribution package...")
    
    # Create distribution directory
    dist_dir = Path("dist")
    if not dist_dir.exists():
        dist_dir.mkdir()
    
    # Initialize fresh database
    if not initialize_database():
        print("⚠️ Using existing database file.")
        # Copy existing database if initialization failed
        existing_db = Path("inventory_management.db")
        if existing_db.exists():
            shutil.copy2(existing_db, Path("dist/inventory_management.db"))
    
    # Copy executable
    exe_file = Path("dist/ShoesManager.exe")
    if exe_file.exists():
        print("✅ Executable file found in dist folder.")
        
        # Create user guide
        guide_content = """# Shoes Management System

## Quick Start
1. Double-click ShoesManager.exe to run
2. The application will start with the inventory management interface
3. Sample data is included for testing

## Features
- Inventory management (Add/Edit/Delete items)
- Barcode scanning for automatic data entry
- Sales processing by barcode
- CSV import/export functionality
- HTML report generation
- Search and filter capabilities

## Sample Data
The application comes with sample inventory items:
- Nike Air Max 270 White (Barcode: 1234567890123)
- Adidas Ultraboost 22 Black (Barcode: 2345678901234)
- Converse Chuck Taylor All Star (Barcode: 3456789012345)

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
