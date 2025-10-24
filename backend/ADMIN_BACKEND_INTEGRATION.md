# Admin Panel - Backend Integration Guide

## Overview

The AdminRecommendations component requires backend API endpoints to function. This guide helps you implement the required endpoints to support the admin panel.

---

## Required Endpoints

### 1. GET /api/v1/products

**Purpose:** Retrieve list of all products

**Endpoint:**

```python
@router.get("/products", response_model=dict)
async def list_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = db.query(Product).all()
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
                "recommended_for": p.recommended_for or []
            }
            for p in products
        ]
    }
```

**Request:**

```bash
GET /api/v1/products
```

**Response (200 OK):**

```json
{
  "products": [
    {
      "id": 1,
      "name": "CeraVe Moisturizing Cream",
      "brand": "CeraVe",
      "category": "moisturizer",
      "price_usd": 24.99,
      "tags": ["hydrating", "gentle", "hypoallergenic"],
      "ingredients": ["water", "glycerin", "ceramides"],
      "dermatologically_safe": true,
      "recommended_for": ["dry_skin", "sensitive_skin"]
    },
    {
      "id": 2,
      "name": "Cetaphil Cleanser",
      "brand": "Cetaphil",
      "category": "cleanser",
      "price_usd": 8.99,
      "tags": ["gentle", "fragrance_free"],
      "ingredients": ["water", "cetyl_alcohol"],
      "dermatologically_safe": true,
      "recommended_for": ["sensitive_skin"]
    }
  ]
}
```

**Frontend Usage:**

```tsx
const response = await fetch(`${API_BASE}/api/v1/products`);
const data = await response.json();
setProducts(data.products || data);
```

---

### 2. POST /api/v1/products

**Purpose:** Create a new product

**Endpoint:**

```python
from pydantic import BaseModel
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    tags: Optional[List[str]] = []
    ingredients: Optional[List[str]] = []
    price_usd: Optional[float] = None
    dermatologically_safe: Optional[bool] = False
    recommended_for: Optional[List[str]] = []

@router.post("/products", response_model=dict, status_code=201)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create a new product"""
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
            "message": "Product created successfully"
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
```

**Request:**

```bash
POST /api/v1/products
Content-Type: application/json

{
  "name": "CeraVe Hydrating Cleanser",
  "brand": "CeraVe",
  "category": "cleanser",
  "tags": ["gentle", "fragrance-free", "hydrating"],
  "ingredients": ["water", "glycerin", "ceramides"],
  "price_usd": 12.99,
  "dermatologically_safe": true,
  "recommended_for": ["dry_skin", "sensitive_skin"]
}
```

**Response (201 Created):**

```json
{
  "id": 3,
  "name": "CeraVe Hydrating Cleanser",
  "brand": "CeraVe",
  "category": "cleanser",
  "tags": ["gentle", "fragrance-free", "hydrating"],
  "ingredients": ["water", "glycerin", "ceramides"],
  "dermatologically_safe": true,
  "message": "Product created successfully"
}
```

**Error Response (400 Bad Request):**

```json
{
  "detail": "name: field required"
}
```

**Frontend Usage:**

```tsx
const payload = {
  name: formData.name,
  brand: formData.brand,
  category: formData.category,
  tags: formData.tags
    .split(",")
    .map((t) => t.trim())
    .filter((t) => t),
  ingredients: formData.ingredients
    .split(",")
    .map((i) => i.trim())
    .filter((i) => i),
  dermatologically_safe: false,
  recommended_for: [],
};

const response = await fetch(`${API_BASE}/api/v1/products`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify(payload),
});

if (response.ok) {
  setSuccessMessage("Product added successfully!");
  await fetchProducts(); // Refresh list
}
```

---

### 3. POST /api/v1/recommend/reload-rules (Optional)

**Purpose:** Reload rules after YAML upload

**Endpoint:**

```python
@router.post("/recommend/reload-rules", response_model=dict)
async def reload_rules():
    """Reload recommendation rules from file"""
    try:
        # Reload your rule engine here
        # Example: rule_engine = RuleEngine()
        # Example: rule_engine.load_rules()

        return {
            "status": "success",
            "message": "Rules reloaded successfully",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
```

**Request:**

```bash
POST /api/v1/recommend/reload-rules
```

**Response (200 OK):**

```json
{
  "status": "success",
  "message": "Rules reloaded successfully",
  "timestamp": "2024-01-15T10:30:45.123456"
}
```

**Frontend Usage:**

```tsx
const response = await fetch(`${API_BASE}/api/v1/recommend/reload-rules`, {
  method: "POST",
});

if (response.ok) {
  setSuccessMessage("Rules reloaded successfully!");
}
```

---

## CORS Configuration

**Required:** Enable CORS for frontend to access backend

**Add to `backend/app/main.py`:**

```python
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

---

## Database Model Example

**Location:** `backend/app/models/db_models.py`

```python
from sqlalchemy import Column, Integer, String, Float, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True, nullable=False)
    brand = Column(String, index=True, nullable=False)
    category = Column(String, index=True)
    price_usd = Column(Float, nullable=True)

    # Store as JSON arrays
    tags = Column(JSON, default=[])
    ingredients = Column(JSON, default=[])
    recommended_for = Column(JSON, default=[])

    dermatologically_safe = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "brand": self.brand,
            "category": self.category,
            "price_usd": self.price_usd,
            "tags": self.tags,
            "ingredients": self.ingredients,
            "dermatologically_safe": self.dermatologically_safe,
            "recommended_for": self.recommended_for
        }
```

---

## Integration Steps

### Step 1: Add Pydantic Schemas

**File:** `backend/app/schemas/pydantic_schemas.py`

```python
from pydantic import BaseModel
from typing import List, Optional

class ProductCreate(BaseModel):
    name: str
    brand: str
    category: str
    tags: Optional[List[str]] = []
    ingredients: Optional[List[str]] = []
    price_usd: Optional[float] = None
    dermatologically_safe: Optional[bool] = False
    recommended_for: Optional[List[str]] = []

    class Config:
        example = {
            "name": "CeraVe Moisturizer",
            "brand": "CeraVe",
            "category": "moisturizer",
            "tags": ["hydrating", "gentle"],
            "ingredients": ["water", "glycerin"]
        }

class ProductResponse(BaseModel):
    id: int
    name: str
    brand: str
    category: str
    tags: List[str]
    ingredients: List[str]
    dermatologically_safe: bool

    class Config:
        from_attributes = True
```

### Step 2: Add Endpoints

**File:** `backend/app/api/v1/products.py` (create if not exists)

```python
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from backend.app.db.session import get_db
from backend.app.models.db_models import Product
from backend.app.schemas.pydantic_schemas import ProductCreate, ProductResponse

router = APIRouter(prefix="/api/v1", tags=["products"])

@router.get("/products")
async def list_products(db: Session = Depends(get_db)):
    """Get all products"""
    products = db.query(Product).all()
    return {
        "products": [p.to_dict() for p in products]
    }

@router.post("/products", status_code=201)
async def create_product(
    product: ProductCreate,
    db: Session = Depends(get_db)
):
    """Create new product"""
    try:
        new_product = Product(**product.dict())
        db.add(new_product)
        db.commit()
        db.refresh(new_product)
        return {**new_product.to_dict(), "message": "Product created"}
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=400, detail=str(e))
```

### Step 3: Register Router in Main

**File:** `backend/app/main.py`

```python
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from backend.app.api.v1.products import router as products_router

app = FastAPI()

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(products_router)

@app.get("/")
async def root():
    return {"message": "API running"}
```

### Step 4: Test Endpoints

```bash
# List products
curl http://localhost:8000/api/v1/products

# Create product
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Test Product",
    "brand": "Test Brand",
    "category": "cleanser",
    "tags": ["gentle"]
  }'

# Reload rules (optional)
curl -X POST http://localhost:8000/api/v1/recommend/reload-rules
```

---

## Error Handling

**Common Errors & Solutions:**

### 400 Bad Request

```json
{
  "detail": "name: field required"
}
```

**Solution:** Verify all required fields are provided (name, brand)

### 404 Not Found

```json
{
  "detail": "Not Found"
}
```

**Solution:** Check endpoint URL matches API prefix (/api/v1/products)

### 422 Unprocessable Entity

```json
{
  "detail": [{ "loc": ["body", "name"], "msg": "field required" }]
}
```

**Solution:** Check request body matches Pydantic schema

### CORS Error

```
Access to XMLHttpRequest blocked by CORS policy
```

**Solution:** Add CORSMiddleware with correct allowed_origins

### 500 Internal Server Error

```json
{
  "detail": "Internal server error"
}
```

**Solution:** Check server logs, verify database connection

---

## Testing Integration

### Manual Testing

**1. Test GET endpoint:**

```bash
curl http://localhost:8000/api/v1/products

# Response should be:
{
  "products": [
    {
      "id": 1,
      "name": "Product 1",
      ...
    }
  ]
}
```

**2. Test POST endpoint:**

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CeraVe",
    "brand": "CeraVe",
    "category": "moisturizer"
  }'

# Response should be 201 Created with product data
```

**3. Test from Admin Panel:**

- Navigate to http://localhost:5173/admin
- Login with any token
- Try to add a product
- Check if it appears in list

### Unit Testing

```python
# backend/tests/test_products.py

import pytest
from fastapi.testclient import TestClient
from backend.app.main import app

client = TestClient(app)

def test_list_products():
    response = client.get("/api/v1/products")
    assert response.status_code == 200
    assert "products" in response.json()

def test_create_product():
    response = client.post("/api/v1/products", json={
        "name": "Test Product",
        "brand": "Test Brand",
        "category": "cleanser"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "Test Product"

def test_create_product_missing_name():
    response = client.post("/api/v1/products", json={
        "brand": "Test Brand",
        "category": "cleanser"
    })
    assert response.status_code == 422
```

---

## Performance Optimization

### 1. Pagination (for large product lists)

```python
@router.get("/products")
async def list_products(
    skip: int = 0,
    limit: int = 10,
    db: Session = Depends(get_db)
):
    products = db.query(Product).offset(skip).limit(limit).all()
    total = db.query(Product).count()
    return {
        "products": [p.to_dict() for p in products],
        "total": total,
        "skip": skip,
        "limit": limit
    }
```

### 2. Filtering

```python
@router.get("/products")
async def list_products(
    category: Optional[str] = None,
    brand: Optional[str] = None,
    db: Session = Depends(get_db)
):
    query = db.query(Product)
    if category:
        query = query.filter(Product.category == category)
    if brand:
        query = query.filter(Product.brand == brand)
    return {"products": [p.to_dict() for p in query.all()]}
```

### 3. Caching (for read-heavy workloads)

```python
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend

@router.get("/products")
@cached(expire=300)  # Cache for 5 minutes
async def list_products(db: Session = Depends(get_db)):
    products = db.query(Product).all()
    return {"products": [p.to_dict() for p in products]}
```

---

## Security Considerations

### 1. Input Validation

```python
from pydantic import validator

class ProductCreate(BaseModel):
    name: str
    brand: str

    @validator('name', 'brand')
    def name_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('must not be empty')
        return v
```

### 2. Rate Limiting

```python
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@router.post("/products")
@limiter.limit("10/minute")
async def create_product(...):
    ...
```

### 3. Authentication (Production)

```python
@router.post("/products")
async def create_product(
    product: ProductCreate,
    current_user: User = Depends(get_current_admin_user),
    db: Session = Depends(get_db)
):
    ...
```

---

## Deployment Checklist

- [ ] Database migrations created
- [ ] Endpoints tested locally
- [ ] CORS configured for production domain
- [ ] Error handling implemented
- [ ] Logging configured
- [ ] Rate limiting enabled
- [ ] Authentication implemented
- [ ] Input validation complete
- [ ] Database backups configured
- [ ] Monitoring set up

---

## Documentation Files

| File                          | Purpose                   |
| ----------------------------- | ------------------------- |
| `ADMIN_PAGE_DOCUMENTATION.md` | Frontend component guide  |
| `ADMIN_QUICKSTART.md`         | Quick start guide         |
| This file                     | Backend integration guide |

---

## Support & Questions

For issues with:

- **Frontend:** See `ADMIN_PAGE_DOCUMENTATION.md`
- **Backend:** This guide
- **Integration:** See examples above
- **Troubleshooting:** See Error Handling section

All endpoints use REST API pattern with JSON request/response format.
