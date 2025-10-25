#!/usr/bin/env python
"""Test script to debug login issues"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.db_models import User
from app.core.security import verify_password, get_password_hash

db = SessionLocal()

# Check what users exist
print("=" * 60)
print("📋 USERS IN DATABASE")
print("=" * 60)
users = db.query(User).all()
print(f"Total users: {len(users)}\n")

for user in users:
    print(f"Username: {user.username}")
    print(f"Email:    {user.email}")
    if user.hashed_password:
        print(f"Password Hash: {user.hashed_password[:30]}...")
    else:
        print(f"Password Hash: ❌ NONE (no password set!)")
    print()

# Test password verification
print("=" * 60)
print("🔐 PASSWORD VERIFICATION TEST")
print("=" * 60)

test_password = "Test@123"  # Try the password for testuser
test_email = "test@haski.com"

# Find user by email
user = db.query(User).filter(User.email == test_email).first()

if user:
    print(f"✅ Found user: {user.username} ({user.email})")
    print(f"   Has password hash: {bool(user.hashed_password)}")
    
    if user.hashed_password:
        is_correct = verify_password(test_password, user.hashed_password)
        print(f"   Password '{test_password}' matches: {is_correct}")
        
        # Debug: show what the hash should be
        expected_hash = get_password_hash(test_password)
        print(f"\n   Input password hash:    {expected_hash[:30]}...")
        print(f"   Stored password hash:   {user.hashed_password[:30]}...")
        print(f"   Hashes match: {expected_hash == user.hashed_password}")
    else:
        print(f"   ⚠️  No password hash stored!")
else:
    print(f"❌ User not found with email: {test_email}")
    print("   Available emails:")
    for user in users:
        print(f"     - {user.email}")

db.close()
