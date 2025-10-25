#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Comprehensive API Integration Test
Tests backend login endpoint and data flow
"""

import json
import sys
from pathlib import Path

# Fix encoding for Windows
if sys.stdout.encoding != 'utf-8':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

sys.path.insert(0, str(Path(__file__).parent))

from app.db.session import SessionLocal
from app.models.db_models import User
from app.core.security import verify_password, get_password_hash
from fastapi.testclient import TestClient
from app.main import app

db = SessionLocal()
client = TestClient(app)

print("=" * 70)
print("🔍 COMPREHENSIVE API INTEGRATION TEST")
print("=" * 70)

# 1. Check database
print("\n1️⃣  DATABASE CHECK")
print("-" * 70)
users = db.query(User).all()
print(f"Total users in database: {len(users)}")
for user in users:
    has_password = "✅ Yes" if user.hashed_password else "❌ No"
    print(f"  - {user.username:12} | {user.email:20} | Password: {has_password}")

# 2. Test direct password verification
print("\n2️⃣  PASSWORD VERIFICATION CHECK")
print("-" * 70)
test_creds = [
    ("demo@haski.com", "Demo@123"),
    ("test@haski.com", "Test@123"),
    ("john@haski.com", "John@123"),
]

for email, password in test_creds:
    user = db.query(User).filter(User.email == email).first()
    if user and user.hashed_password:
        is_valid = verify_password(password, user.hashed_password)
        status = "✅ PASS" if is_valid else "❌ FAIL"
        print(f"{status} | {user.username:12} | {email:20} | {password}")
    else:
        print(f"❌ FAIL | User not found or no password: {email}")

# 3. Test backend login endpoint
print("\n3️⃣  BACKEND API LOGIN ENDPOINT TEST")
print("-" * 70)

for email, password in test_creds:
    payload = {
        "email": email,
        "password": password,
    }
    
    print(f"\nTesting: {email}")
    print(f"  Payload: {json.dumps(payload)}")
    
    response = client.post("/api/v1/auth/login", json=payload)
    
    print(f"  Status Code: {response.status_code}")
    print(f"  Response: {response.json()}")
    
    if response.status_code == 200:
        data = response.json()
        if "access_token" in data:
            print(f"  ✅ SUCCESS: Got token (first 30 chars): {data['access_token'][:30]}...")
        else:
            print(f"  ❌ ERROR: No access_token in response")
    else:
        print(f"  ❌ ERROR: {response.status_code} - {response.json()}")

# 4. Test with username instead of email
print("\n4️⃣  BACKEND API LOGIN WITH USERNAME TEST")
print("-" * 70)

username_tests = [
    ("demo", "Demo@123"),
    ("testuser", "Test@123"),
    ("john_doe", "John@123"),
]

for username, password in username_tests:
    payload = {
        "username": username,
        "password": password,
    }
    
    print(f"\nTesting: {username}")
    print(f"  Payload: {json.dumps(payload)}")
    
    response = client.post("/api/v1/auth/login", json=payload)
    
    print(f"  Status Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"  ✅ SUCCESS: Got token")
    else:
        print(f"  ❌ ERROR: {response.status_code} - {response.json()}")

# 5. Check auth endpoint schema
print("\n5️⃣  AUTH ENDPOINT SCHEMA CHECK")
print("-" * 70)
print("\nChecking what the login endpoint expects...")

# Try with email only
print("\n  Trying with 'email' field:")
response = client.post("/api/v1/auth/login", json={
    "email": "demo@haski.com",
    "password": "Demo@123"
})
print(f"    Status: {response.status_code}")

# Try with username only
print("\n  Trying with 'username' field:")
response = client.post("/api/v1/auth/login", json={
    "username": "demo",
    "password": "Demo@123"
})
print(f"    Status: {response.status_code}")

# Try with both
print("\n  Trying with both 'username' and 'email' fields:")
response = client.post("/api/v1/auth/login", json={
    "username": "demo",
    "email": "demo@haski.com",
    "password": "Demo@123"
})
print(f"    Status: {response.status_code}")

print("\n" + "=" * 70)
print("✅ TEST COMPLETE")
print("=" * 70)

db.close()
