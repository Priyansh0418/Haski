#!/usr/bin/env python
"""
Seed Demo Users Script

Creates demo test accounts in the database for easy testing.
This script can be run from the root directory:

    python seed_demo_users.py
"""

import sys
from pathlib import Path

# Add the backend module to path
backend_dir = Path(__file__).parent
sys.path.insert(0, str(backend_dir))

from app.db.session import SessionLocal, engine
from app.db.base import Base
from app.models.db_models import User
from app.core.security import get_password_hash


def seed_demo_users():
    """Create demo users in the database."""
    db = SessionLocal()

    # Demo accounts to create
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

    try:
        # Ensure tables exist
        Base.metadata.create_all(bind=engine)

        for account in demo_accounts:
            # Check if user already exists
            existing = db.query(User).filter(
                (User.username == account["username"]) | (User.email == account["email"])
            ).first()

            if existing:
                print(f"⚠️  User '{account['username']}' already exists, skipping...")
                continue

            # Create new user
            hashed_password = get_password_hash(account["password"])
            user = User(
                username=account["username"],
                email=account["email"],
                hashed_password=hashed_password,
            )
            db.add(user)
            print(
                f"✅ Created user: {account['username']} | {account['email']} | Password: {account['password']}"
            )

        db.commit()
        print("\n✨ Demo users seeded successfully!")
        print("\n📝 Demo Credentials:")
        print("=" * 60)
        for account in demo_accounts:
            existing = db.query(User).filter(User.username == account["username"]).first()
            if existing:
                print(f"\n👤 Username: {account['username']}")
                print(f"📧 Email:    {account['email']}")
                print(f"🔐 Password: {account['password']}")
        print("\n" + "=" * 60)

    except Exception as e:
        print(f"❌ Error seeding demo users: {str(e)}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    print("🌱 Seeding demo users...\n")
    seed_demo_users()
