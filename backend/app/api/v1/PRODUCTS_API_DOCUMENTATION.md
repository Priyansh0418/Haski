# Products API Documentation

Complete reference for the Products Management API endpoints.

**Base URL:** `http://localhost:8000/api/v1/products`

---

## Table of Contents

1. [Endpoints Overview](#endpoints-overview)
2. [List Products](#list-products)
3. [Get Product Details](#get-product-details)
4. [Create Product](#create-product)
5. [Utility Endpoints](#utility-endpoints)
6. [Filtering Guide](#filtering-guide)
7. [Pagination Guide](#pagination-guide)
8. [Response Formats](#response-formats)
9. [Error Handling](#error-handling)
10. [Examples](#examples)

---

## Endpoints Overview

| Method | Endpoint | Description | Auth Required |
|--------|----------|-------------|----------------|
| GET | `/products` | List products with filtering & pagination | No |
| GET | `/products/{id}` | Get single product details | No |
| POST | `/products` | Create new product (admin only) | Yes (Admin) |
| GET | `/products/search/tags` | Get all available tags | No |
| GET | `/products/search/ingredients` | Get all available ingredients | No |
| GET | `/products/stats/categories` | Get category statistics | No |

---

## List Products

### Request

**Endpoint:** `GET /products`

**Query Parameters:**

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `tag` | string | No | Filter by product tag (e.g., "cleanser", "acne-fighting") |
| `ingredient` | string | No | Filter by ingredient name (case-insensitive) |
| `category` | string | No | Filter by category (e.g., "cleanser", "moisturizer") |
| `min_rating` | float | No | Minimum rating (0-5 scale) |
| `max_price` | float | No | Maximum price in USD |
| `dermatologically_safe` | boolean | No | Filter by dermatological safety |
| `search` | string | No | Full-text search by product name or brand |
| `sort_by` | string | No | Sort by: rating (default), price, newest, name |
| `sort_order` | string | No | Sort order: desc (default) or asc |
| `page` | integer | No | Page number (1-indexed, default: 1) |
| `page_size` | integer | No | Items per page (1-100, default: 20) |

**Example Requests:**

```bash
# List all products (default pagination)
curl -X GET "http://localhost:8000/api/v1/products/products"

# List cleansers with pagination
curl -X GET "http://localhost:8000/api/v1/products/products?tag=cleanser&page_size=10"

# Filter by ingredient and rating
curl -X GET "http://localhost:8000/api/v1/products/products?ingredient=salicylic%20acid&min_rating=4"

# Search for brand with sorting
curl -X GET "http://localhost:8000/api/v1/products/products?search=cerave&sort_by=price&sort_order=asc"

# Complex filter: BHA exfoliants under $15
curl -X GET "http://localhost:8000/api/v1/products/products?tag=bha&max_price=15&sort_by=rating"
```

### Response

**Status Code:** `200 OK`

**Response Format:**

```json
{
  "total": 5,
  "page": 1,
  "page_size": 20,
  "total_pages": 1,
  "products": [
    {
      "id": 1,
      "name": "Salicylic Acid 2%",
      "brand": "The Ordinary",
      "category": "treatment",
      "price_usd": 5.90,
      "url": "https://theordinary.deciem.com",
      "ingredients": ["water", "salicylic acid"],
      "tags": ["exfoliating", "bha", "acne-fighting"],
      "dermatologically_safe": true,
      "recommended_for": ["acne", "blackheads"],
      "avoid_for": ["very_sensitive"],
      "avg_rating": 4.3,
      "review_count": 5890,
      "source": "the_ordinary",
      "external_id": "ordinary_sa_001",
      "created_at": "2024-01-15T10:30:00"
    },
    ...
  ]
}
```

**Response Fields:**

| Field | Type | Description |
|-------|------|-------------|
| `total` | integer | Total number of products matching filters |
| `page` | integer | Current page number |
| `page_size` | integer | Items per page |
| `total_pages` | integer | Total number of pages |
| `products` | array | Array of ProductResponse objects |

---

## Get Product Details

### Request

**Endpoint:** `GET /products/{id}`

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| `id` | integer | Product ID |

**Example Requests:**

```bash
# Get product with ID 1
curl -X GET "http://localhost:8000/api/v1/products/products/1"

# Get product with ID 42
curl -X GET "http://localhost:8000/api/v1/products/products/42"
```

### Response

**Status Code:** `200 OK`

**Response Format:**

```json
{
  "id": 1,
  "name": "Salicylic Acid 2%",
  "brand": "The Ordinary",
  "category": "treatment",
  "price_usd": 5.90,
  "url": "https://theordinary.deciem.com",
  "ingredients": ["water", "salicylic acid"],
  "tags": ["exfoliating", "bha", "acne-fighting"],
  "dermatologically_safe": true,
  "recommended_for": ["acne", "blackheads"],
  "avoid_for": ["very_sensitive"],
  "avg_rating": 4.3,
  "review_count": 5890,
  "source": "the_ordinary",
  "external_id": "ordinary_sa_001",
  "created_at": "2024-01-15T10:30:00"
}
```

**Error Response (404):**

```json
{
  "detail": "Product 99999 not found"
}
```

---

## Create Product

### Request

**Endpoint:** `POST /products`

**Authentication:** Required (Admin only)

**Headers:**

```
Authorization: Bearer {access_token}
Content-Type: application/json
```

**Request Body:**

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| `name` | string | Yes | Product name |
| `brand` | string | Yes | Brand name |
| `category` | string | Yes | Product category (e.g., "cleanser", "moisturizer") |
| `price_usd` | float | No | Price in USD |
| `url` | string | No | Product URL |
| `ingredients` | array[string] | No | List of ingredients |
| `tags` | array[string] | No | List of tags (automatically lowercased) |
| `dermatologically_safe` | boolean | No | Dermatologically safe (default: true) |
| `recommended_for` | array[string] | No | Recommended for skin types |
| `avoid_for` | array[string] | No | Should avoid if conditions |
| `avg_rating` | float | No | Average rating (0-5 scale) |
| `review_count` | integer | No | Number of reviews (default: 0) |
| `source` | string | No | Product source/origin |
| `external_id` | string | No | External ID for tracking |

**Example Request:**

```bash
curl -X POST "http://localhost:8000/api/v1/products/products" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Salicylic Acid 2%",
    "brand": "The Ordinary",
    "category": "treatment",
    "price_usd": 5.90,
    "url": "https://theordinary.deciem.com",
    "ingredients": ["water", "salicylic acid"],
    "tags": ["exfoliating", "BHA", "acne-fighting"],
    "dermatologically_safe": true,
    "recommended_for": ["acne", "blackheads"],
    "avoid_for": ["very_sensitive"],
    "avg_rating": 4.3,
    "review_count": 5890,
    "source": "the_ordinary",
    "external_id": "ordinary_sa_001"
  }'
```

### Response

**Status Code:** `201 Created`

**Response Format:** Same as [Get Product Details](#get-product-details)

**Error Responses:**

- **403 Forbidden** (not admin):
  ```json
  {"detail": "Admin access required"}
  ```

- **400 Bad Request** (duplicate external_id):
  ```json
  {"detail": "Product with external_id 'X' already exists"}
  ```

- **422 Unprocessable Entity** (validation error):
  ```json
  {
    "detail": [
      {
        "loc": ["body", "name"],
        "msg": "field required",
        "type": "value_error.missing"
      }
    ]
  }
  ```

---

## Utility Endpoints

### List Available Tags

**Endpoint:** `GET /products/search/tags`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/products/products/search/tags"
```

**Response:**

```json
{
  "tags": [
    "acne-fighting",
    "anti-aging",
    "anti-inflammatory",
    "BHA",
    "cleanser",
    "exfoliating",
    "gentle",
    "hydrating",
    "pore-minimizing",
    "safe-for-sensitive"
  ],
  "total": 10
}
```

---

### List Available Ingredients

**Endpoint:** `GET /products/search/ingredients`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/products/products/search/ingredients"
```

**Response:**

```json
{
  "ingredients": [
    "ceramides",
    "cetyl alcohol",
    "glycerin",
    "glycolic acid",
    "hyaluronic acid",
    "niacinamide",
    "salicylic acid",
    "water"
  ],
  "total": 8
}
```

---

### Get Category Statistics

**Endpoint:** `GET /products/stats/categories`

**Example Request:**

```bash
curl -X GET "http://localhost:8000/api/v1/products/stats/categories"
```

**Response:**

```json
{
  "categories": {
    "cleanser": 3,
    "moisturizer": 2,
    "treatment": 5
  },
  "total": 10
}
```

---

## Filtering Guide

### Filter by Tag

Tags are predefined labels for products (e.g., "cleanser", "acne-fighting").

**Example:**

```bash
# Get all exfoliating products
curl "http://localhost:8000/api/v1/products/products?tag=exfoliating"

# Get cleansers (case-insensitive)
curl "http://localhost:8000/api/v1/products/products?tag=CLEANSER"
```

### Filter by Ingredient

Search for products containing specific ingredients.

**Example:**

```bash
# Get products with salicylic acid
curl "http://localhost:8000/api/v1/products/products?ingredient=salicylic%20acid"

# Get products with niacinamide (case-insensitive)
curl "http://localhost:8000/api/v1/products/products?ingredient=niacinamide"
```

### Filter by Category

Match exact product categories.

**Example:**

```bash
# Get all moisturizers
curl "http://localhost:8000/api/v1/products/products?category=moisturizer"

# Get all treatments
curl "http://localhost:8000/api/v1/products/products?category=treatment"
```

### Filter by Rating

Filter products by minimum average rating.

**Example:**

```bash
# Get products rated 4.5 stars or higher
curl "http://localhost:8000/api/v1/products/products?min_rating=4.5"

# Get highly-rated products (4.0+)
curl "http://localhost:8000/api/v1/products/products?min_rating=4"
```

### Filter by Price

Filter products by maximum price.

**Example:**

```bash
# Get products under $10
curl "http://localhost:8000/api/v1/products/products?max_price=10"

# Get budget products under $5
curl "http://localhost:8000/api/v1/products/products?max_price=5"
```

### Filter by Dermatological Safety

Filter by dermatological approval.

**Example:**

```bash
# Get dermatologically safe products
curl "http://localhost:8000/api/v1/products/products?dermatologically_safe=true"

# Get products that are NOT dermatologically safe
curl "http://localhost:8000/api/v1/products/products?dermatologically_safe=false"
```

### Search by Name/Brand

Full-text search in product names and brands.

**Example:**

```bash
# Search for "The Ordinary" products
curl "http://localhost:8000/api/v1/products/products?search=the%20ordinary"

# Search for "CeraVe"
curl "http://localhost:8000/api/v1/products/products?search=cerave"

# Search for products with "Acid" in name
curl "http://localhost:8000/api/v1/products/products?search=acid"
```

### Combine Multiple Filters

Filters are combined with AND logic.

**Example:**

```bash
# Get BHA exfoliants under $15 rated 4+ stars
curl "http://localhost:8000/api/v1/products/products?tag=bha&category=treatment&max_price=15&min_rating=4"

# Get safe hydrating cleansers from CeraVe
curl "http://localhost:8000/api/v1/products/products?tag=hydrating&category=cleanser&search=cerave&dermatologically_safe=true"
```

---

## Pagination Guide

### Default Pagination

```bash
# Default: page 1, 20 items per page
curl "http://localhost:8000/api/v1/products/products"
```

### Custom Page Size

```bash
# Get 10 items per page
curl "http://localhost:8000/api/v1/products/products?page_size=10"

# Get 50 items per page (maximum)
curl "http://localhost:8000/api/v1/products/products?page_size=50"
```

### Navigate Pages

```bash
# Go to page 2
curl "http://localhost:8000/api/v1/products/products?page=2"

# Go to page 3 with custom size
curl "http://localhost:8000/api/v1/products/products?page=3&page_size=10"
```

### Pagination Response Example

```json
{
  "total": 42,           # Total products matching filter
  "page": 2,             # Current page number
  "page_size": 10,       # Items per page
  "total_pages": 5,      # Total number of pages
  "products": [...]      # Array of products
}
```

**Calculate if more pages:** `total > (page * page_size)`

---

## Response Formats

### Product Response Object

```json
{
  "id": 1,
  "name": "Salicylic Acid 2%",
  "brand": "The Ordinary",
  "category": "treatment",
  "price_usd": 5.90,
  "url": "https://theordinary.deciem.com",
  "ingredients": ["water", "salicylic acid"],
  "tags": ["exfoliating", "bha", "acne-fighting"],
  "dermatologically_safe": true,
  "recommended_for": ["acne", "blackheads"],
  "avoid_for": ["very_sensitive"],
  "avg_rating": 4.3,
  "review_count": 5890,
  "source": "the_ordinary",
  "external_id": "ordinary_sa_001",
  "created_at": "2024-01-15T10:30:00"
}
```

### Data Type Conversions

**Prices:** Stored as cents in database, returned as USD dollars

```
Database: 590  →  Response: 5.90
Database: 1590 →  Response: 15.90
```

**Ratings:** Stored as 0-500 scale, returned as 0-5 scale

```
Database: 430  →  Response: 4.3
Database: 480  →  Response: 4.8
Database: 500  →  Response: 5.0
```

---

## Error Handling

### HTTP Status Codes

| Status | Meaning | Typical Cause |
|--------|---------|---------------|
| 200 | OK | Successful GET request |
| 201 | Created | Successful POST request |
| 400 | Bad Request | Invalid filter values, duplicate external_id |
| 403 | Forbidden | Not authenticated/authorized (admin required) |
| 404 | Not Found | Product ID doesn't exist |
| 422 | Unprocessable Entity | Invalid request body (validation error) |
| 500 | Internal Server Error | Server error (check logs) |

### Common Error Responses

**Product Not Found (404):**

```json
{
  "detail": "Product 99999 not found"
}
```

**Not Admin (403):**

```json
{
  "detail": "Admin access required"
}
```

**Duplicate Product (400):**

```json
{
  "detail": "Product with external_id 'ordinary_sa_001' already exists"
}
```

**Validation Error (422):**

```json
{
  "detail": [
    {
      "loc": ["body", "name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

**Invalid Page Size (422):**

```json
{
  "detail": [
    {
      "loc": ["query", "page_size"],
      "msg": "ensure this value is less than or equal to 100",
      "type": "value_error.number.not_le"
    }
  ]
}
```

---

## Examples

### Frontend Integration Examples

#### JavaScript/Fetch

**List Products with Filters:**

```javascript
// Fetch BHA products under $15 sorted by rating
const params = new URLSearchParams({
  tag: 'bha',
  max_price: 15,
  sort_by: 'rating',
  sort_order: 'desc',
  page_size: 20
});

const response = await fetch(
  `/api/v1/products/products?${params}`,
  { method: 'GET' }
);
const data = await response.json();
console.log(data.products);
```

**Get Product Details:**

```javascript
const productId = 1;
const response = await fetch(`/api/v1/products/products/${productId}`);
const product = await response.json();
console.log(`${product.brand} - ${product.name} ($${product.price_usd})`);
```

**Create Product (Admin):**

```javascript
const token = localStorage.getItem('access_token');

const newProduct = {
  name: "New Cleanser",
  brand: "Test Brand",
  category: "cleanser",
  price_usd: 12.99,
  tags: ["gentle", "hydrating"],
  dermatologically_safe: true
};

const response = await fetch('/api/v1/products/products', {
  method: 'POST',
  headers: {
    'Authorization': `Bearer ${token}`,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify(newProduct)
});

if (response.status === 201) {
  const created = await response.json();
  console.log(`Created product: ${created.name} (ID: ${created.id})`);
}
```

#### React Component Example

```tsx
import { useState, useEffect } from 'react';

function ProductCatalog() {
  const [products, setProducts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filters, setFilters] = useState({
    tag: '',
    category: '',
    max_price: null,
    page: 1,
    page_size: 20
  });

  useEffect(() => {
    fetchProducts();
  }, [filters]);

  const fetchProducts = async () => {
    const params = new URLSearchParams(
      Object.fromEntries(Object.entries(filters).filter(([, v]) => v))
    );
    
    const response = await fetch(`/api/v1/products/products?${params}`);
    const data = await response.json();
    setProducts(data.products);
    setLoading(false);
  };

  return (
    <div>
      <select onChange={(e) => setFilters({...filters, tag: e.target.value})}>
        <option value="">All Tags</option>
        <option value="cleanser">Cleanser</option>
        <option value="exfoliating">Exfoliating</option>
      </select>

      {loading ? <div>Loading...</div> : (
        <div>
          {products.map(product => (
            <div key={product.id}>
              <h3>{product.name}</h3>
              <p>{product.brand} - ${product.price_usd}</p>
              <p>Rating: {product.avg_rating}/5 ({product.review_count} reviews)</p>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
```

---

## Limitations & Notes

### Admin Role Implementation

**Current Implementation:** Admin status is checked via hardcoded email addresses:

```python
ADMIN_EMAILS = [
    "admin@skinhaira.ai",
    "admin@example.com",
    "priyansh0418@gmail.com"
]
```

**Future Enhancement:** Add `is_admin` field to User model for proper role-based access control.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-01 | Initial release with filtering, pagination, and admin creation |

---

## Support

For issues or questions:
1. Check error responses and status codes above
2. Verify filter parameter names and values
3. Ensure authentication token is valid (for admin endpoints)
4. Check application logs for detailed error messages
