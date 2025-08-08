#!/usr/bin/env python3
"""
Database initialization script - Creates database schema.
This should be run once after starting the database containers.
"""

import sys
from pathlib import Path

# Add packages to Python path
common_path = Path(__file__).parent / "packages" / "common" / "src"
sys.path.insert(0, str(common_path))

from common.db import enable_extensions, create_tables

def main():
    print("🗄️  Healthcare Support Portal - Database Initialization")
    print("=" * 55)
    
    try:
        print("🔧 Enabling PostgreSQL extensions...")
        enable_extensions()
        print("✅ Extensions enabled successfully")
        
        print("📋 Creating database tables...")
        create_tables()
        print("✅ Database schema created successfully")
        
        print("\n✅ Database initialization complete!")
        print("📝 Next steps:")
        print("   - Install frontend dependencies: cd frontend && npm install")
        print("   - Seed demo data: uv run python packages/common/src/common/seed_data.py")
        print("   - Start all services: ./run_all.sh")
        
    except Exception as e:
        print(f"❌ Database initialization failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)