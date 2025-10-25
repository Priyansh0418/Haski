# Haski Recommender System - API Testing Script (PowerShell)
# ===========================================================
# This script tests all endpoints with curl/Invoke-WebRequest
# Usage: .\test_api.ps1 -Token "YOUR_JWT_TOKEN" -AdminToken "ADMIN_JWT_TOKEN"

[Diagnostics.CodeAnalysis.SuppressMessageAttribute("PSUseDeclaredVarsMoreThanAssignments", "",
    Justification="Tokens are consumed via PowerShell's case-insensitive parameter binding and lower-case references.")]
param(
    [string]$Token = "",
    [string]$AdminToken = "",
    [string]$BaseUrl = "http://localhost:8000"
)

# Test counters
$TestsPassed = 0
$TestsFailed = 0
$LastError = ""

# Helper function to show headers
function Write-HaskiHeader {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute("PSUseApprovedVerbs", "", Justification="Header is a suitable verb for context.")]
    param([string]$Title)
    Write-Host ""
    Write-Host ("╔" + "═" * 66 + "╗") -ForegroundColor Cyan
    Write-Host ("║ " + $Title.PadRight(64) + " ║") -ForegroundColor Cyan
    Write-Host ("╚" + "═" * 66 + "╝") -ForegroundColor Cyan
    Write-Host ""
}

function Write-HaskiTest {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute("PSUseApprovedVerbs", "", Justification="Test is a suitable verb for context.")]
    param([string]$Name)
    Write-Host "────────────────────────────────────────────────────────────────"
    Write-Host "TEST: $Name" -ForegroundColor Yellow
    Write-Host "────────────────────────────────────────────────────────────────"
}

function Write-HaskiSuccess {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute("PSUseApprovedVerbs", "", Justification="Success is a suitable verb for context.")]
    param([string]$Message)
    Write-Host "✓ $Message" -ForegroundColor Green
}

function Write-HaskiFailure {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute("PSUseApprovedVerbs", "", Justification="Failure is a suitable verb for context.")]
    param([string]$Message)
    Write-Host "✗ $Message" -ForegroundColor Red
}

function Write-HaskiWarning {
    [Diagnostics.CodeAnalysis.SuppressMessageAttribute("PSUseApprovedVerbs", "", Justification="Warning is a suitable verb for context.")]
    param([string]$Message)
    Write-Host "⚠ $Message" -ForegroundColor Yellow
}

# Banner
Write-HaskiHeader "Haski Recommender System - API Testing Suite"

# Check tokens
if ([string]::IsNullOrEmpty($Token)) {
    Write-HaskiWarning "No user token provided"
    Write-Host "Usage: .\test_api.ps1 -Token `"YOUR_JWT_TOKEN`" -AdminToken `"ADMIN_JWT_TOKEN`""
    Write-Host ""
    Write-Host "To get tokens:"
    Write-Host "1. Start the backend: cd backend; python -m uvicorn app.main:app --reload"
    Write-Host "2. Login to get JWT token"
    Write-Host ""
    exit 1
}

Write-HaskiSuccess "User token provided"
if ([string]::IsNullOrEmpty($AdminToken)) {
    $AdminToken = $Token
    Write-HaskiWarning "No admin token provided, using user token"
}
else {
    Write-HaskiSuccess "Admin token provided"
}

Write-Host "Base URL: $BaseUrl"
Write-Host ""

# ===== TEST 1: Generate Recommendation =====

Write-HaskiHeader "TEST SUITE 1: RECOMMENDATION ENDPOINT"

Write-HaskiTest "POST /api/v1/recommend (Direct Analysis)"

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
        Write-HaskiFailure "Could not extract recommendation_id"
        $TestsFailed++
    }
    else {
        Write-HaskiSuccess "Recommendation ID: $RecId"
        $TestsPassed++
        
        # Verify response structure
        Write-Host ""
        Write-Host "Checking response structure..."
        
        $RoutinesCount = $RecResponse.routines.Count
        $ProductsCount = $RecResponse.products.Count
        $RulesCount = $RecResponse.applied_rules.Count
        
        if ($RoutinesCount -gt 0) {
            Write-HaskiSuccess "Routines: $RoutinesCount"
            $TestsPassed++
        }
        else {
            Write-HaskiFailure "No routines found"
            $TestsFailed++
        }
        
        if ($ProductsCount -gt 0) {
            Write-HaskiSuccess "Products: $ProductsCount"
            $TestsPassed++
        }
        else {
            Write-HaskiFailure "No products found"
            $TestsFailed++
        }
        
        if ($RulesCount -gt 0) {
            Write-HaskiSuccess "Applied Rules: $RulesCount"
            $TestsPassed++
        }
        else {
            Write-HaskiFailure "No rules found"
            $TestsFailed++
        }
    }
}
catch {
    Write-HaskiFailure "Error generating recommendation: $($_.Exception.Message)"
    $TestsFailed++
}

Write-Host ""

# ===== TEST 2: Submit Feedback =====

Write-HaskiHeader "TEST SUITE 2: FEEDBACK ENDPOINT"

if (-not [string]::IsNullOrEmpty($RecId)) {
    Write-HaskiTest "POST /api/v1/feedback"
    
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
            Write-HaskiSuccess "Feedback submitted (ID: $($FeedbackResponse.feedback_id))"
            $TestsPassed++
        }
        else {
            Write-HaskiFailure "Feedback submission failed"
            $TestsFailed++
        }
    }
    catch {
        Write-HaskiFailure "Error submitting feedback: $($_.Exception.Message)"
        $TestsFailed++
    }
    
    Write-Host ""
    
    # ===== TEST 3: Get Feedback Stats =====
    
    Write-HaskiTest "GET /api/v1/feedback/{recommendation_id}/stats"
    
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
            Write-HaskiSuccess "Average rating: $AvgRating"
            $TestsPassed++
        }
        else {
            Write-HaskiFailure "Stats retrieval failed"
            $TestsFailed++
        }
    }
    catch {
        Write-HaskiFailure "Error getting stats: $($_.Exception.Message)"
        $TestsFailed++
    }
}
else {
    Write-HaskiWarning "Skipping feedback tests (no recommendation_id)"
}

Write-Host ""

# ===== TEST 4: Search Products =====

Write-HaskiHeader "TEST SUITE 3: PRODUCTS ENDPOINT"

Write-HaskiTest "GET /api/v1/products/search?tag=acne"

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
            Write-HaskiSuccess "Found $Count products"
            $TestsPassed++
        }
        else {
            Write-HaskiWarning "No products found (database may be empty)"
        }
    }
    else {
        Write-HaskiFailure "Product search failed"
        $TestsFailed++
    }
}
catch {
    Write-HaskiFailure "Error searching products: $($_.Exception.Message)"
    $TestsFailed++
}

Write-Host ""

# ===== TEST 5: Admin Endpoint =====

Write-HaskiHeader "TEST SUITE 4: ADMIN ENDPOINTS"

Write-HaskiTest "POST /admin/reload-rules"

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
            Write-HaskiSuccess "Rules reloaded: $RulesCount rules"
            $TestsPassed++
        }
        else {
            Write-HaskiFailure "Rule reload failed: $($ReloadResponse.status)"
            $TestsFailed++
        }
    }
    else {
        Write-HaskiFailure "Admin endpoint error"
        $TestsFailed++
    }
}
catch {
    Write-HaskiFailure "Error reloading rules: $($_.Exception.Message)"
    $TestsFailed++
}

Write-Host ""

# ===== SUMMARY =====

Write-HaskiHeader "TEST SUMMARY"

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
