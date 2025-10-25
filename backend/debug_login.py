#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Debug script to test actual login with detailed error information
"""

import sys
from pathlib import Path
import json

if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.db_models import User
from app.core.security import verify_password
from fastapi.testclient import TestClient
from app.main import app

db = SessionLocal()
client = TestClient(app)

print("=" * 80)
print("DEBUGGING LOGIN ISSUE")
print("=" * 80)

# 1. Check if demo user exists
print("\n1. Checking if demo@haski.com user exists in database...")
user = db.query(User).filter(User.email == "demo@haski.com").first()

if not user:
    print("   ❌ ERROR: User demo@haski.com NOT FOUND in database!")
    print("\n   Available users in database:")
    all_users = db.query(User).all()
    for u in all_users:
        print(f"     - {u.username} ({u.email})")
else:
    print(f"   ✅ Found user: {user.username} ({user.email})")
    print(f"      User ID: {user.id}")
    print(f"      Has password hash: {bool(user.hashed_password)}")
    
    if not user.hashed_password:
        print("      ❌ ERROR: User has NO password hash!")
        sys.exit(1)
    
    # 2. Test password verification directly
    print("\n2. Testing password verification...")
    test_password = "Demo@123"
    is_valid = verify_password(test_password, user.hashed_password)
    print(f"   Password '{test_password}' verification: {'✅ PASS' if is_valid else '❌ FAIL'}")
    
    if not is_valid:
        print(f"      Stored hash: {user.hashed_password[:40]}...")
        from app.core.security import get_password_hash
        expected_hash = get_password_hash(test_password)
        print(f"      Expected hash: {expected_hash[:40]}...")
        sys.exit(1)

# 3. Test API endpoint
print("\n3. Testing API endpoint directly...")
payload = {
    "email": "demo@haski.com",
    "password": "Demo@123"
}

print(f"   Sending: {json.dumps(payload)}")
response = client.post("/api/v1/auth/login", json=payload)

print(f"   Response Status: {response.status_code}")
print(f"   Response Body: {response.text}")

if response.status_code == 200:
    print("   ✅ SUCCESS!")
else:
    print(f"   ❌ ERROR: Got {response.status_code}")
    try:
        error_data = response.json()
        print(f"      Error detail: {error_data}")
    except:
        pass

# 4. Debug the actual login process
print("\n4. Debug trace - what happens in login process...")
from sqlalchemy import or_

email = "demo@haski.com"
password = "Demo@123"

print(f"   Looking up user with email: {email}")
found_user = db.query(User).filter(or_(User.username == email, User.email == email)).first()

if found_user:
    print(f"   ✅ Found user: {found_user.username}")
    print(f"      Has password hash: {bool(found_user.hashed_password)}")
    
    if not found_user.hashed_password:
        print(f"      ❌ ISSUE: User has no password hash!")
    else:
        pwd_match = verify_password(password, found_user.hashed_password)
        print(f"      Password matches: {pwd_match}")
        
        if pwd_match:
            from app.core.security import create_access_token
            token = create_access_token(subject=found_user.id)
            print(f"      ✅ Would create token: {token[:40]}...")
        else:
            print(f"      ❌ Password does not match!")
else:
    print(f"   ❌ User not found!")

print("\n" + "=" * 80)

db.close()
