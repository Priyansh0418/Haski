#!/bin/bash

# Haski Recommender System - API Testing Script
# ================================================
# This script tests all endpoints with curl examples
# Usage: ./test_api.sh [TOKEN] [ADMIN_TOKEN]

set -e

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
BASE_URL="${BASE_URL:-http://localhost:8000}"
TOKEN="${1:-}"
ADMIN_TOKEN="${2:-}"

# Banner
echo "╔════════════════════════════════════════════════════════════════╗"
echo "║        Haski Recommender System - API Testing Suite            ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""

# Check tokens
if [ -z "$TOKEN" ]; then
    echo -e "${YELLOW}⚠ No user token provided${NC}"
    echo "Usage: $0 <USER_TOKEN> [ADMIN_TOKEN]"
    echo ""
    echo "To get tokens:"
    echo "1. Start the backend: cd backend && uvicorn app.main:app --reload"
    echo "2. Login to get JWT token"
    echo ""
    exit 1
fi

echo -e "${GREEN}✓ User token provided${NC}"
if [ -z "$ADMIN_TOKEN" ]; then
    ADMIN_TOKEN=$TOKEN
    echo -e "${YELLOW}⚠ No admin token provided, using user token${NC}"
else
    echo -e "${GREEN}✓ Admin token provided${NC}"
fi

echo "Base URL: $BASE_URL"
echo ""

# Test counter
TESTS_PASSED=0
TESTS_FAILED=0

# Helper function
test_endpoint() {
    local name="$1"
    local method="$2"
    local endpoint="$3"
    local data="$4"
    local token="$5"
    
    echo "────────────────────────────────────────────────────────────────"
    echo "TEST: $name"
    echo "────────────────────────────────────────────────────────────────"
    echo -e "${YELLOW}Request:${NC}"
    echo "$method $endpoint"
    
    if [ -n "$data" ]; then
        echo "Body:"
        echo "$data" | jq '.' 2>/dev/null || echo "$data"
    fi
    
    echo ""
    echo -e "${YELLOW}Response:${NC}"
    
    if [ "$method" = "GET" ]; then
        RESPONSE=$(curl -s -X GET "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json")
    else
        RESPONSE=$(curl -s -X $method "$BASE_URL$endpoint" \
            -H "Authorization: Bearer $token" \
            -H "Content-Type: application/json" \
            -d "$data")
    fi
    
    # Pretty print response
    if echo "$RESPONSE" | jq '.' 2>/dev/null >/dev/null; then
        echo "$RESPONSE" | jq '.'
    else
        echo "$RESPONSE"
    fi
    
    # Check for error
    if echo "$RESPONSE" | jq -e '.detail' >/dev/null 2>&1; then
        ERROR_MSG=$(echo "$RESPONSE" | jq -r '.detail')
        echo -e "${RED}✗ FAILED: $ERROR_MSG${NC}"
        ((TESTS_FAILED++))
    else
        echo -e "${GREEN}✓ PASSED${NC}"
        ((TESTS_PASSED++))
    fi
    
    echo ""
    echo "$RESPONSE"
}

# ===== TEST 1: Generate Recommendation =====

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo "TEST SUITE 1: RECOMMENDATION ENDPOINT"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

RECOMMEND_DATA='{
  "method": "direct_analysis",
  "skin_type": "oily",
  "hair_type": "wavy",
  "conditions_detected": ["acne", "oily_skin"],
  "confidence_scores": {"acne": 0.87, "oily_skin": 0.92},
  "age": 28,
  "gender": "F",
  "skin_sensitivity": "normal",
  "include_skincare": true,
  "include_diet": true,
  "include_products": true
}'

echo "Generating recommendation..."
REC_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/recommend" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json" \
    -d "$RECOMMEND_DATA")

echo "$REC_RESPONSE" | jq '.'

# Extract recommendation_id
REC_ID=$(echo "$REC_RESPONSE" | jq -r '.recommendation_id // empty')

if [ -z "$REC_ID" ]; then
    echo -e "${RED}✗ FAILED: Could not extract recommendation_id${NC}"
    ((TESTS_FAILED++))
else
    echo -e "${GREEN}✓ Recommendation ID: $REC_ID${NC}"
    ((TESTS_PASSED++))
    
    # Verify response structure
    echo ""
    echo "Checking response structure..."
    
    ROUTINES=$(echo "$REC_RESPONSE" | jq '.routines | length')
    PRODUCTS=$(echo "$REC_RESPONSE" | jq '.products | length')
    RULES=$(echo "$REC_RESPONSE" | jq '.applied_rules | length')
    
    if [ "$ROUTINES" -gt 0 ]; then
        echo -e "${GREEN}✓ Routines: $ROUTINES${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ No routines found${NC}"
        ((TESTS_FAILED++))
    fi
    
    if [ "$PRODUCTS" -gt 0 ]; then
        echo -e "${GREEN}✓ Products: $PRODUCTS${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ No products found${NC}"
        ((TESTS_FAILED++))
    fi
    
    if [ "$RULES" -gt 0 ]; then
        echo -e "${GREEN}✓ Applied Rules: $RULES${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ No rules found${NC}"
        ((TESTS_FAILED++))
    fi
fi

echo ""

# ===== TEST 2: Submit Feedback =====

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo "TEST SUITE 2: FEEDBACK ENDPOINT"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

if [ -n "$REC_ID" ]; then
    FEEDBACK_DATA="{
      \"recommendation_id\": \"$REC_ID\",
      \"helpful_rating\": 4,
      \"product_satisfaction\": 4,
      \"routine_completion_pct\": 80,
      \"would_recommend\": true,
      \"timeframe\": \"2_weeks\",
      \"feedback_text\": \"Great recommendations!\"
    }"
    
    echo "Submitting feedback..."
    FEEDBACK_RESPONSE=$(curl -s -X POST "$BASE_URL/api/v1/feedback" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json" \
        -d "$FEEDBACK_DATA")
    
    echo "$FEEDBACK_RESPONSE" | jq '.'
    
    if echo "$FEEDBACK_RESPONSE" | jq -e '.feedback_id' >/dev/null 2>&1; then
        echo -e "${GREEN}✓ Feedback submitted${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ Feedback submission failed${NC}"
        ((TESTS_FAILED++))
    fi
    
    echo ""
    
    # ===== TEST 3: Get Feedback Stats =====
    
    echo "Getting feedback stats..."
    STATS_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/feedback/$REC_ID/stats" \
        -H "Authorization: Bearer $TOKEN" \
        -H "Content-Type: application/json")
    
    echo "$STATS_RESPONSE" | jq '.'
    
    if echo "$STATS_RESPONSE" | jq -e '.avg_helpful_rating' >/dev/null 2>&1; then
        AVG_RATING=$(echo "$STATS_RESPONSE" | jq -r '.avg_helpful_rating')
        echo -e "${GREEN}✓ Average rating: $AVG_RATING${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ Stats retrieval failed${NC}"
        ((TESTS_FAILED++))
    fi
fi

echo ""

# ===== TEST 4: Search Products =====

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo "TEST SUITE 3: PRODUCTS ENDPOINT"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Searching products by tag (acne)..."
SEARCH_RESPONSE=$(curl -s -X GET "$BASE_URL/api/v1/products/search?tag=acne" \
    -H "Authorization: Bearer $TOKEN" \
    -H "Content-Type: application/json")

echo "$SEARCH_RESPONSE" | jq '.'

if echo "$SEARCH_RESPONSE" | jq -e '.count' >/dev/null 2>&1; then
    COUNT=$(echo "$SEARCH_RESPONSE" | jq -r '.count')
    if [ "$COUNT" -gt 0 ]; then
        echo -e "${GREEN}✓ Found $COUNT products${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${YELLOW}⚠ No products found (this is OK if database is empty)${NC}"
    fi
else
    echo -e "${RED}✗ Product search failed${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# ===== TEST 5: Admin Endpoint =====

echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo "TEST SUITE 4: ADMIN ENDPOINTS"
echo -e "${YELLOW}═══════════════════════════════════════════════════════════════${NC}"
echo ""

echo "Reloading rules..."
RELOAD_RESPONSE=$(curl -s -X POST "$BASE_URL/admin/reload-rules" \
    -H "Authorization: Bearer $ADMIN_TOKEN" \
    -H "Content-Type: application/json" \
    -d '{}')

echo "$RELOAD_RESPONSE" | jq '.'

if echo "$RELOAD_RESPONSE" | jq -e '.status' >/dev/null 2>&1; then
    STATUS=$(echo "$RELOAD_RESPONSE" | jq -r '.status')
    if [ "$STATUS" = "success" ]; then
        RULES_COUNT=$(echo "$RELOAD_RESPONSE" | jq -r '.rules_loaded')
        echo -e "${GREEN}✓ Rules reloaded: $RULES_COUNT rules${NC}"
        ((TESTS_PASSED++))
    else
        echo -e "${RED}✗ Rule reload failed${NC}"
        ((TESTS_FAILED++))
    fi
else
    echo -e "${RED}✗ Admin endpoint error${NC}"
    ((TESTS_FAILED++))
fi

echo ""

# ===== SUMMARY =====

echo "╔════════════════════════════════════════════════════════════════╗"
echo "║                      TEST SUMMARY                              ║"
echo "╚════════════════════════════════════════════════════════════════╝"
echo ""
echo -e "Tests Passed: ${GREEN}$TESTS_PASSED${NC}"
echo -e "Tests Failed: ${RED}$TESTS_FAILED${NC}"
echo ""

if [ $TESTS_FAILED -eq 0 ]; then
    echo -e "${GREEN}✓ ALL TESTS PASSED!${NC}"
    exit 0
else
    echo -e "${RED}✗ SOME TESTS FAILED${NC}"
    exit 1
fi
