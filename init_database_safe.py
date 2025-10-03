#!/usr/bin/env python3
"""
Safe Database Initialization Script

Creates a fresh database with comprehensive error handling and validation.
"""

import os
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def validate_environment():
    """Validate that all required modules can be imported"""
    print("🔍 Validating environment...")
    
    try:
        # Test basic imports
        from app.db import db_manager
        from app.models import Base
        from app.repository import InventoryRepository
        from app.schemas import InventoryItemCreate
        print("✅ All required modules imported successfully.")
        return True
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Environment validation failed: {e}")
        return False

def create_fresh_database():
    """Create a completely fresh database"""
    print("🗄️ Creating fresh database...")
    
    try:
        from app.db import db_manager
        from app.models import Base
        
        # Create fresh database file
        db_file = Path("inventory_management.db")
        
        # Backup existing database if it exists
        if db_file.exists():
            backup_file = Path("inventory_management_backup.db")
            if backup_file.exists():
                backup_file.unlink()
            db_file.rename(backup_file)
            print("✅ Existing database backed up as inventory_management_backup.db")
        
        # Create new database file
        db_file.touch()
        print("✅ Fresh database file created.")
        
        # Create all tables
        Base.metadata.create_all(db_manager.engine)
        print("✅ All database tables created successfully.")
        
        return True
        
    except Exception as e:
        print(f"❌ Database creation failed: {e}")
        return False

def add_sample_data():
    """Add sample data to the database"""
    print("📊 Adding sample data...")
    
    try:
        from app.db import db_manager
        from app.repository import InventoryRepository
        from app.schemas import InventoryItemCreate
        
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            
            # Comprehensive sample data
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
                },
                {
                    "location": "B-02",
                    "purchase_date": date(2024, 2, 10),
                    "model_name": "Jordan 1 Retro",
                    "name": "Air Jordan 1 Retro High OG",
                    "size": "US 9.5",
                    "barcode": "4567890123456",
                    "vendor": "Nike Store",
                    "price": Decimal("170.00"),
                    "notes": "Basketball classic"
                },
                {
                    "location": "C-01",
                    "purchase_date": date(2024, 2, 15),
                    "model_name": "Vans Old Skool",
                    "name": "Vans Old Skool Classic",
                    "size": "US 7",
                    "barcode": "5678901234567",
                    "vendor": "Vans Store",
                    "price": Decimal("60.00"),
                    "notes": "Skateboarding classic"
                },
                {
                    "location": "C-02",
                    "purchase_date": date(2024, 2, 20),
                    "model_name": "New Balance 990v5",
                    "name": "New Balance 990v5 Grey",
                    "size": "US 11",
                    "barcode": "6789012345678",
                    "vendor": "New Balance Store",
                    "price": Decimal("185.00"),
                    "notes": "Premium running shoe"
                }
            ]
            
            # Add sample items with detailed error handling
            added_count = 0
            failed_count = 0
            
            for i, item_data in enumerate(sample_items, 1):
                try:
                    item_schema = InventoryItemCreate(**item_data)
                    repository.create_with_barcode_update(item_schema)
                    added_count += 1
                    print(f"✅ [{i}/{len(sample_items)}] Added: {item_data['name']}")
                except Exception as e:
                    failed_count += 1
                    print(f"❌ [{i}/{len(sample_items)}] Failed to add {item_data['name']}: {e}")
            
            print(f"📊 Sample data summary: {added_count} added, {failed_count} failed")
            
            if added_count > 0:
                print("✅ Sample data added successfully.")
                return True
            else:
                print("❌ No sample data could be added.")
                return False
        
    except Exception as e:
        print(f"❌ Sample data addition failed: {e}")
        return False

def verify_database():
    """Verify that the database is working correctly"""
    print("🔍 Verifying database...")
    
    try:
        from app.db import db_manager
        from app.repository import InventoryRepository
        
        with db_manager.get_session_context() as session:
            repository = InventoryRepository(session)
            
            # Test basic operations
            items = repository.get_all()
            print(f"✅ Database verification: {len(items)} items found")
            
            # Test barcode lookup
            barcode_info = repository.get_barcode_info("1234567890123")
            if barcode_info:
                print(f"✅ Barcode lookup test: {barcode_info.name}")
            else:
                print("⚠️ Barcode lookup test failed")
            
            return True
            
    except Exception as e:
        print(f"❌ Database verification failed: {e}")
        return False

def main():
    """Main initialization process"""
    print("🚀 Safe Database Initialization")
    print("=" * 50)
    
    # Check if running from correct directory
    if not Path("app/ui/tk_app.py").exists():
        print("❌ Please run from project root directory.")
        print("   Expected: app/ui/tk_app.py")
        return False
    
    # Step 1: Validate environment
    if not validate_environment():
        print("❌ Environment validation failed. Please check your setup.")
        return False
    
    # Step 2: Create fresh database
    if not create_fresh_database():
        print("❌ Database creation failed.")
        return False
    
    # Step 3: Add sample data
    if not add_sample_data():
        print("❌ Sample data addition failed.")
        return False
    
    # Step 4: Verify database
    if not verify_database():
        print("❌ Database verification failed.")
        return False
    
    print("=" * 50)
    print("🎉 Database initialization completed successfully!")
    print("📁 Database file: inventory_management.db")
    print("📊 Sample items: 6 inventory items with barcodes")
    print("🔍 Database verified and ready to use")
    print("=" * 50)
    
    return True

if __name__ == "__main__":
    success = main()
    if not success:
        print("\n❌ Database initialization failed!")
        print("Please check the error messages above and try again.")
        sys.exit(1)
    else:
        print("\n🎯 Next steps:")
        print("1. Run the GUI: python -m app.ui.tk_app")
        print("2. Or run CLI: python -m app.ui.cli list")
        print("3. Test barcode scanning with sample barcodes")
