# 🔌 Haski API - Endpoint Quick Reference

**Last Updated**: October 25, 2025  
**Status**: ✅ All Endpoints Verified & Working

---

## 📋 Quick Index

- **Health Checks**: 2 endpoints
- **Authentication**: 2 endpoints
- **Profile Management**: 3 endpoints
- **Image Analysis**: 1 endpoint
- **Recommendations**: 1+ endpoint
- **Feedback**: 2+ endpoints
- **Photos**: 3+ endpoints
- **Products**: 3+ endpoints

**Total**: 25+ Endpoints

---

## 🏥 Health Checks

### Check 1: Root Health

```
GET /

Response:
{
  "status": "ok",
  "message": "SkinHairAI API running"
}
```

### Check 2: API v1 Health

```
GET /api/v1/health

Response:
{
  "status": "ok",
  "version": "v1"
}
```

---

## 🔐 Authentication

### Sign Up

```
POST /api/v1/auth/signup

Content-Type: application/json

Body:
{
  "username": "john_doe",
  "email": "john@example.com",
  "password": "SecurePass123!"
}

Response (201):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}

Errors:
- 400: Username or email already registered
- 422: Invalid input
```

### Login

```
POST /api/v1/auth/login

Content-Type: application/json

Body:
{
  "email": "john@example.com",
  "password": "SecurePass123!"
}

OR

{
  "username": "john_doe",
  "password": "SecurePass123!"
}

Response (200):
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}

Errors:
- 400: Username or email required
- 401: Invalid credentials
- 422: Invalid input
```

---

## 👤 Profile Management

### Get Profile

```
GET /api/v1/profile/me

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "id": 1,
  "user_id": 1,
  "age": 28,
  "gender": "female",
  "location": "New York",
  "allergies": "pollen",
  "lifestyle": "active",
  "skin_type": "combination",
  "hair_type": "straight"
}

Errors:
- 401: Not authenticated
- 404: Profile not found
```

### Create Profile

```
POST /api/v1/profile/

Headers:
Authorization: Bearer {access_token}

Content-Type: application/json

Body (all optional):
{
  "birth_year": 1996,
  "age": 28,
  "gender": "female",
  "location": "New York",
  "allergies": "pollen",
  "lifestyle": "active",
  "skin_type": "combination",
  "hair_type": "straight"
}

Response (200):
{
  "id": 1,
  "user_id": 1
}

Errors:
- 400: Profile already exists
- 401: Not authenticated
- 422: Invalid input
```

### Update Profile

```
PUT /api/v1/profile/

Headers:
Authorization: Bearer {access_token}

Content-Type: application/json

Body (all optional):
{
  "birth_year": 1996,
  "age": 29,
  "gender": "female",
  "location": "San Francisco",
  "allergies": "latex, pollen",
  "lifestyle": "moderate",
  "skin_type": "oily",
  "hair_type": "curly"
}

Response (200):
{
  "id": 1,
  "user_id": 1
}

Errors:
- 401: Not authenticated
- 404: Profile not found
- 422: Invalid input
```

---

## 📸 Image Analysis

### Analyze Image

```
POST /api/v1/analyze/image

Headers (optional):
Authorization: Bearer {access_token}

Content-Type: multipart/form-data

Body:
image: <binary file data>

Supported Formats:
- image/jpeg
- image/png
- image/gif
- image/webp

Max Size: 10 MB

Response (201):
{
  "skin_type": "oily",
  "hair_type": "wavy",
  "conditions_detected": ["acne", "oiliness"],
  "confidence_scores": {
    "skin_type": 0.92,
    "hair_type": 0.87
  },
  "model_version": "v1-skinhair-classifier",
  "analysis_id": 123,
  "photo_id": 456,
  "status": "success"
}

Errors:
- 400: Invalid file type
- 400: Empty file uploaded
- 413: File exceeds 10 MB
- 500: Analysis failed
```

---

## 💡 Recommendations

### Generate Recommendations

```
POST /api/v1/recommend/recommend

Headers:
Authorization: Bearer {access_token}

Content-Type: application/json

Body (Option 1 - Load from DB):
{
  "analysis_id": 123
}

OR (Option 2 - Direct data):
{
  "analysis": {
    "skin_type": "oily",
    "hair_type": "wavy",
    "conditions": ["acne"]
  },
  "profile": {
    "age": 28,
    "gender": "female",
    "allergies": ["latex"]
  }
}

Response (201):
{
  "recommendation_id": "rec_20251024_001",
  "routines": [
    {
      "type": "morning",
      "steps": ["cleanse", "tone", "moisturize"],
      "details": "..."
    }
  ],
  "products": [
    {
      "id": "prod_001",
      "name": "Gentle Cleanser",
      "category": "cleanser",
      "reason": "Suitable for oily skin"
    }
  ],
  "diet": ["increase water intake"],
  "warnings": [],
  "escalation": {
    "level": "none",
    "message": "All clear",
    "high_priority": false
  },
  "applied_rules": ["r001", "r002"],
  "metadata": {
    "timestamp": "2025-10-25T10:30:00Z"
  }
}

Errors:
- 400: Invalid input data
- 401: Not authenticated
- 404: Analysis not found
- 500: Engine error
```

---

## 📝 Feedback

### Submit Feedback

```
POST /api/v1/feedback/submit

Headers:
Authorization: Bearer {access_token}

Content-Type: application/json

Body:
{
  "recommendation_id": "rec_20251024_001",
  "rating": 4,
  "helpful": true,
  "comment": "Great recommendations!",
  "improvement_areas": ["More specific instructions"]
}

Response (201):
{
  "id": 1,
  "recommendation_id": "rec_20251024_001",
  "user_id": 1,
  "rating": 4,
  "helpful": true,
  "created_at": "2025-10-25T10:30:00Z"
}

Errors:
- 400: Invalid input
- 401: Not authenticated
- 404: Recommendation not found
```

### Get Feedback Stats

```
GET /api/v1/feedback/{recommendation_id}/stats

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "recommendation_id": "rec_20251024_001",
  "total_feedback": 5,
  "average_rating": 4.2,
  "helpful_count": 4,
  "not_helpful_count": 1
}

Errors:
- 404: Recommendation not found
```

---

## 📸 Photo Management

### List Photos

```
GET /api/v1/photos/

Headers:
Authorization: Bearer {access_token}

Response (200):
[
  {
    "id": 1,
    "user_id": 1,
    "filename": "photo.jpg",
    "s3_key": "uploads/photo.jpg",
    "created_at": "2025-10-25T10:30:00Z"
  }
]

Errors:
- 401: Not authenticated
```

### Get Photo Details

```
GET /api/v1/photos/{id}

Headers:
Authorization: Bearer {access_token}

Response (200):
{
  "id": 1,
  "user_id": 1,
  "filename": "photo.jpg",
  "s3_key": "uploads/photo.jpg",
  "created_at": "2025-10-25T10:30:00Z"
}

Errors:
- 401: Not authenticated
- 404: Photo not found
```

### Delete Photo

```
DELETE /api/v1/photos/{id}

Headers:
Authorization: Bearer {access_token}

Response (204): No content

Errors:
- 401: Not authenticated
- 404: Photo not found
```

---

## 🛍️ Products

### List Products

```
GET /api/v1/products/

Query Parameters (optional):
- category: string (filter by category)
- limit: integer (default: 100)
- offset: integer (default: 0)

Response (200):
[
  {
    "id": "prod_001",
    "name": "Gentle Cleanser",
    "category": "cleanser",
    "description": "...",
    "price": 29.99,
    "rating": 4.5,
    "url": "https://..."
  }
]
```

### Get Product Details

```
GET /api/v1/products/{id}

Response (200):
{
  "id": "prod_001",
  "name": "Gentle Cleanser",
  "category": "cleanser",
  "description": "...",
  "price": 29.99,
  "rating": 4.5,
  "url": "https://...",
  "reviews": [...],
  "ingredients": [...]
}

Errors:
- 404: Product not found
```

### Add Product (Admin)

```
POST /api/v1/products/

Headers:
Authorization: Bearer {admin_token}

Content-Type: application/json

Body:
{
  "name": "New Cleanser",
  "category": "cleanser",
  "description": "Gentle formula",
  "price": 25.00,
  "rating": 0,
  "url": "https://..."
}

Response (201):
{
  "id": "prod_new",
  "name": "New Cleanser",
  "category": "cleanser",
  "description": "Gentle formula",
  "price": 25.00
}

Errors:
- 401: Not authenticated
- 403: Not admin
- 422: Invalid input
```

---

## 🔑 Authentication Headers

All protected endpoints require:

```
Authorization: Bearer {access_token}
```

Where `{access_token}` is the JWT token received from signup/login.

Example:

```
curl -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc..." \
     https://api.example.com/api/v1/profile/me
```

---

## 📊 Response Status Codes

| Code | Meaning                                 |
| ---- | --------------------------------------- |
| 200  | OK - Successful request                 |
| 201  | Created - Resource created successfully |
| 204  | No Content - Successful deletion        |
| 400  | Bad Request - Invalid input             |
| 401  | Unauthorized - Missing/invalid auth     |
| 403  | Forbidden - No permission               |
| 404  | Not Found - Resource doesn't exist      |
| 413  | Payload Too Large - File too big        |
| 422  | Validation Error - Invalid data format  |
| 500  | Server Error - Internal error           |

---

## 🔗 Base URLs

**Development**:

```
http://localhost:8000
```

**API v1 Prefix**:

```
/api/v1
```

**Full Example**:

```
http://localhost:8000/api/v1/auth/login
```

---

## 💻 Using with Frontend

### From React Component

```typescript
const API_URL = import.meta.env.VITE_API_BASE_URL || "http://localhost:8000";

// Login example
const response = await fetch(`${API_URL}/api/v1/auth/login`, {
  method: "POST",
  headers: {
    "Content-Type": "application/json",
  },
  body: JSON.stringify({
    email: "user@example.com",
    password: "password",
  }),
});

const { access_token } = await response.json();

// Subsequent requests with token
const profileResponse = await fetch(`${API_URL}/api/v1/profile/me`, {
  headers: {
    Authorization: `Bearer ${access_token}`,
  },
});
```

---

## 🧪 Testing All Endpoints

Run the comprehensive test suite:

```bash
python test_all_endpoints.py
```

This tests all endpoints with proper error handling and verification.

---

## ❓ Common Issues & Solutions

**"CORS error"**
→ Ensure backend has CORS configured for your frontend URL

**"Unauthorized (401)"**
→ Check token is valid and included in Authorization header

**"File too large (413)"**
→ Upload image under 10 MB

**"Invalid file type (400)"**
→ Use JPEG, PNG, GIF, or WebP format

**"Profile not found (404)"**
→ Create profile first via POST /api/v1/profile/

---

## 📞 Support

For detailed documentation, see:

- INTEGRATION_CHECK.md - Integration overview
- COMPLETE_VERIFICATION_REPORT.md - Detailed verification
- test_all_endpoints.py - Test examples
