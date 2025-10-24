# Backend API - Quick Start Guide

## Starting the Backend Server

```bash
cd d:\Haski-main\backend
python -m uvicorn app.main:app --host 127.0.0.1 --port 8001
```

Server will be available at: **http://127.0.0.1:8001**

## API Documentation

- **Interactive Swagger UI**: http://127.0.0.1:8001/docs
- **ReDoc Documentation**: http://127.0.0.1:8001/redoc
- **OpenAPI JSON**: http://127.0.0.1:8001/openapi.json

## Authentication Flow

### 1. Sign Up (Get JWT Token)

**Endpoint**: `POST /api/v1/auth/signup`

```bash
curl -X POST http://127.0.0.1:8001/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "secure_password_123"
  }'
```

**Response** (200 OK):
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxIiwiZXhwIjoxNzI5NzYxMjAwfQ.xxx",
  "token_type": "bearer"
}
```

Save the `access_token` - you'll need it for subsequent requests.

### 2. Upload Photo (Requires Authentication)

**Endpoint**: `POST /api/v1/photos/upload`

```bash
curl -X POST http://127.0.0.1:8001/api/v1/photos/upload \
  -H "Authorization: Bearer <your_token_from_signup>" \
  -F "image=@/path/to/image.jpg"
```

**Response** (201 Created):
```json
{
  "photo_id": 42,
  "image_url": "file://D:\\Haski-main\\backend\\storage\\images\\image.jpg"
}
```

### 3. Analyze Photo (Requires Authentication)

**Endpoint**: `POST /api/v1/analyze/photo`

```bash
curl -X POST http://127.0.0.1:8001/api/v1/analyze/photo \
  -H "Authorization: Bearer <your_token_from_signup>" \
  -F "image=@/path/to/image.jpg"
```

**Response** (201 Created):
```json
{
  "skin_type": "combination",
  "hair_type": "wavy",
  "conditions_detected": ["mild_acne", "dry_skin"],
  "confidence_scores": {
    "skin_type": 0.92,
    "hair_type": 0.87,
    "mild_acne": 0.76,
    "dry_skin": 0.65
  },
  "model_version": "v0-mock",
  "id": 15,
  "photo_id": 42
}
```

## File Upload Requirements

- **Maximum File Size**: 10 MB
- **Allowed Formats**: JPEG, PNG, GIF, WebP
- **MIME Types**: `image/jpeg`, `image/png`, `image/gif`, `image/webp`

### Common Upload Errors

| Status | Error | Solution |
|--------|-------|----------|
| 401 | Missing/invalid token | Ensure `Authorization: Bearer <token>` header is present |
| 400 | Invalid file type | Use jpeg, png, gif, or webp format |
| 413 | File too large | Compress image to under 10 MB |
| 400 | Empty file | Upload a file with content |

## Working with Python Requests

```python
import requests

BASE_URL = "http://127.0.0.1:8001"

# 1. Sign up
signup_response = requests.post(
    f"{BASE_URL}/api/v1/auth/signup",
    json={
        "username": "testuser",
        "email": "test@example.com",
        "password": "mypassword"
    }
)
token = signup_response.json()["access_token"]

# 2. Upload photo
headers = {"Authorization": f"Bearer {token}"}
with open("photo.jpg", "rb") as f:
    upload_response = requests.post(
        f"{BASE_URL}/api/v1/photos/upload",
        headers=headers,
        files={"image": f}
    )
print(upload_response.json())

# 3. Analyze photo
with open("photo.jpg", "rb") as f:
    analyze_response = requests.post(
        f"{BASE_URL}/api/v1/analyze/photo",
        headers=headers,
        files={"image": f}
    )
analysis = analyze_response.json()
print(f"Skin type: {analysis['skin_type']}")
print(f"Hair type: {analysis['hair_type']}")
```

## Database Migrations

Initialize the database with all tables:

```bash
cd backend

# Apply initial migration
python -m alembic upgrade head
```

After making changes to models:

```bash
# Generate new migration
python -m alembic revision --autogenerate -m "Description of changes"

# Apply migration
python -m alembic upgrade head

# Rollback if needed
python -m alembic downgrade -1
```

## Directory Structure

```
backend/
├── app/
│   ├── api/
│   │   └── v1/
│   │       ├── auth.py          # Login/signup endpoints
│   │       ├── photos.py         # Photo upload (requires auth)
│   │       ├── analyze.py        # Image analysis (requires auth)
│   │       ├── profile.py        # User profile endpoints
│   │       └── __init__.py       # Router aggregation
│   ├── core/
│   │   ├── config.py            # Settings
│   │   └── security.py          # JWT & auth dependencies
│   ├── db/
│   │   ├── base.py              # SQLAlchemy declarative base
│   │   └── session.py           # Database engine & session
│   ├── models/
│   │   └── db_models.py         # SQLAlchemy models
│   ├── services/
│   │   ├── storage.py           # File storage
│   │   └── ml_infer.py          # ML inference
│   └── main.py                  # FastAPI app definition
├── migrations/                  # Alembic migrations
│   └── versions/                # Individual migration files
├── storage/
│   └── images/                  # Uploaded images (local storage)
├── dev.db                       # SQLite database
└── alembic.ini                  # Alembic configuration
```

## Troubleshooting

### Server won't start
- Check if port 8001 is already in use: `netstat -ano | findstr "8001"`
- Kill process: `taskkill /PID <pid> /F`

### Database errors
- Delete `dev.db` and re-apply migrations: `python -m alembic upgrade head`

### 401 Unauthorized errors
- Make sure you're including the `Authorization` header
- Token format must be: `Authorization: Bearer <token>`
- Tokens expire after 24 hours by default

### CORS errors
- Frontend must be running on same host or CORS policy needs to be updated in `app/main.py`
