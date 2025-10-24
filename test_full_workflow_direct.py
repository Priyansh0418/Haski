#!/usr/bin/env python3
"""
Complete end-to-end workflow test for SkinHairAI API (using TestClient)
Tests: User signup → Login → Image upload → ML analysis → Response validation

This version uses FastAPI's TestClient for direct testing without needing a running server.
"""

from fastapi.testclient import TestClient
from backend.app.main import app
import json
from pathlib import Path
from datetime import datetime

# Test configuration
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

# Initialize test client
client = TestClient(app)


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
        response = client.get("/api/v1/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API is healthy")
            print(f"  {json.dumps(data, indent=2)}")
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
    
    try:
        response = client.post("/api/v1/auth/signup", json=payload)
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"User created successfully")
            print(f"  Response: {json.dumps(data, indent=2)}")
            return True
        elif response.status_code == 409:
            print_info(f"User already exists - trying to use existing account")
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
        "password": TEST_PASSWORD,
        "email": TEST_EMAIL
    }
    
    print_info(f"Logging in as: {TEST_USERNAME}")
    
    try:
        response = client.post("/api/v1/auth/login", json=payload)
        
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
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    try:
        with open(TEST_IMAGE_PATH, 'rb') as f:
            files = {'file': ('test_image.jpg', f, 'image/jpeg')}
            
            response = client.post(
                "/api/v1/analyze/photo",
                files=files,
                headers=headers
            )
        
        if response.status_code in [200, 201]:
            data = response.json()
            print_success(f"Analysis completed successfully!")
            print(f"\n  {BLUE}Analysis Results:{RESET}")
            print(f"    Class ID: {data.get('class_id')}")
            print(f"    Class Name: {data.get('class_name')}")
            confidence = data.get('confidence', 0)
            if isinstance(confidence, (int, float)):
                print(f"    Confidence: {confidence:.2%}")
            else:
                print(f"    Confidence: {confidence}")
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
        import traceback
        traceback.print_exc()
        return False


def test_get_profile(token):
    """Test 5: Get user profile"""
    print_section("TEST 5: Get User Profile")
    
    headers = {
        "Authorization": f"Bearer {token}"
    }
    
    # First, create the profile if it doesn't exist
    print_info("Creating profile...")
    profile_data = {
        "age": 25,
        "gender": "other",
        "skin_type": "normal",
        "hair_type": "straight"
    }
    
    try:
        create_response = client.post(
            "/api/v1/profile/create",
            json=profile_data,
            headers=headers
        )
        
        if create_response.status_code in [200, 201]:
            print_success(f"Profile created")
        else:
            print_info(f"Profile creation returned: {create_response.status_code}")
    except Exception as e:
        print_info(f"Profile creation (not critical): {e}")
    
    # Now get the profile
    try:
        response = client.get(
            "/api/v1/profile/me",
            headers=headers
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
    print("║" + "(Using TestClient - No Server Needed)".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    print(f"{RESET}\n")
    
    # Run test sequence
    results = []
    
    # Test 1: Health check
    results.append(("Health Check", test_health_check()))
    
    # Test 2: Signup
    results.append(("User Signup", test_user_signup()))
    
    # Test 3: Login
    token = test_user_login()
    results.append(("User Login", token is not None))
    
    if token:
        # Test 4: Image upload & analysis
        results.append(("Image Upload & Analysis", test_image_upload_and_analysis(token)))
        
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
