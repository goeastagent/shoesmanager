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
        from datetime import date
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
    """Create distribution folder"""
    print("📦 Creating distribution folder...")
    
    dist_dir = Path("dist/ShoesManager")
    if dist_dir.exists():
        shutil.rmtree(dist_dir)
    
    # Initialize fresh database
    if not initialize_database():
        print("⚠️ Using existing database file.")
        # Copy existing database if initialization failed
        existing_db = Path("inventory_management.db")
        if existing_db.exists():
            shutil.copy2(existing_db, Path("dist/inventory_management.db"))
    
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
3. Sample data is included for testing.

## Main Features
- Add/Edit/Delete inventory items
- Automatic information input via barcode scanning
- Sales processing by barcode
- CSV import/export
- HTML report generation

## Sample Data
The application comes with sample inventory items:
- Nike Air Max 270 White (Barcode: 1234567890123)
- Adidas Ultraboost 22 Black (Barcode: 2345678901234)
- Converse Chuck Taylor All Star (Barcode: 3456789012345)

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
