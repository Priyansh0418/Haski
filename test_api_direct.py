#!/usr/bin/env python
"""Test API endpoints directly with TestClient"""
import sys
sys.path.insert(0, '/d:/Haski-main')

from fastapi.testclient import TestClient
from backend.app.main import app
from pathlib import Path
import json

client = TestClient(app)

print("=" * 60)
print("TESTING API ENDPOINTS DIRECTLY")
print("=" * 60)

# Test 1: Health check
print("\nTest 1: Health Check")
response = client.get('/api/v1/health')
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")

# Test 2: Root endpoint
print("\nTest 2: Root Endpoint")
response = client.get('/')
print(f"  Status: {response.status_code}")
print(f"  Response: {response.json()}")

# Test 3: Try to upload and analyze an image (without auth)
print("\nTest 3: Upload & Analyze (Should fail - no auth)")
test_image_path = Path("d:/Haski-main/test_image.jpg")
if test_image_path.exists():
    with open(test_image_path, "rb") as f:
        files = {"image": ("test_image.jpg", f, "image/jpeg")}
        response = client.post("/api/v1/analyze/photo", files=files)
    print(f"  Status: {response.status_code}")
    print(f"  Response: {response.json()}")
else:
    print(f"  Test image not found at {test_image_path}")

print("\n" + "=" * 60)
print("Tests complete!")
print("=" * 60)
