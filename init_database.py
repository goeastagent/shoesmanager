#!/usr/bin/env python3
"""
Database Initialization Script

Creates a fresh database with sample data for the Shoes Management System.
"""

import os
import sys
from pathlib import Path
from datetime import date
from decimal import Decimal

# Add project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

def initialize_database():
    """Initialize database with fresh schema and sample data"""
    print("🗄️ Initializing Shoes Management System Database...")
    print("=" * 50)
    
    try:
        # Import required modules
        from app.db import db_manager
        from app.models import Base
        from app.repository import InventoryRepository
        from app.schemas import InventoryItemCreate
        
        # Create fresh database
        db_file = Path("inventory_management.db")
        if db_file.exists():
            backup_file = Path("inventory_management_backup.db")
            if backup_file.exists():
                backup_file.unlink()
            db_file.rename(backup_file)
            print("✅ Existing database backed up as inventory_management_backup.db")
        
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
                }
            ]
            
            # Add sample items
            added_count = 0
            for item_data in sample_items:
                try:
                    item_schema = InventoryItemCreate(**item_data)
                    repository.create_with_barcode_update(item_schema)
                    added_count += 1
                    print(f"✅ Added: {item_data['name']}")
                except Exception as e:
                    print(f"⚠️ Could not add {item_data['name']}: {e}")
            
            print(f"✅ {added_count} sample items added to database.")
        
        print("=" * 50)
        print("🎉 Database initialization completed successfully!")
        print("📁 Database file: inventory_management.db")
        print("📊 Sample items: 5 inventory items with barcodes")
        print("=" * 50)
        
        return True
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        print("Please check your environment and try again.")
        return False

def main():
    """Main function"""
    print("🚀 Shoes Management System - Database Initializer")
    print("=" * 50)
    
    # Check if running from correct directory
    if not Path("app/ui/tk_app.py").exists():
        print("❌ Please run from project root directory.")
        print("   Expected: app/ui/tk_app.py")
        return False
    
    # Initialize database
    success = initialize_database()
    
    if success:
        print("\n🎯 Next steps:")
        print("1. Run the GUI: python -m app.ui.tk_app")
        print("2. Or run CLI: python -m app.ui.cli list")
        print("3. Test barcode scanning with sample barcodes")
    
    return success

if __name__ == "__main__":
    success = main()
    if not success:
        sys.exit(1)
