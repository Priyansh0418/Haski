#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Check what error message the backend returns for login
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fastapi.testclient import TestClient
from app.main import app
import json

client = TestClient(app)

print("Testing login with actual error response body...\n")

# Test 1: With email
print("Test 1: Login with email=demo@haski.com, password=Demo@123")
response = client.post("/api/v1/auth/login", json={
    "email": "demo@haski.com",
    "password": "Demo@123"
})

print(f"Status: {response.status_code}")
print(f"Headers: {dict(response.headers)}")
print(f"Body:\n{json.dumps(response.json(), indent=2)}\n")

# Test 2: With wrong password
print("Test 2: Login with wrong password")
response = client.post("/api/v1/auth/login", json={
    "email": "demo@haski.com",
    "password": "WrongPassword123"
})

print(f"Status: {response.status_code}")
print(f"Body:\n{json.dumps(response.json(), indent=2)}\n")

# Test 3: With non-existent email
print("Test 3: Login with non-existent email")
response = client.post("/api/v1/auth/login", json={
    "email": "nonexistent@example.com",
    "password": "Demo@123"
})

print(f"Status: {response.status_code}")
print(f"Body:\n{json.dumps(response.json(), indent=2)}\n")

# Test 4: With username instead of email
print("Test 4: Login with username=demo, password=Demo@123")
response = client.post("/api/v1/auth/login", json={
    "username": "demo",
    "password": "Demo@123"
})

print(f"Status: {response.status_code}")
print(f"Body:\n{json.dumps(response.json(), indent=2)}\n")
