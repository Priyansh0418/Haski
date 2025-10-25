#!/usr/bin/env python
"""
Reset and reseed demo users with correct passwords
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.db_models import User
from app.core.security import get_password_hash

db = SessionLocal()

try:
    # Delete all users
    deleted = db.query(User).delete()
    db.commit()
    print(f"🗑️  Deleted {deleted} existing users")
    
    # Create fresh demo accounts
    demo_accounts = [
        {
            "username": "demo",
            "email": "demo@haski.com",
            "password": "Demo@123",
        },
        {
            "username": "testuser",
            "email": "test@haski.com",
            "password": "Test@123",
        },
        {
            "username": "john_doe",
            "email": "john@haski.com",
            "password": "John@123",
        },
    ]
    
    for account in demo_accounts:
        hashed_password = get_password_hash(account["password"])
        user = User(
            username=account["username"],
            email=account["email"],
            hashed_password=hashed_password,
        )
        db.add(user)
        print(f"✅ Created: {account['username']} | {account['email']} | {account['password']}")
    
    db.commit()
    
    print("\n✨ Demo users recreated successfully!")
    print("\n" + "=" * 60)
    print("📝 Login with these credentials:")
    print("=" * 60)
    for account in demo_accounts:
        print(f"\n👤 Username: {account['username']}")
        print(f"📧 Email:    {account['email']}")
        print(f"🔐 Password: {account['password']}")
    print("\n" + "=" * 60)
    
except Exception as e:
    print(f"❌ Error: {e}")
    db.rollback()
finally:
    db.close()
