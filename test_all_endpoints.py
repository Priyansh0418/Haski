#!/usr/bin/env python3
"""
Haski Project - Complete API Endpoint Test Suite
Tests all endpoints for functionality and integration

Usage:
    python api_endpoints_test.py
    
Prerequisites:
    - Backend running on localhost:8000
    - Frontend running on localhost:5173 (optional for UI testing)
"""

import requests
import json
import time
from pathlib import Path
from typing import Dict, Any, Optional

# Configuration
API_BASE_URL = "http://localhost:8000"
API_V1_PREFIX = f"{API_BASE_URL}/api/v1"

# Test data
TEST_USER = {
    "username": f"test_user_{int(time.time())}",
    "email": f"test_{int(time.time())}@example.com",
    "password": "TestPassword123!@#"
}

# Color output
class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    RESET = '\033[0m'
    BOLD = '\033[1m'

def print_section(title: str):
    """Print section header"""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{title:^70}{Colors.RESET}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*70}{Colors.RESET}\n")

def print_success(message: str):
    """Print success message"""
    print(f"{Colors.GREEN}✓ {message}{Colors.RESET}")

def print_error(message: str):
    """Print error message"""
    print(f"{Colors.RED}✗ {message}{Colors.RESET}")

def print_info(message: str):
    """Print info message"""
    print(f"{Colors.BLUE}ℹ {message}{Colors.RESET}")

def print_test(test_name: str):
    """Print test header"""
    print(f"\n{Colors.BOLD}{test_name}{Colors.RESET}")

# ============================================================================
# TESTS
# ============================================================================

def test_health_check():
    """Test 1: Health check endpoint"""
    print_test("TEST 1: Health Check")
    
    try:
        response = requests.get(f"{API_BASE_URL}/")
        if response.status_code == 200:
            data = response.json()
            print_success(f"Root health check: {data}")
            return True
        else:
            print_error(f"Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Connection error: {e}")
        return False

def test_api_v1_health():
    """Test 2: API v1 health check"""
    print_test("TEST 2: API v1 Health Check")
    
    try:
        response = requests.get(f"{API_V1_PREFIX}/health")
        if response.status_code == 200:
            data = response.json()
            print_success(f"API v1 health: {data}")
            return True
        else:
            print_error(f"API v1 health check failed: {response.status_code}")
            return False
    except Exception as e:
        print_error(f"Error: {e}")
        return False

def test_signup():
    """Test 3: User signup"""
    print_test("TEST 3: User Signup")
    
    try:
        payload = {
            "username": TEST_USER["username"],
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        print_info(f"Signup with: {TEST_USER['username']} / {TEST_USER['email']}")
        
        response = requests.post(f"{API_V1_PREFIX}/auth/signup", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_success(f"Signup successful")
                print_info(f"Token: {token[:50]}...")
                return True, token
            else:
                print_error("No token in response")
                return False, None
        else:
            print_error(f"Signup failed: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Error: {e}")
        return False, None

def test_login(token_from_signup):
    """Test 4: User login"""
    print_test("TEST 4: User Login")
    
    try:
        payload = {
            "email": TEST_USER["email"],
            "password": TEST_USER["password"]
        }
        
        print_info(f"Login with: {TEST_USER['email']}")
        
        response = requests.post(f"{API_V1_PREFIX}/auth/login", json=payload)
        
        if response.status_code == 200:
            data = response.json()
            token = data.get("access_token")
            if token:
                print_success(f"Login successful")
                # Verify it's the same token
                if token == token_from_signup:
                    print_success("Token matches signup token")
                else:
                    print_info("Token differs from signup (expected for new session)")
                return True, token
            else:
                print_error("No token in response")
                return False, None
        else:
            print_error(f"Login failed: {response.status_code} - {response.text}")
            return False, None
    except Exception as e:
        print_error(f"Error: {e}")
        return False, None

def test_profile_endpoints(token: str):
    """Test 5: Profile endpoints"""
    print_test("TEST 5: Profile Endpoints")
    
    results = []
    
    # Create profile
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "birth_year": 1996,
            "gender": "female",
            "location": "New York",
            "allergies": "pollen",
            "lifestyle": "active",
            "skin_type": "combination",
            "hair_type": "straight"
        }
        
        print_info("Creating profile...")
        response = requests.post(f"{API_V1_PREFIX}/profile/", json=payload, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            profile_id = data.get("id")
            print_success(f"Profile created: {profile_id}")
            results.append(("Create Profile", True))
        else:
            print_error(f"Profile creation failed: {response.status_code} - {response.text}")
            results.append(("Create Profile", False))
    except Exception as e:
        print_error(f"Error creating profile: {e}")
        results.append(("Create Profile", False))
    
    # Get profile
    try:
        headers = {"Authorization": f"Bearer {token}"}
        
        print_info("Getting profile...")
        response = requests.get(f"{API_V1_PREFIX}/profile/me", headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            print_success(f"Profile retrieved: Age={data.get('age')}, Gender={data.get('gender')}")
            results.append(("Get Profile", True))
        else:
            print_error(f"Get profile failed: {response.status_code}")
            results.append(("Get Profile", False))
    except Exception as e:
        print_error(f"Error getting profile: {e}")
        results.append(("Get Profile", False))
    
    # Update profile
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "age": 29,
            "location": "San Francisco"
        }
        
        print_info("Updating profile...")
        response = requests.put(f"{API_V1_PREFIX}/profile/", json=payload, headers=headers)
        
        if response.status_code == 200:
            print_success("Profile updated")
            results.append(("Update Profile", True))
        else:
            print_error(f"Update profile failed: {response.status_code}")
            results.append(("Update Profile", False))
    except Exception as e:
        print_error(f"Error updating profile: {e}")
        results.append(("Update Profile", False))
    
    return results

def test_image_analysis(token: Optional[str] = None):
    """Test 6: Image analysis endpoint"""
    print_test("TEST 6: Image Analysis Endpoint")
    
    # Check if test image exists
    test_image_path = Path("test_image.jpg")
    if not test_image_path.exists():
        print_info("Creating test image...")
        # Create a simple test image using PIL if available
        try:
            from PIL import Image
            img = Image.new('RGB', (100, 100), color=(73, 109, 137))
            img.save(test_image_path)
            print_success(f"Test image created: {test_image_path}")
        except ImportError:
            print_error("PIL not available, cannot create test image")
            return [("Image Analysis", False)]
    
    try:
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"
        
        print_info("Uploading image for analysis...")
        
        with open(test_image_path, 'rb') as f:
            files = {'image': f}
            response = requests.post(
                f"{API_V1_PREFIX}/analyze/image",
                files=files,
                headers=headers
            )
        
        if response.status_code == 201:
            data = response.json()
            print_success(f"Analysis successful")
            print_info(f"  - Skin Type: {data.get('skin_type')}")
            print_info(f"  - Hair Type: {data.get('hair_type')}")
            print_info(f"  - Conditions: {data.get('conditions_detected')}")
            print_info(f"  - Model: {data.get('model_version')}")
            return [("Image Analysis", True)]
        else:
            print_error(f"Analysis failed: {response.status_code} - {response.text}")
            return [("Image Analysis", False)]
    except Exception as e:
        print_error(f"Error: {e}")
        return [("Image Analysis", False)]

def test_recommendations_endpoint(token: str):
    """Test 7: Recommendations endpoint"""
    print_test("TEST 7: Recommendations Endpoint")
    
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "analysis": {
                "skin_type": "oily",
                "hair_type": "wavy",
                "conditions": ["acne"]
            },
            "profile": {
                "age": 28,
                "gender": "female",
                "allergies": []
            }
        }
        
        print_info("Generating recommendations...")
        response = requests.post(
            f"{API_V1_PREFIX}/recommend/recommend",
            json=payload,
            headers=headers
        )
        
        if response.status_code == 201:
            data = response.json()
            print_success("Recommendations generated")
            print_info(f"  - Recommendation ID: {data.get('recommendation_id')}")
            print_info(f"  - Applied Rules: {len(data.get('applied_rules', []))} rules")
            print_info(f"  - Products: {len(data.get('products', []))} recommended")
            print_info(f"  - Escalation Level: {data.get('escalation', {}).get('level')}")
            return [("Recommendations", True)]
        else:
            print_error(f"Recommendations failed: {response.status_code} - {response.text}")
            return [("Recommendations", False)]
    except Exception as e:
        print_error(f"Error: {e}")
        return [("Recommendations", False)]

def test_feedback_endpoints(token: str):
    """Test 8: Feedback endpoints"""
    print_test("TEST 8: Feedback Endpoints")
    
    # First, get a recommendation to leave feedback on
    try:
        headers = {"Authorization": f"Bearer {token}"}
        payload = {
            "analysis": {
                "skin_type": "oily",
                "hair_type": "wavy",
                "conditions": []
            }
        }
        
        response = requests.post(
            f"{API_V1_PREFIX}/recommend/recommend",
            json=payload,
            headers=headers
        )
        
        if response.status_code != 201:
            print_error("Could not create recommendation for feedback test")
            return [("Submit Feedback", False)]
        
        rec_id = response.json().get("recommendation_id")
        
        # Submit feedback
        print_info(f"Submitting feedback on recommendation {rec_id}...")
        
        feedback_payload = {
            "recommendation_id": rec_id,
            "rating": 4,
            "helpful": True,
            "comment": "Great recommendations!",
            "improvement_areas": ["More specific instructions"]
        }
        
        response = requests.post(
            f"{API_V1_PREFIX}/feedback/submit",
            json=feedback_payload,
            headers=headers
        )
        
        if response.status_code == 201:
            print_success("Feedback submitted")
            return [("Submit Feedback", True)]
        else:
            print_error(f"Feedback submission failed: {response.status_code}")
            return [("Submit Feedback", False)]
    
    except Exception as e:
        print_error(f"Error: {e}")
        return [("Submit Feedback", False)]

# ============================================================================
# MAIN
# ============================================================================

def main():
    """Run all tests"""
    print_section("HASKI PROJECT - API ENDPOINT TEST SUITE")
    
    print_info(f"API Base URL: {API_BASE_URL}")
    print_info(f"Test started at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")
    
    results = []
    
    # Test 1: Health checks
    if test_health_check():
        results.append(("Health Check (Root)", True))
    else:
        results.append(("Health Check (Root)", False))
    
    if test_api_v1_health():
        results.append(("Health Check (API v1)", True))
    else:
        results.append(("Health Check (API v1)", False))
        print_error("Cannot proceed without API health check")
        print_section("TEST SUMMARY")
        print_results(results)
        return
    
    # Test 2: Authentication
    signup_success, token = test_signup()
    results.append(("User Signup", signup_success))
    
    if not token:
        print_section("TEST SUMMARY")
        print_results(results)
        return
    
    login_success, _ = test_login(token)
    results.append(("User Login", login_success))
    
    # Test 3: Profile
    profile_results = test_profile_endpoints(token)
    results.extend(profile_results)
    
    # Test 4: Image Analysis
    analysis_results = test_image_analysis(token)
    results.extend(analysis_results)
    
    # Test 5: Recommendations
    rec_results = test_recommendations_endpoint(token)
    results.extend(rec_results)
    
    # Test 6: Feedback
    feedback_results = test_feedback_endpoints(token)
    results.extend(feedback_results)
    
    # Print summary
    print_section("TEST SUMMARY")
    print_results(results)

def print_results(results):
    """Print test results summary"""
    total = len(results)
    passed = sum(1 for _, success in results if success)
    failed = total - passed
    
    print(f"\n{Colors.BOLD}Results:{Colors.RESET}")
    for test_name, success in results:
        status = f"{Colors.GREEN}PASS{Colors.RESET}" if success else f"{Colors.RED}FAIL{Colors.RESET}"
        print(f"  {status} - {test_name}")
    
    print(f"\n{Colors.BOLD}Summary:{Colors.RESET}")
    print(f"  Total: {total}")
    print(f"  {Colors.GREEN}Passed: {passed}{Colors.RESET}")
    print(f"  {Colors.RED}Failed: {failed}{Colors.RESET}")
    
    if failed == 0:
        print(f"\n{Colors.GREEN}{Colors.BOLD}✓ ALL TESTS PASSED{Colors.RESET}")
    else:
        print(f"\n{Colors.RED}{Colors.BOLD}✗ SOME TESTS FAILED{Colors.RESET}")
    
    print(f"\nTest completed at: {time.strftime('%Y-%m-%d %H:%M:%S')}\n")

if __name__ == "__main__":
    main()
