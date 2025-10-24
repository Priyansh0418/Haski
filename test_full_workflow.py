#!/usr/bin/env python3
"""
Complete end-to-end workflow test for SkinHairAI API
Tests: User signup → Login → Image upload → ML analysis → Response validation
"""

import requests
import json
import time
from pathlib import Path
from datetime import datetime

# Configuration
API_BASE_URL = "http://127.0.0.1:8000/api/v1"
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


def print_section(title):
    """Print a formatted section header"""
    print(f"\n{BLUE}{'='*70}")
    print(f"{title:^70}")
    print(f"{'='*70}{RESET}\n")


def print_success(msg):
    """Print success message"""
    print(f"{GREEN}✓ {msg}{RESET}")


def print_error(msg):
    """Print error message"""
    print(f"{RED}✗ {msg}{RESET}")


def print_info(msg):
    """Print info message"""
    print(f"{YELLOW}→ {msg}{RESET}")


def test_health_check():
    """Test 1: Health check endpoint"""
    print_section("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Unexpected status code: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Health check failed: {e}")
        return False


def test_user_signup():
    """Test 2: User signup"""
    print_section("TEST 2: User Signup")
    
    payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD,
        "email": TEST_EMAIL
    }
    
    print_info(f"Creating user: {TEST_USERNAME}")
    print_info(f"Endpoint: POST /auth/signup")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/signup",
            json=payload,
            timeout=5
        )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"User created successfully")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return True
        elif response.status_code == 409:
            print_info(f"User already exists (conflict) - this is ok")
            return True
        else:
            print_error(f"Signup failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Signup request failed: {e}")
        return False


def test_user_login():
    """Test 3: User login and get JWT token"""
    print_section("TEST 3: User Login (Get JWT Token)")
    
    payload = {
        "username": TEST_USERNAME,
        "password": TEST_PASSWORD
    }
    
    print_info(f"Logging in as: {TEST_USERNAME}")
    print_info(f"Endpoint: POST /auth/login")
    
    try:
        response = requests.post(
            f"{API_BASE_URL}/auth/login",
            json=payload,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            access_token = data.get("access_token")
            if access_token:
                print_success(f"Login successful! Token obtained")
                print(f"  Token: {access_token[:50]}...")
                return access_token
            else:
                print_error(f"No access token in response")
                print(f"  Response: {json.dumps(data, indent=2)}")
                return None
        else:
            print_error(f"Login failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return None
    except Exception as e:
        print_error(f"Login request failed: {e}")
        return None


def test_image_upload_and_analysis(token):
    """Test 4: Upload image and get ML analysis"""
    print_section("TEST 4: Upload Image & ML Analysis")
    
    if not TEST_IMAGE_PATH.exists():
        print_error(f"Test image not found at: {TEST_IMAGE_PATH}")
        return False
    
    print_info(f"Image file: {TEST_IMAGE_PATH}")
    print_info(f"File size: {TEST_IMAGE_PATH.stat().st_size} bytes")
    print_info(f"Endpoint: POST /analyze/photo")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': (TEST_IMAGE_PATH.name, f, 'image/jpeg')}
            
            response = requests.post(
                f"{API_BASE_URL}/analyze/photo",
                files=files,
                headers=headers,
                timeout=30  # ML analysis might take a bit
            )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Analysis completed successfully!")
            print(f"\n  {BLUE}Analysis Results:{RESET}")
            print(f"    Class ID: {data.get('class_id')}")
            print(f"    Class Name: {data.get('class_name')}")
            print(f"    Confidence: {data.get('confidence'):.2%}")
            print(f"    Model Type: {data.get('model_type')}")
            print(f"    Analysis ID: {data.get('id')}")
            print(f"    Photo ID: {data.get('photo_id')}")
            print(f"\n  Full Response:\n{json.dumps(data, indent=4)}")
            return True
        else:
            print_error(f"Analysis failed: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Analysis request failed: {e}")
        return False


def test_get_profile(token):
    """Test 5: Get user profile"""
    print_section("TEST 5: Get User Profile")
    
    print_info(f"Endpoint: GET /profile/me")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        response = requests.get(
            f"{API_BASE_URL}/profile/me",
            headers=headers,
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Profile retrieved successfully")
            print(f"  Profile: {json.dumps(data, indent=2)}")
            return True
        else:
            print_error(f"Failed to get profile: {response.status_code}")
            print(f"  Response: {response.text}")
            return False
    except Exception as e:
        print_error(f"Profile request failed: {e}")
        return False


def main():
    """Run all tests"""
    print(f"\n{BLUE}")
    print("╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "SkinHairAI API - END-TO-END WORKFLOW TEST".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}\n")
    
    # Check if server is running
    print_info("Checking if API server is running...")
    try:
        response = requests.get(f"{API_BASE_URL}/health", timeout=2)
        if response.status_code == 200:
            print_success("API server is running and responsive!")
        else:
            print_error("API server returned unexpected status")
    except requests.exceptions.ConnectionError:
        print_error(f"Cannot connect to API at {API_BASE_URL}")
        print_error("Please start the server with: python -m uvicorn backend.app.main:app --port 8000")
        return
    except Exception as e:
        print_error(f"Connection check failed: {e}")
        return
    
    # Run test sequence
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    time.sleep(0.5)
    
    # Test 2: Signup
    results.append(("User Signup", test_user_signup()))
    time.sleep(0.5)
    
    # Test 3: Login
    token = test_user_login()
    results.append(("User Login", token is not None))
    time.sleep(0.5)
    
    if token:
        # Test 4: Image upload & analysis
        results.append(("Image Upload & Analysis", test_image_upload_and_analysis(token)))
        time.sleep(0.5)
        
        # Test 5: Get profile
        results.append(("Get User Profile", test_get_profile(token)))
    
    # Print summary
    print_section("TEST SUMMARY")
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = f"{GREEN}PASS{RESET}" if result else f"{RED}FAIL{RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{BLUE}Total: {passed}/{total} tests passed{RESET}\n")
    
    if passed == total:
        print(f"{GREEN}{'✓ All tests passed! API integration is working correctly!':^70}{RESET}\n")
    else:
        print(f"{RED}{'✗ Some tests failed. Check the output above for details.':^70}{RESET}\n")


if __name__ == "__main__":
    main()
