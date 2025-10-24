#!/usr/bin/env python
"""
Test script for Admin Recommender API endpoints.

Usage:
    python test_admin_api.py

Before running:
    1. Set ADMIN_SECRET environment variable:
       export ADMIN_SECRET="your-secret-token"
    
    2. Start the backend:
       python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
"""

import os
import requests
import json

# Configuration
BASE_URL = "http://localhost:8000"
ADMIN_SECRET = os.getenv("ADMIN_SECRET", "test-secret")

print(f"Admin API Test Script")
print(f"=" * 60)
print(f"Base URL: {BASE_URL}")
print(f"Admin Token: {ADMIN_SECRET}")
print()


def get_headers():
    """Get authorization headers with admin token."""
    return {
        "Authorization": f"Bearer {ADMIN_SECRET}",
        "Content-Type": "application/json"
    }


def test_reload_rules():
    """Test POST /admin/recommender/reload-rules endpoint."""
    print("TEST 1: Reload Rules")
    print("-" * 60)
    
    url = f"{BASE_URL}/admin/recommender/reload-rules"
    
    try:
        response = requests.post(url, headers=get_headers())
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        print()
        return False


def test_get_status():
    """Test GET /admin/recommender/status endpoint."""
    print("TEST 2: Get Engine Status")
    print("-" * 60)
    
    url = f"{BASE_URL}/admin/recommender/status"
    
    try:
        response = requests.get(url, headers=get_headers())
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        print()
        return response.status_code == 200
    except Exception as e:
        print(f"Error: {e}")
        print()
        return False


def test_no_auth():
    """Test that endpoints require authentication."""
    print("TEST 3: Test Missing Authorization (should fail)")
    print("-" * 60)
    
    url = f"{BASE_URL}/admin/recommender/status"
    
    try:
        response = requests.get(url)  # No auth header
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        print()
        return response.status_code == 401
    except Exception as e:
        print(f"Error: {e}")
        print()
        return False


def test_invalid_token():
    """Test that invalid tokens are rejected."""
    print("TEST 4: Test Invalid Token (should fail)")
    print("-" * 60)
    
    url = f"{BASE_URL}/admin/recommender/status"
    headers = {
        "Authorization": "Bearer invalid-token",
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.get(url, headers=headers)
        print(f"Status: {response.status_code}")
        print(f"Response:")
        print(json.dumps(response.json(), indent=2))
        print()
        return response.status_code == 403
    except Exception as e:
        print(f"Error: {e}")
        print()
        return False


if __name__ == "__main__":
    results = []
    
    results.append(("Reload Rules", test_reload_rules()))
    results.append(("Get Status", test_get_status()))
    results.append(("Missing Auth", test_no_auth()))
    results.append(("Invalid Token", test_invalid_token()))
    
    print("=" * 60)
    print("SUMMARY")
    print("=" * 60)
    for test_name, passed in results:
        status = "✓ PASS" if passed else "✗ FAIL"
        print(f"{status}: {test_name}")
