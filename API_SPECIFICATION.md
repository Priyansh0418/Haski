# Admin Panel API Specification

**Version:** 1.0
**Date:** January 2024
**Status:** Ready for Implementation

---

## API Overview

The Admin Recommendations panel requires three API endpoints for full functionality:

| #   | Method | Endpoint                         | Purpose            | Priority        |
| --- | ------ | -------------------------------- | ------------------ | --------------- |
| 1   | GET    | `/api/v1/products`               | List all products  | ⭐⭐⭐ Required |
| 2   | POST   | `/api/v1/products`               | Create new product | ⭐⭐⭐ Required |
| 3   | POST   | `/api/v1/recommend/reload-rules` | Reload rules       | ⭐⭐ Optional   |

---

## Endpoint Specifications

### 1. GET /api/v1/products

**Description:** Retrieve a list of all products

**HTTP Method:** `GET`

**URL:** `http://localhost:8000/api/v1/products`

**Headers:**

```
Accept: application/json
```

**Query Parameters:** (Optional)

```
skip: integer (default: 0) - pagination offset
limit: integer (default: 100) - pagination limit
category: string (optional) - filter by category
brand: string (optional) - filter by brand
```

**Request Example:**

```bash
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Accept: application/json"
```

**Response Status:** `200 OK`

**Response Schema:**

```json
{
  "products": [
    {
      "id": 1,
      "name": "string",
      "brand": "string",
      "category": "string",
      "price_usd": "number",
      "tags": ["string"],
      "ingredients": ["string"],
      "dermatologically_safe": "boolean",
      "recommended_for": ["string"],
      "created_at": "ISO-8601 datetime (optional)",
      "updated_at": "ISO-8601 datetime (optional)"
    }
  ]
}
```

**Response Example:**

```json
{
  "products": [
    {
      "id": 1,
      "name": "CeraVe Hydrating Cleanser",
      "brand": "CeraVe",
      "category": "cleanser",
      "price_usd": 12.99,
      "tags": ["gentle", "fragrance-free", "hydrating"],
      "ingredients": ["water", "glycerin", "ceramides", "hyaluronic acid"],
      "dermatologically_safe": true,
      "recommended_for": ["dry_skin", "sensitive_skin"],
      "created_at": "2024-01-15T10:30:00Z",
      "updated_at": "2024-01-15T10:30:00Z"
    },
    {
      "id": 2,
      "name": "Neutrogena Acne Cleanser",
      "brand": "Neutrogena",
      "category": "cleanser",
      "price_usd": 8.99,
      "tags": ["acne-fighting", "oil-control"],
      "ingredients": ["water", "salicylic acid", "alcohol"],
      "dermatologically_safe": false,
      "recommended_for": ["oily_skin", "acne_prone"],
      "created_at": "2024-01-15T10:45:00Z",
      "updated_at": "2024-01-15T10:45:00Z"
    }
  ]
}
```

**Error Responses:**

`500 Internal Server Error` (Database failure):

```json
{
  "detail": "Database connection failed"
}
```

**Notes:**

- Returns empty array if no products exist
- Should support pagination for large datasets (100+ products)
- Response time should be < 500ms
- Consider caching for performance

---

### 2. POST /api/v1/products

**Description:** Create a new product

**HTTP Method:** `POST`

**URL:** `http://localhost:8000/api/v1/products`

**Headers:**

```
Content-Type: application/json
Accept: application/json
```

**Request Schema:**

```json
{
  "name": "string (required, 1-255 chars)",
  "brand": "string (required, 1-255 chars)",
  "category": "string (required, enum)",
  "tags": ["string"] | "comma,separated,string" (optional),
  "ingredients": ["string"] | "comma,separated,string" (optional),
  "price_usd": "number (optional, > 0)",
  "dermatologically_safe": "boolean (optional, default: false)",
  "recommended_for": ["string"] (optional)
}
```

**Valid Categories:**

```
cleanser
moisturizer
serum
treatment
sunscreen
mask
other
```

**Request Example (JSON):**

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CeraVe Hydrating Moisturizer",
    "brand": "CeraVe",
    "category": "moisturizer",
    "tags": ["hydrating", "gentle", "hypoallergenic"],
    "ingredients": ["water", "glycerin", "ceramides"],
    "price_usd": 24.99,
    "dermatologically_safe": true,
    "recommended_for": ["dry_skin", "sensitive_skin"]
  }'
```

**Request Example (from Admin Panel):**

```
POST /api/v1/products
Content-Type: application/json

{
  "name": "CeraVe Moisturizing Cream",
  "brand": "CeraVe",
  "category": "moisturizer",
  "tags": ["hydrating", "gentle"],
  "ingredients": ["water", "glycerin", "ceramides"]
}
```

**Response Status:** `201 Created`

**Response Schema:**

```json
{
  "id": "number",
  "name": "string",
  "brand": "string",
  "category": "string",
  "price_usd": "number",
  "tags": ["string"],
  "ingredients": ["string"],
  "dermatologically_safe": "boolean",
  "recommended_for": ["string"],
  "message": "Product created successfully"
}
```

**Response Example:**

```json
{
  "id": 3,
  "name": "CeraVe Hydrating Moisturizer",
  "brand": "CeraVe",
  "category": "moisturizer",
  "tags": ["hydrating", "gentle", "hypoallergenic"],
  "ingredients": ["water", "glycerin", "ceramides"],
  "dermatologically_safe": true,
  "recommended_for": ["dry_skin", "sensitive_skin"],
  "message": "Product created successfully"
}
```

**Error Responses:**

`400 Bad Request` (Missing required field):

```json
{
  "detail": "name: field required"
}
```

`400 Bad Request` (Empty string):

```json
{
  "detail": "name: must not be empty"
}
```

`400 Bad Request` (Invalid category):

```json
{
  "detail": "category: not a valid choice"
}
```

`422 Unprocessable Entity` (Invalid data type):

```json
{
  "detail": [
    {
      "loc": ["body", "price_usd"],
      "msg": "value is not a valid number",
      "type": "type_error.number"
    }
  ]
}
```

`500 Internal Server Error` (Database failure):

```json
{
  "detail": "Failed to create product: duplicate entry"
}
```

**Validation Rules:**

- `name` required, 1-255 characters, not empty
- `brand` required, 1-255 characters, not empty
- `category` required, must be from valid categories list
- `tags` optional, array of strings or comma-separated string
- `ingredients` optional, array of strings or comma-separated string
- `price_usd` optional, must be positive number
- `dermatologically_safe` optional boolean, default false

**Notes:**

- Tags/ingredients should be split on commas if provided as string
- Auto-sanitize input to prevent XSS/SQL injection
- Should validate all fields before database insert
- Response includes created product data with ID
- Should log creation for audit trail

---

### 3. POST /api/v1/recommend/reload-rules

**Description:** Trigger backend to reload recommendation rules (optional endpoint)

**HTTP Method:** `POST`

**URL:** `http://localhost:8000/api/v1/recommend/reload-rules`

**Headers:**

```
Accept: application/json
```

**Request Body:** (Empty)

```
(No body required)
```

**Request Example:**

```bash
curl -X POST "http://localhost:8000/api/v1/recommend/reload-rules" \
  -H "Accept: application/json"
```

**Response Status:** `200 OK`

**Response Schema:**

```json
{
  "status": "success",
  "message": "Rules reloaded successfully",
  "timestamp": "ISO-8601 datetime",
  "rules_loaded": "integer (optional)"
}
```

**Response Example:**

```json
{
  "status": "success",
  "message": "Rules reloaded successfully",
  "timestamp": "2024-01-15T10:30:45.123456Z",
  "rules_loaded": 42
}
```

**Error Responses:**

`500 Internal Server Error` (Rules file missing):

```json
{
  "detail": "Rules file not found: rules.yml"
}
```

`500 Internal Server Error` (Invalid YAML):

```json
{
  "detail": "Failed to parse rules.yml: invalid YAML syntax"
}
```

**Notes:**

- This endpoint is optional for MVP
- Implement only if rules need dynamic reloading
- Should be called after uploading new rules.yml
- Frontend will call this automatically after rules upload
- Can be used for maintenance/debugging

---

## Implementation Guide

### Python/FastAPI Example

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import Optional, List

router = APIRouter(prefix="/api/v1", tags=["products"])

# Pydantic models
from pydantic import BaseModel, validator

class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    tags: Optional[List[str]] = []
    ingredients: Optional[List[str]] = []
    price_usd: Optional[float] = None
    dermatologically_safe: Optional[bool] = False
    recommended_for: Optional[List[str]] = []

    @validator('name', 'brand')
    def not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('must not be empty')
        return v

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    tags: List[str]
    ingredients: List[str]
    dermatologically_safe: bool
    recommended_for: List[str]

# Endpoints
@router.get("/products")
async def list_products(
    skip: int = 0,
    limit: int = 100,
    category: Optional[str] = None,
    brand: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all products"""
    query = db.query(Product)

    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)

    products = query.offset(skip).limit(limit).all()

    return {
        "products": [
            {
                "id": p.id,
                "name": p.name,
                "brand": p.brand,
                "category": p.category,
                "price_usd": p.price_usd,
                "tags": p.tags,
                "ingredients": p.ingredients,
                "dermatologically_safe": p.dermatologically_safe,
                "recommended_for": p.recommended_for
            }
            for p in products
        ]
    }

@router.post("/products", status_code=201)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create new product"""
    try:
        new_product = Product(
            name=product.name,
            brand=product.brand,
            category=product.category,
            tags=product.tags,
            ingredients=product.ingredients,
            price_usd=product.price_usd,
            dermatologically_safe=product.dermatologically_safe,
            recommended_for=product.recommended_for
        )
        db.add(new_product)
        db.commit()
        db.refresh(new_product)

        return {
            "id": new_product.id,
            "name": new_product.name,
            "brand": new_product.brand,
            "category": new_product.category,
            "tags": new_product.tags,
            "ingredients": new_product.ingredients,
            "dermatologically_safe": new_product.dermatologically_safe,
            "recommended_for": new_product.recommended_for,
            "message": "Product created successfully"
        }
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/recommend/reload-rules")
async def reload_rules():
    """Reload recommendation rules"""
    try:
        # Your rule loading logic here
        return {
            "status": "success",
            "message": "Rules reloaded successfully",
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

---

## CORS Configuration

Frontend runs on `http://localhost:5173` or `http://localhost:3000`
Backend must allow these origins:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://localhost:3000",
        "http://localhost:8080"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Testing Guide

### Manual Testing with curl

**1. List products:**

```bash
curl -X GET "http://localhost:8000/api/v1/products" \
  -H "Accept: application/json"
```

**2. Create product:**

```bash
curl -X POST "http://localhost:8000/api/v1/products" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "brand": "Test Brand",
    "category": "cleanser",
    "tags": ["gentle"],
    "ingredients": ["water"]
  }'
```

**3. Reload rules:**

```bash
curl -X POST "http://localhost:8000/api/v1/recommend/reload-rules" \
  -H "Accept: application/json"
```

### Automated Testing with pytest

```python
from fastapi.testclient import TestClient

client = TestClient(app)

def test_list_products():
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    data = response.json()
    assert "products" in data
    assert isinstance(data["products"], list)

def test_create_product():
    response = client.post("/api/v1/products", json={
        "name": "Test",
        "brand": "Test",
        "category": "cleanser"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Test"

def test_create_product_missing_name():
    response = client.post("/api/v1/products", json={
        "brand": "Test",
        "category": "cleanser"
    })
    assert response.status_code == 422

def test_reload_rules():
    response = client.post("/api/v1/recommend/reload-rules")
    assert response.status_code == 200
    assert response.json()["status"] == "success"
```

---

## Performance Expectations

| Operation                     | Expected Time | Status         |
| ----------------------------- | ------------- | -------------- |
| GET /products (1-100 items)   | < 100ms       | ✅ Required    |
| POST /products                | < 500ms       | ✅ Required    |
| List pagination (1000+ items) | < 200ms       | ✅ Recommended |
| Reload rules                  | < 1s          | ⏳ Optional    |

---

## Error Handling Standards

**HTTP Status Codes:**

- `200 OK` - Successful GET
- `201 Created` - Successful POST (new resource)
- `400 Bad Request` - Validation error (invalid input)
- `404 Not Found` - Resource not found
- `422 Unprocessable Entity` - Invalid data type
- `500 Internal Server Error` - Server error

**Error Response Format:**

```json
{
  "detail": "Human-readable error message"
}
```

or

```json
{
  "detail": [
    {
      "loc": ["body", "field_name"],
      "msg": "error message",
      "type": "error_type"
    }
  ]
}
```

---

## Security Considerations

### Required

- [ ] Input validation on all fields
- [ ] SQL injection prevention (use parameterized queries)
- [ ] XSS prevention (sanitize output)
- [ ] CORS properly configured
- [ ] Rate limiting (optional)

### Future

- [ ] Authentication/authorization
- [ ] HTTPS only
- [ ] API key or token requirement
- [ ] Audit logging
- [ ] Data encryption

---

## Frontend Integration

Frontend (AdminRecommendations.tsx) will:

1. GET `/api/v1/products` on component mount
2. POST `/api/v1/products` when user submits form
3. Optionally POST `/api/v1/recommend/reload-rules` after file upload

See `ADMIN_PAGE_DOCUMENTATION.md` for details.

---

## Database Schema Example

```sql
CREATE TABLE products (
    id INTEGER PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL,
    brand VARCHAR(255) NOT NULL,
    category VARCHAR(50) NOT NULL,
    price_usd DECIMAL(10, 2),
    tags JSON,
    ingredients JSON,
    dermatologically_safe BOOLEAN DEFAULT FALSE,
    recommended_for JSON,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    INDEX idx_brand (brand),
    INDEX idx_category (category)
);
```

---

## Deployment Checklist

- [ ] All endpoints implemented
- [ ] CORS configured
- [ ] Database migration created
- [ ] Input validation complete
- [ ] Error handling tested
- [ ] Performance tested
- [ ] Security audit complete
- [ ] Logging configured
- [ ] Documentation complete
- [ ] Frontend integration tested
- [ ] Production database ready
- [ ] Monitoring set up

---

## Summary

This API specification provides a complete definition of the three endpoints required for the Admin Recommendations panel:

✅ **GET /api/v1/products** - List all products
✅ **POST /api/v1/products** - Create new product
⏳ **POST /api/v1/recommend/reload-rules** - Reload rules (optional)

Use this as a reference for implementation. See `ADMIN_BACKEND_INTEGRATION.md` for detailed code examples.
