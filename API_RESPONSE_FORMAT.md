# 🎯 API Response Format - Expected Behavior

## Endpoint: POST /api/v1/analyze/photo

### Request

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/photo" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  -F "image=@/path/to/image.jpg"
```

---

## Response Format (Business-Friendly)

### Status: 201 Created

```json
{
  "skin_type": "dry",
  "hair_type": "straight",
  "conditions_detected": ["blackheads"],
  "confidence_scores": {
    "dry": 0.91,
    "straight": 0.84
  },
  "model_version": "v1-skinhair-classifier",
  "analysis_id": 5,
  "photo_id": 9,
  "status": "success"
}
```

---

## Response Field Descriptions

| Field                 | Type    | Description                                                       |
| --------------------- | ------- | ----------------------------------------------------------------- |
| `skin_type`           | string  | Detected skin type (e.g., "dry", "oily", "combination", "normal") |
| `hair_type`           | string  | Detected hair type (e.g., "straight", "wavy", "curly", "coily")   |
| `conditions_detected` | array   | List of detected skin conditions (e.g., ["acne", "blackheads"])   |
| `confidence_scores`   | object  | Confidence scores for each detected attribute (0.0 - 1.0)         |
| `model_version`       | string  | Version identifier for the ML model used                          |
| `analysis_id`         | integer | Unique ID for this analysis in the database                       |
| `photo_id`            | integer | Reference to the uploaded photo record                            |
| `status`              | string  | Analysis status ("success" or "error")                            |

---

## Real-World Examples

### Example 1: Clear Skin

```json
{
  "skin_type": "normal",
  "hair_type": "straight",
  "conditions_detected": [],
  "confidence_scores": {
    "normal": 0.95,
    "straight": 0.92
  },
  "model_version": "v1-skinhair-classifier",
  "analysis_id": 10,
  "photo_id": 15,
  "status": "success"
}
```

### Example 2: Multiple Conditions

```json
{
  "skin_type": "oily",
  "hair_type": "curly",
  "conditions_detected": ["acne", "enlarged_pores", "hyperpigmentation"],
  "confidence_scores": {
    "oily": 0.87,
    "curly": 0.91,
    "acne": 0.78,
    "enlarged_pores": 0.72,
    "hyperpigmentation": 0.65
  },
  "model_version": "v1-skinhair-classifier",
  "analysis_id": 11,
  "photo_id": 16,
  "status": "success"
}
```

### Example 3: Error Response

```json
{
  "detail": "Invalid file type. Allowed types: image/jpeg, image/png, image/gif, image/webp"
}
```

Status: **400 Bad Request**

---

## Complete Workflow Example

### Step 1: Signup

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/auth/signup" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "SecurePass123!"
  }'
```

**Response:**

```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

---

### Step 2: Analyze Image

```bash
curl -X POST "http://127.0.0.1:8000/api/v1/analyze/photo" \
  -H "Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..." \
  -F "image=@user_selfie.jpg"
```

**Response:**

```json
{
  "skin_type": "combination",
  "hair_type": "wavy",
  "conditions_detected": ["seborrheic_dermatitis", "slight_dryness"],
  "confidence_scores": {
    "combination": 0.88,
    "wavy": 0.85,
    "seborrheic_dermatitis": 0.72,
    "slight_dryness": 0.68
  },
  "model_version": "v1-skinhair-classifier",
  "analysis_id": 42,
  "photo_id": 67,
  "status": "success"
}
```

---

## HTTP Status Codes

| Code                    | Meaning                | Scenario                       |
| ----------------------- | ---------------------- | ------------------------------ |
| `201 Created`           | ✅ Analysis successful | Image analyzed, results stored |
| `400 Bad Request`       | ❌ Invalid file        | Wrong file type or empty file  |
| `403 Forbidden`         | ❌ Not authenticated   | Missing or invalid JWT token   |
| `413 Payload Too Large` | ❌ File too large      | Image exceeds 10MB             |
| `500 Internal Error`    | ❌ Server error        | Model inference failed         |

---

## Integration Examples

### Python Requests

```python
import requests

# Setup
token = "your_jwt_token_here"
headers = {"Authorization": f"Bearer {token}"}
url = "http://127.0.0.1:8000/api/v1/analyze/photo"

# Upload and analyze
with open("photo.jpg", "rb") as f:
    files = {"image": f}
    response = requests.post(url, headers=headers, files=files)

# Parse response
result = response.json()
print(f"Skin Type: {result['skin_type']}")
print(f"Hair Type: {result['hair_type']}")
print(f"Conditions: {result['conditions_detected']}")
for key, conf in result['confidence_scores'].items():
    print(f"  - {key}: {conf:.1%}")
```

### JavaScript/Fetch

```javascript
const token = "your_jwt_token_here";
const formData = new FormData();
formData.append("image", fileInput.files[0]);

const response = await fetch("/api/v1/analyze/photo", {
  method: "POST",
  headers: {
    Authorization: `Bearer ${token}`,
  },
  body: formData,
});

const result = await response.json();
console.log(`Skin Type: ${result.skin_type}`);
console.log(`Hair Type: ${result.hair_type}`);
console.log(`Conditions: ${result.conditions_detected.join(", ")}`);
```

### cURL (One-liner)

```bash
curl -X POST "http://localhost:8000/api/v1/analyze/photo" \
  -H "Authorization: Bearer $(curl -s -X POST http://localhost:8000/api/v1/auth/signup -H 'Content-Type: application/json' -d '{\"username\":\"user\",\"email\":\"u@test.com\",\"password\":\"pass\"}' | jq -r '.access_token')" \
  -F "image=@photo.jpg" | jq .
```

---

## Testing the API

### Using TestClient (Python)

```python
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

# Create user
signup = client.post("/api/v1/auth/signup", json={
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123"
})
token = signup.json()["access_token"]

# Analyze image
with open("test_image.jpg", "rb") as f:
    result = client.post(
        "/api/v1/analyze/photo",
        files={"image": f},
        headers={"Authorization": f"Bearer {token}"}
    )

print(result.json())
```

### Run Test Suite

```bash
# Complete API tests
python api_test_complete.py

# End-to-end workflow
python test_integration_final.py

# Backend integration
python test_backend_integration.py
```

---

## Database Records

After analysis, the following records are created:

### Photo Record

```python
{
  "id": 9,
  "user_id": 5,
  "filename": "image.jpg",
  "s3_key": None,
  "uploaded_at": "2025-10-24T20:50:56.123456"
}
```

### Analysis Record

```python
{
  "id": 5,
  "user_id": 5,
  "photo_id": 9,
  "skin_type": "dry",
  "hair_type": "straight",
  "conditions": ["blackheads"],
  "confidence_scores": {
    "skin_type": 0.91,
    "hair_type": 0.84,
    "conditions": [0.77]
  },
  "created_at": "2025-10-24T20:50:56.123456"
}
```

Query from database:

```python
from backend.app.db.session import SessionLocal
from backend.app.models.db_models import Analysis

db = SessionLocal()
analysis = db.query(Analysis).filter(Analysis.id == 5).first()
print(f"Skin Type: {analysis.skin_type}")
print(f"Confidence: {analysis.confidence_scores}")
```

---

## Next Steps

1. **Integration**: Use response fields in your UI
2. **Storage**: Results are automatically saved to database
3. **Recommendations**: Use confidence scores for follow-up suggestions
4. **Personalization**: Store user history for trends
5. **Scaling**: Deploy to production for multi-user access

---

**✅ API is ready for production integration!**
