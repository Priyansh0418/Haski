# Products API - Quick Reference

## Base URL
```
http://localhost:8000/api/v1/products
```

## Endpoints

### 1. List Products
```
GET /products
```

**Parameters:**
- `tag` - Filter by tag (e.g., "cleanser")
- `ingredient` - Filter by ingredient (e.g., "salicylic acid")
- `category` - Filter by category (e.g., "moisturizer")
- `min_rating` - Minimum rating 0-5 (e.g., "4.5")
- `max_price` - Maximum price USD (e.g., "15")
- `dermatologically_safe` - true/false
- `search` - Search name/brand (e.g., "cerave")
- `sort_by` - rating|price|newest|name (default: "rating")
- `sort_order` - asc|desc (default: "desc")
- `page` - Page number (default: 1)
- `page_size` - Items per page, max 100 (default: 20)

**Examples:**
```bash
# Get all products
GET /products

# Get page 2 with 10 items
GET /products?page=2&page_size=10

# Filter by tag
GET /products?tag=cleanser

# Filter by price and rating
GET /products?max_price=15&min_rating=4

# Search and sort
GET /products?search=ordinary&sort_by=rating&sort_order=desc

# Complex filter
GET /products?tag=bha&category=treatment&max_price=20&min_rating=4&sort_by=price&sort_order=asc
```

**Response:**
```json
{
  "total": 42,
  "page": 1,
  "page_size": 20,
  "total_pages": 3,
  "products": [
    {
      "id": 1,
      "name": "Salicylic Acid 2%",
      "brand": "The Ordinary",
      "category": "treatment",
      "price_usd": 5.90,
      "avg_rating": 4.3,
      "review_count": 5890,
      "tags": ["exfoliating", "bha", "acne-fighting"],
      "ingredients": ["water", "salicylic acid"],
      ...
    }
  ]
}
```

---

### 2. Get Product Details
```
GET /products/{id}
```

**Example:**
```bash
GET /products/1
```

**Response:**
```json
{
  "id": 1,
  "name": "Salicylic Acid 2%",
  "brand": "The Ordinary",
  "category": "treatment",
  "price_usd": 5.90,
  "url": "https://theordinary.com",
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

---

### 3. Create Product (Admin Only)
```
POST /products
Authorization: Bearer {token}
Content-Type: application/json
```

**Request Body:**
```json
{
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
}
```

**Required Fields:**
- `name`
- `brand`
- `category`
- `dermatologically_safe` (optional, default: true)

**Response (201 Created):**
Same as Get Product Details, including generated ID.

**Errors:**
- `403 Forbidden` - Not admin
- `400 Bad Request` - Duplicate external_id
- `422 Validation Error` - Missing/invalid fields

---

### 4. List Available Tags
```
GET /products/search/tags
```

**Response:**
```json
{
  "tags": ["acne-fighting", "BHA", "cleanser", "exfoliating", ...],
  "total": 24
}
```

---

### 5. List Available Ingredients
```
GET /products/search/ingredients
```

**Response:**
```json
{
  "ingredients": ["ceramides", "glycerin", "salicylic acid", ...],
  "total": 156
}
```

---

### 6. Get Category Statistics
```
GET /products/stats/categories
```

**Response:**
```json
{
  "categories": {
    "cleanser": 12,
    "moisturizer": 8,
    "treatment": 22
  },
  "total": 42
}
```

---

## Common Use Cases

### Browse All Products
```bash
curl "http://localhost:8000/api/v1/products/products"
```

### Find Exfoliating Products
```bash
curl "http://localhost:8000/api/v1/products/products?tag=exfoliating"
```

### Find BHA Products Under $10
```bash
curl "http://localhost:8000/api/v1/products/products?tag=bha&max_price=10"
```

### Search for The Ordinary
```bash
curl "http://localhost:8000/api/v1/products/products?search=ordinary&page_size=50"
```

### Get Highest Rated Products
```bash
curl "http://localhost:8000/api/v1/products/products?sort_by=rating&sort_order=desc"
```

### Get Cheapest Products
```bash
curl "http://localhost:8000/api/v1/products/products?sort_by=price&sort_order=asc"
```

### Get Newest Products
```bash
curl "http://localhost:8000/api/v1/products/products?sort_by=newest"
```

### Find Products with Specific Ingredient
```bash
curl "http://localhost:8000/api/v1/products/products?ingredient=salicylic%20acid"
```

### Find Safe Products for Sensitive Skin
```bash
curl "http://localhost:8000/api/v1/products/products?dermatologically_safe=true&tag=gentle"
```

### Paginate Results (10 per page)
```bash
# Page 1
curl "http://localhost:8000/api/v1/products/products?page_size=10"

# Page 2
curl "http://localhost:8000/api/v1/products/products?page=2&page_size=10"

# Page 3
curl "http://localhost:8000/api/v1/products/products?page=3&page_size=10"
```

---

## JavaScript Fetch Examples

### List Products
```javascript
const response = await fetch('/api/v1/products/products');
const data = await response.json();
console.log(data.products);
```

### With Filters
```javascript
const params = new URLSearchParams({
  tag: 'cleanser',
  max_price: 20,
  sort_by: 'rating',
  page_size: 15
});

const response = await fetch(`/api/v1/products/products?${params}`);
const data = await response.json();
```

### Get Product Details
```javascript
const productId = 1;
const response = await fetch(`/api/v1/products/products/${productId}`);
const product = await response.json();
console.log(product);
```

### Create Product (Admin)
```javascript
const token = localStorage.getItem('access_token');

const newProduct = {
  name: "New Cleanser",
  brand: "Test Brand",
  category: "cleanser",
  price_usd: 12.99,
  tags: ["hydrating", "gentle"],
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
  console.log('Created product ID:', created.id);
} else {
  console.error('Error:', response.status);
}
```

---

## Error Codes

| Code | Meaning | Cause |
|------|---------|-------|
| 200 | OK | Successful GET |
| 201 | Created | Successful POST |
| 400 | Bad Request | Duplicate external_id |
| 403 | Forbidden | Not admin / Not authenticated |
| 404 | Not Found | Product ID doesn't exist |
| 422 | Unprocessable Entity | Validation error |
| 500 | Server Error | Internal error |

---

## Important Notes

### Admin Access
Currently uses email-based admin check. Admin emails:
- `admin@skinhaira.ai`
- `admin@example.com`
- `priyansh0418@gmail.com`

Future: Implement proper `is_admin` role field in User model.

### Data Formats
- **Prices:** In USD (e.g., 5.90), stored as cents in DB (e.g., 590)
- **Ratings:** On 5-point scale (e.g., 4.3), stored as 0-500 in DB (e.g., 430)
- **Tags:** Lowercase in database and API responses
- **Timestamps:** ISO 8601 format (e.g., "2024-01-15T10:30:00")

### Rate Limiting
- No rate limiting currently implemented
- Page size limited to max 100 items

---

## Integration Points

### Recommender System
- `recommend.py` queries products for recommendations
- Uses category, ingredients, tags for filtering

### Feedback System
- `feedback.py` users rate recommended products
- Products endpoint allows browsing full catalog

### ML API
- ML models output recommended product categories
- Products API provides actual products for categories

---

## Performance Tips

1. **Pagination:** Always use pagination for large datasets
   ```bash
   ?page=1&page_size=20  # Efficient
   ```

2. **Filtering:** More specific filters are faster
   ```bash
   ?tag=cleanser&category=moisturizer  # Faster than just one filter
   ```

3. **Sorting:** Sort by indexed fields for speed
   - Indexed: rating, price, name, category
   - Use: `?sort_by=rating` instead of custom fields

4. **Avoid:** Large page sizes on slow connections
   ```bash
   ?page_size=1000  # Slow, use pagination instead
   ```

---

## Troubleshooting

### No Products Returned
1. Check if database has products loaded
2. Verify filters are correct
3. Try without filters: `GET /products`

### 403 Forbidden on POST
1. Ensure authentication token is provided
2. Verify user email is in admin list
3. Check token hasn't expired

### 404 Not Found
1. Verify product ID is correct
2. Product may have been deleted
3. Check product exists: `GET /products?search=name`

### 422 Validation Error
1. Check required fields are present
2. Verify field types (string, number, boolean)
3. Review error details in response

---

## Support & Documentation

- Full API Documentation: `PRODUCTS_API_DOCUMENTATION.md`
- Test Examples: `test_products.py`
- Implementation: `products.py`

For issues, check logs in:
```
backend/logs/app.log
```
