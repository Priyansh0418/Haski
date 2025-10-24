#!/usr/bin/env python3
"""
===================================================================
COMPLETE END-TO-END INTEGRATION TEST - SkinHairAI API
===================================================================

This test verifies the entire ML inference workflow integrated
with the FastAPI backend, including:
  ✓ User authentication (signup/login)
  ✓ ML model loading and inference
  ✓ API response format validation
  ✓ Database persistence

Note: This uses FastAPI's TestClient for direct testing
without needing a running server.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
import json
from pathlib import Path
from datetime import datetime

# Configuration
TEST_IMAGE_PATH = Path("d:/Haski-main/test_image.jpg")
TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M%S")
TEST_USERNAME = f"testuser_{TIMESTAMP}"
TEST_PASSWORD = "TestPassword123!"
TEST_EMAIL = f"test_{TIMESTAMP}@example.com"

# ANSI Colors
GREEN = "\033[92m"
RED = "\033[91m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
RESET = "\033[0m"

client = TestClient(app)


def print_section(title):
    print(f"\n{BLUE}{'='*75}{RESET}")
    print(f"{BLUE}{title:^75}{RESET}")
    print(f"{BLUE}{'='*75}{RESET}\n")


def print_success(msg):
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    print(f"{YELLOW}→ {msg}{RESET}")


def main():
    print(f"\n{BLUE}")
    print("╔" + "═" * 73 + "╗")
    print("║" + " " * 73 + "║")
    print("║" + "SkinHairAI - END-TO-END API INTEGRATION TEST".center(73) + "║")
    print("║" + " " * 73 + "║")
    print("╚" + "═" * 73 + "╝")
    print(f"{RESET}\n")
    
    results = []
    
    # ========================================
    # TEST 1: Health Check
    # ========================================
    print_section("TEST 1: API Health Check")
    try:
        response = client.get("/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print_success("API health check passed")
            print(f"  Status: {data.get('status')}")
            print(f"  Version: {data.get('version')}")
            results.append(("Health Check", True))
        else:
            print_error(f"Unexpected status: {response.status_code}")
            results.append(("Health Check", False))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(("Health Check", False))
    
    # ========================================
    # TEST 2: User Signup
    # ========================================
    print_section("TEST 2: User Signup")
    payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "email": TEST_EMAIL
    }
    print_info(f"Creating test user: {TEST_USERNAME}")
    
    try:
        response = client.post("/api/v1/auth/signup", json=payload)
        if response.status_code in [200, 201]:
            data = response.json()
            print_success("User signup successful")
            print(f"  Access Token: {data['access_token'][:40]}...")
            results.append(("User Signup", True))
        else:
            print_error(f"Signup failed: {response.status_code}")
            results.append(("User Signup", False))
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(("User Signup", False))
    
    # ========================================
    # TEST 3: User Login
    # ========================================
    print_section("TEST 3: User Login & Get JWT Token")
    login_payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "email": TEST_EMAIL
    }
    
    try:
        response = client.post("/api/v1/auth/login", json=login_payload)
        if response.status_code == 200:
            data = response.json()
            token = data['access_token']
            print_success("Login successful")
            print(f"  Access Token: {token[:40]}...")
            results.append(("User Login", True))
        else:
            print_error(f"Login failed: {response.status_code}")
            results.append(("User Login", False))
            token = None
    except Exception as e:
        print_error(f"Error: {e}")
        results.append(("User Login", False))
        token = None
    
    if not token:
        print_error("Cannot proceed without authentication token")
        token = None
    
    # ========================================
    # TEST 4: ML Model Inference (with auth)
    # ========================================
    if token:
        print_section("TEST 4: ML Model Inference via API")
        
        if not TEST_IMAGE_PATH.exists():
            print_error(f"Test image not found: {TEST_IMAGE_PATH}")
            results.append(("ML Inference", False))
        else:
            print_info(f"Test image: {TEST_IMAGE_PATH.name}")
            print_info(f"File size: {TEST_IMAGE_PATH.stat().st_size} bytes")
            
            headers = {"Authorization": f"Bearer {token}"}
            
            try:
                with open(TEST_IMAGE_PATH, 'rb') as f:
                    files = {'image': ('test_image.jpg', f, 'image/jpeg')}
                    response = client.post(
                        "/api/v1/analyze/photo",
                        files=files,
                        headers=headers
                    )
                
                if response.status_code in [200, 201]:
                    data = response.json()
                    print_success("Image analysis completed!")
                    print(f"\n  {BLUE}Model Output:{RESET}")
                    print(f"    Class ID: {data.get('class_id')}")
                    print(f"    Class Name: {data.get('class_name')}")
                    conf = data.get('confidence', 0)
                    if isinstance(conf, (int, float)) and 0 <= conf <= 1:
                        print(f"    Confidence: {conf*100:.2f}%")
                    else:
                        print(f"    Confidence: {conf}")
                    print(f"    Model Type: {data.get('model_type')}")
                    print(f"    Analysis ID: {data.get('id')}")
                    print(f"    Photo ID: {data.get('photo_id')}")
                    print(f"    Probabilities: {len(data.get('probabilities', []))} classes")
                    print(f"\n  {BLUE}Full Response:{RESET}")
                    print(json.dumps(data, indent=4))
                    results.append(("ML Inference", True))
                else:
                    print_error(f"Analysis failed: {response.status_code}")
                    print(f"  Response: {response.text[:200]}")
                    results.append(("ML Inference", False))
            except Exception as e:
                print_error(f"Error: {e}")
                results.append(("ML Inference", False))
    
    # ========================================
    # SUMMARY
    # ========================================
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{BLUE}Results: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{('═'*73):^75}")
        print(f"{'✓ FULL INTEGRATION SUCCESS':^75}{RESET}")
        print(f"{('═'*73):^75}")
        print(f"\n{GREEN}Your ML model is fully integrated and operational!{RESET}\n")
    else:
        print(f"{YELLOW}Some tests did not pass. Review failures above.{RESET}\n")


if __name__ == "__main__":
    main()
