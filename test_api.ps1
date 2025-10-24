# Haski Recommender System - API Testing Script (PowerShell)
# ===========================================================
# This script tests all endpoints with curl/Invoke-WebRequest
# Usage: .\test_api.ps1 -Token "YOUR_JWT_TOKEN" -AdminToken "ADMIN_JWT_TOKEN"

param(
    [string]$Token = "",
    [string]$AdminToken = "",
    [string]$BaseUrl = "http://localhost:8000"
)

# Colors
$Success = "Green"
$Error = "Red"
$Warning = "Yellow"

# Test counters
$TestsPassed = 0
$TestsFailed = 0

# Helper function to print headers
function Print-Header {
    param([string]$Title)
    Write-Host ""
    Write-Host ("╔" + "═" * 66 + "╗") -ForegroundColor Cyan
    Write-Host ("║ " + $Title.PadRight(64) + " ║") -ForegroundColor Cyan
    Write-Host ("╚" + "═" * 66 + "╝") -ForegroundColor Cyan
    Write-Host ""
}

function Print-Test {
    param([string]$Name)
    Write-Host "────────────────────────────────────────────────────────────────"
    Write-Host "TEST: $Name" -ForegroundColor Yellow
    Write-Host "────────────────────────────────────────────────────────────────"
}

function Print-Success {
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Print-Failed {
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Print-Warning {
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Banner
Print-Header "Haski Recommender System - API Testing Suite"

# Check tokens
if ([string]::IsNullOrEmpty($Token)) {
    Print-Warning "No user token provided"
    Write-Host "Usage: .\test_api.ps1 -Token `"YOUR_JWT_TOKEN`" -AdminToken `"ADMIN_JWT_TOKEN`""
    Write-Host ""
    Write-Host "To get tokens:"
    Write-Host "1. Start the backend: cd backend; python -m uvicorn app.main:app --reload"
    Write-Host "2. Login to get JWT token"
    Write-Host ""
    exit 1
}

Print-Success "User token provided"
if ([string]::IsNullOrEmpty($AdminToken)) {
    $AdminToken = $Token
    Print-Warning "No admin token provided, using user token"
}
else {
    Print-Success "Admin token provided"
}

Write-Host "Base URL: $BaseUrl"
Write-Host ""

# ===== TEST 1: Generate Recommendation =====

Print-Header "TEST SUITE 1: RECOMMENDATION ENDPOINT"

Print-Test "POST /api/v1/recommend (Direct Analysis)"

$RecommendData = @{
    method = "direct_analysis"
    skin_type = "oily"
    hair_type = "wavy"
    conditions_detected = @("acne", "oily_skin")
    confidence_scores = @{acne = 0.87; oily_skin = 0.92}
    age = 28
    gender = "F"
    skin_sensitivity = "normal"
    include_skincare = $true
    include_diet = $true
    include_products = $true
} | ConvertTo-Json

Write-Host "Request:" -ForegroundColor Yellow
Write-Host "POST $BaseUrl/api/v1/recommend"
Write-Host "Body:"
$RecommendData | ConvertFrom-Json | ConvertTo-Json | Write-Host

Write-Host ""
Write-Host "Response:" -ForegroundColor Yellow

try {
    $RecResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/recommend" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $Token"; "Content-Type" = "application/json"} `
        -Body $RecommendData | Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    $RecResponse | ConvertTo-Json | Write-Host
    
    # Extract recommendation_id
    $RecId = $RecResponse.recommendation_id
    
    if ([string]::IsNullOrEmpty($RecId)) {
        Print-Failed "Could not extract recommendation_id"
        $TestsFailed++
    }
    else {
        Print-Success "Recommendation ID: $RecId"
        $TestsPassed++
        
        # Verify response structure
        Write-Host ""
        Write-Host "Checking response structure..."
        
        $RoutinesCount = $RecResponse.routines.Count
        $ProductsCount = $RecResponse.products.Count
        $RulesCount = $RecResponse.applied_rules.Count
        
        if ($RoutinesCount -gt 0) {
            Print-Success "Routines: $RoutinesCount"
            $TestsPassed++
        }
        else {
            Print-Failed "No routines found"
            $TestsFailed++
        }
        
        if ($ProductsCount -gt 0) {
            Print-Success "Products: $ProductsCount"
            $TestsPassed++
        }
        else {
            Print-Failed "No products found"
            $TestsFailed++
        }
        
        if ($RulesCount -gt 0) {
            Print-Success "Applied Rules: $RulesCount"
            $TestsPassed++
        }
        else {
            Print-Failed "No rules found"
            $TestsFailed++
        }
    }
}
catch {
    Print-Failed "Error generating recommendation: $($_.Exception.Message)"
    $TestsFailed++
}

Write-Host ""

# ===== TEST 2: Submit Feedback =====

Print-Header "TEST SUITE 2: FEEDBACK ENDPOINT"

if (-not [string]::IsNullOrEmpty($RecId)) {
    Print-Test "POST /api/v1/feedback"
    
    $FeedbackData = @{
        recommendation_id = $RecId
        helpful_rating = 4
        product_satisfaction = 4
        routine_completion_pct = 80
        would_recommend = $true
        timeframe = "2_weeks"
        feedback_text = "Great recommendations!"
    } | ConvertTo-Json
    
    Write-Host "Request:" -ForegroundColor Yellow
    Write-Host "POST $BaseUrl/api/v1/feedback"
    Write-Host "Body:"
    $FeedbackData | ConvertFrom-Json | ConvertTo-Json | Write-Host
    
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Yellow
    
    try {
        $FeedbackResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/feedback" `
            -Method Post `
            -Headers @{"Authorization" = "Bearer $Token"; "Content-Type" = "application/json"} `
            -Body $FeedbackData | Select-Object -ExpandProperty Content | ConvertFrom-Json
        
        $FeedbackResponse | ConvertTo-Json | Write-Host
        
        if ($null -ne $FeedbackResponse.feedback_id) {
            Print-Success "Feedback submitted (ID: $($FeedbackResponse.feedback_id))"
            $TestsPassed++
        }
        else {
            Print-Failed "Feedback submission failed"
            $TestsFailed++
        }
    }
    catch {
        Print-Failed "Error submitting feedback: $($_.Exception.Message)"
        $TestsFailed++
    }
    
    Write-Host ""
    
    # ===== TEST 3: Get Feedback Stats =====
    
    Print-Test "GET /api/v1/feedback/{recommendation_id}/stats"
    
    Write-Host "Request:" -ForegroundColor Yellow
    Write-Host "GET $BaseUrl/api/v1/feedback/$RecId/stats"
    Write-Host ""
    Write-Host "Response:" -ForegroundColor Yellow
    
    try {
        $StatsResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/feedback/$RecId/stats" `
            -Method Get `
            -Headers @{"Authorization" = "Bearer $Token"; "Content-Type" = "application/json"} | `
            Select-Object -ExpandProperty Content | ConvertFrom-Json
        
        $StatsResponse | ConvertTo-Json | Write-Host
        
        if ($null -ne $StatsResponse.avg_helpful_rating) {
            $AvgRating = $StatsResponse.avg_helpful_rating
            Print-Success "Average rating: $AvgRating"
            $TestsPassed++
        }
        else {
            Print-Failed "Stats retrieval failed"
            $TestsFailed++
        }
    }
    catch {
        Print-Failed "Error getting stats: $($_.Exception.Message)"
        $TestsFailed++
    }
}
else {
    Print-Warning "Skipping feedback tests (no recommendation_id)"
}

Write-Host ""

# ===== TEST 4: Search Products =====

Print-Header "TEST SUITE 3: PRODUCTS ENDPOINT"

Print-Test "GET /api/v1/products/search?tag=acne"

Write-Host "Request:" -ForegroundColor Yellow
Write-Host "GET $BaseUrl/api/v1/products/search?tag=acne"
Write-Host ""
Write-Host "Response:" -ForegroundColor Yellow

try {
    $SearchResponse = Invoke-WebRequest -Uri "$BaseUrl/api/v1/products/search?tag=acne" `
        -Method Get `
        -Headers @{"Authorization" = "Bearer $Token"; "Content-Type" = "application/json"} | `
        Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    $SearchResponse | ConvertTo-Json | Write-Host
    
    if ($null -ne $SearchResponse.count) {
        $Count = $SearchResponse.count
        if ($Count -gt 0) {
            Print-Success "Found $Count products"
            $TestsPassed++
        }
        else {
            Print-Warning "No products found (database may be empty)"
        }
    }
    else {
        Print-Failed "Product search failed"
        $TestsFailed++
    }
}
catch {
    Print-Failed "Error searching products: $($_.Exception.Message)"
    $TestsFailed++
}

Write-Host ""

# ===== TEST 5: Admin Endpoint =====

Print-Header "TEST SUITE 4: ADMIN ENDPOINTS"

Print-Test "POST /admin/reload-rules"

Write-Host "Request:" -ForegroundColor Yellow
Write-Host "POST $BaseUrl/admin/reload-rules"
Write-Host "Body: {}"
Write-Host ""
Write-Host "Response:" -ForegroundColor Yellow

try {
    $ReloadResponse = Invoke-WebRequest -Uri "$BaseUrl/admin/reload-rules" `
        -Method Post `
        -Headers @{"Authorization" = "Bearer $AdminToken"; "Content-Type" = "application/json"} `
        -Body "{}" | Select-Object -ExpandProperty Content | ConvertFrom-Json
    
    $ReloadResponse | ConvertTo-Json | Write-Host
    
    if ($null -ne $ReloadResponse.status) {
        if ($ReloadResponse.status -eq "success") {
            $RulesCount = $ReloadResponse.rules_loaded
            Print-Success "Rules reloaded: $RulesCount rules"
            $TestsPassed++
        }
        else {
            Print-Failed "Rule reload failed: $($ReloadResponse.status)"
            $TestsFailed++
        }
    }
    else {
        Print-Failed "Admin endpoint error"
        $TestsFailed++
    }
}
catch {
    Print-Failed "Error reloading rules: $($_.Exception.Message)"
    $TestsFailed++
}

Write-Host ""

# ===== SUMMARY =====

Print-Header "TEST SUMMARY"

Write-Host "Tests Passed: " -NoNewline
Write-Host $TestsPassed -ForegroundColor Green
Write-Host "Tests Failed: " -NoNewline
Write-Host $TestsFailed -ForegroundColor Red
Write-Host ""

if ($TestsFailed -eq 0) {
    Write-Host "✓ ALL TESTS PASSED!" -ForegroundColor Green
    exit 0
}
else {
    Write-Host "✗ SOME TESTS FAILED" -ForegroundColor Red
    exit 1
}
