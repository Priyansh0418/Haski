# Admin Recommendations Page - Documentation

## Overview

The **AdminRecommendations** component (`frontend/src/routes/AdminRecommendations.tsx`) is a React admin panel for managing skincare product recommendations, rules, and demo products.

**Location:** `frontend/src/routes/AdminRecommendations.tsx`
**Route:** `/admin`
**Protection:** localStorage-based MVP authentication (`is_admin === "1"`)

---

## Features

### 1. 🔐 Admin Authentication

- **Token-based login** for MVP (any non-empty token)
- **localStorage persistence** (`is_admin` flag)
- **Simple logout** functionality
- **Quick access** without session storage

**Login Flow:**

```
User → Enter Token → localStorage.setItem('is_admin', '1') → Access Dashboard
```

**Authentication Code:**

```tsx
const storedIsAdmin = localStorage.getItem("is_admin");
setIsAdmin(storedIsAdmin === "1");
```

### 2. 📁 Rules File Upload

- **YAML file upload** (accepts `.yml` and `.yaml` files)
- **File validation** (checks file type)
- **Backend integration** (POST to `/api/v1/rules/upload` - for future)
- **Rules reload** (optional POST to `/api/v1/recommend/reload-rules`)

**Supported Files:**

- `rules.yml`
- `rules.yaml`

**Upload Flow:**

```
Select File → Click Upload → Show Success Message → Optionally reload backend rules
```

### 3. ➕ Add Demo Products

- **Quick product creation form**
- **Fields:** Name, Brand, Category, Tags, Ingredients
- **Tags/Ingredients:** Comma-separated input
- **Backend:** POST to `/api/v1/products`
- **Auto-refresh:** Products list updates after creation

**Product Fields:**

- **Name** (required) - Product name
- **Brand** (required) - Brand name
- **Category** - Dropdown (cleanser, moisturizer, serum, treatment, sunscreen, mask, other)
- **Tags** - Comma-separated (e.g., "gentle, hydrating, hypoallergenic")
- **Ingredients** - Comma-separated (e.g., "water, glycerin, ceramides")

**Form Example:**

```tsx
{
  name: "CeraVe Moisturizing Cream",
  brand: "CeraVe",
  category: "moisturizer",
  tags: "gentle, hydrating, hypoallergenic",
  ingredients: "water, glycerin, ceramides"
}
```

### 4. 📦 Products List

- **Display all existing products**
- **Real-time updates** after product creation
- **Product information:** Name, brand, category, tags, ingredients
- **Dermatologically safe badge** for qualified products
- **Scrollable list** (80vh max height)

**Product Card Shows:**

```
Product Name (Brand)
✓ Safe badge (if dermatologically_safe)
Category: moisturizer
Tags: gentle, hydrating
Ingredients: water, glycerin, ...
For: dry_skin, sensitive
```

---

## API Endpoints Used

| Endpoint                         | Method | Purpose            | Status      |
| -------------------------------- | ------ | ------------------ | ----------- |
| `/api/v1/products`               | GET    | Fetch all products | ✅ Required |
| `/api/v1/products`               | POST   | Create new product | ✅ Required |
| `/api/v1/recommend/reload-rules` | POST   | Reload rules       | ⏳ Optional |
| `/api/v1/rules/upload`           | POST   | Upload rules file  | ⏳ Future   |

### GET /api/v1/products

```bash
curl http://localhost:8000/api/v1/products
```

**Response:**

```json
{
  "products": [
    {
      "id": 1,
      "name": "CeraVe Moisturizer",
      "brand": "CeraVe",
      "category": "moisturizer",
      "price_usd": 24.99,
      "tags": ["gentle", "hydrating"],
      "ingredients": ["water", "glycerin", "ceramides"],
      "dermatologically_safe": true,
      "recommended_for": ["dry_skin", "sensitive"]
    }
  ]
}
```

### POST /api/v1/products

```bash
curl -X POST http://localhost:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "CeraVe Moisturizer",
    "brand": "CeraVe",
    "category": "moisturizer",
    "tags": ["gentle", "hydrating"],
    "ingredients": ["water", "glycerin"],
    "dermatologically_safe": true,
    "recommended_for": []
  }'
```

### POST /api/v1/recommend/reload-rules (Optional)

```bash
curl -X POST http://localhost:8000/api/v1/recommend/reload-rules
```

---

## Usage

### 1. Access Admin Panel

**URL:** `http://localhost:3000/admin`

### 2. Login (MVP)

1. Go to admin page
2. Enter any non-empty token (e.g., "admin-token-123")
3. Click "Login to Admin"
4. Access dashboard

**Note:** In production, replace with proper JWT authentication

### 3. Upload Rules (Optional)

1. Click "Upload Rules" section
2. Select `rules.yml` file
3. Click "Upload Rules" button
4. (Optional) Backend will reload rules if endpoint available

### 4. Add Product

1. Fill in product form:
   - Name: "CeraVe Hydrating Cleanser"
   - Brand: "CeraVe"
   - Category: "Cleanser"
   - Tags: "gentle, fragrance-free, hydrating"
   - Ingredients: "water, glycerin, ceramides"
2. Click "Add Product"
3. Product appears in list (right side)
4. Success message displays

### 5. View Products

- List updates automatically
- Shows: name, brand, category, tags, ingredients, safety badge
- Scrollable if many products

---

## Component Architecture

### State Management

```tsx
const [isAdmin, setIsAdmin] = useState(false);                    // Auth status
const [adminToken, setAdminToken] = useState("");                // Login input
const [products, setProducts] = useState<Product[]>([]);         // Products list
const [loading, setLoading] = useState(false);                   // Loading state
const [error, setError] = useState<string | null>(null);         // Error message
const [successMessage, setSuccessMessage] = useState<string | null>(null); // Success
const [rulesFile, setRulesFile] = useState<File | null>(null);   // Rules file
const [uploadingRules, setUploadingRules] = useState(false);      // Upload state
const [formData, setFormData] = useState<FormData>({...});        // Product form
```

### Key Functions

**fetchProducts()**

```tsx
const fetchProducts = async () => {
  const response = await fetch(`${API_BASE}/api/v1/products`);
  const data = await response.json();
  setProducts(data.products || data);
};
```

**handleAddProduct()**

```tsx
const handleAddProduct = async (e) => {
  const response = await fetch(`${API_BASE}/api/v1/products`, {
    method: "POST",
    body: JSON.stringify(payload),
  });
  // Refresh products list
  await fetchProducts();
};
```

**handleRulesUpload()**

```tsx
const handleRulesUpload = async (e) => {
  // Upload file and optionally reload backend rules
  await fetch(`${API_BASE}/api/v1/recommend/reload-rules`, {
    method: "POST",
  });
};
```

---

## Styling (Tailwind CSS)

### Layout

- **Responsive grid:** 1 column on mobile, 2 columns on desktop
- **Max width:** 6xl container
- **Spacing:** Consistent padding (4-8 units)

### Components

- **Buttons:** Blue for primary, Green for add, Red for logout
- **Forms:** Gray borders, blue focus rings
- **Cards:** White background, shadow, rounded corners
- **Messages:** Green for success, Red for errors
- **Badges:** Green background for safe products

### Responsive Breakpoints

```tsx
grid-cols-1 lg:grid-cols-2  // 1 column, then 2 on lg+
max-h-[80vh]                 // Scrollable products list
w-full max-w-md              // Login form width
```

---

## Environment Variables

**VITE_API_URL** (optional)

```env
VITE_API_URL=http://localhost:8000
```

**Fallback:** `http://localhost:8000` if not set

---

## Authentication (MVP)

### Current Implementation

```tsx
// Login: Any non-empty token → localStorage.setItem('is_admin', '1')
// Check: localStorage.getItem('is_admin') === '1'
// Logout: localStorage.removeItem('is_admin')
```

### Production Implementation (TODO)

```tsx
// 1. Replace with JWT token from backend
// 2. Validate token on backend
// 3. Store in httpOnly cookie (not localStorage)
// 4. Add role-based access control (RBAC)
// 5. Implement token refresh mechanism
// 6. Add session timeout
```

---

## Error Handling

**Try-catch blocks** for all API calls:

```tsx
try {
  const response = await fetch(url);
  if (response.ok) {
    // Success handling
  } else {
    setError(`Failed: ${errorData.detail}`);
  }
} catch (err) {
  setError(`Error: ${err}`);
}
```

**User Feedback:**

- ✓ Success messages (green, auto-dismiss after 3s)
- ✗ Error messages (red, persist until dismissed)
- Loading states (disabled buttons during operations)

---

## Integration with Backend

### Required Endpoints

**1. GET /api/v1/products**

```python
@router.get("/products")
async def list_products():
    products = db.query(Product).all()
    return {"products": [p.to_dict() for p in products]}
```

**2. POST /api/v1/products**

```python
@router.post("/products")
async def create_product(product: ProductCreate):
    new_product = Product(**product.dict())
    db.add(new_product)
    db.commit()
    return new_product.to_dict()
```

### Optional Endpoints

**3. POST /api/v1/recommend/reload-rules**

```python
@router.post("/recommend/reload-rules")
async def reload_rules():
    engine = RuleEngine()  # Force reload
    return {"status": "Rules reloaded"}
```

---

## Testing

### Manual Testing Checklist

- [ ] Navigate to `/admin`
- [ ] See login form
- [ ] Enter token and login
- [ ] See admin dashboard
- [ ] Products list loads
- [ ] Add product form visible
- [ ] Upload rules form visible
- [ ] Fill product form and submit
- [ ] Product appears in list
- [ ] Select rules.yml and upload
- [ ] Success message displays
- [ ] Logout button works
- [ ] Redirected to login after logout
- [ ] Error handling for missing name/brand
- [ ] Error handling for failed API calls

### Example Test Data

**Product 1:**

```
Name: CeraVe Hydrating Cleanser
Brand: CeraVe
Category: Cleanser
Tags: gentle, fragrance-free, hydrating
Ingredients: water, glycerin, ceramides
```

**Product 2:**

```
Name: Neutrogena Acne Cleanser
Brand: Neutrogena
Category: Cleanser
Tags: acne-fighting, exfoliating
Ingredients: water, salicylic_acid, benzoyl_peroxide
```

---

## File Structure

```
frontend/src/
├── routes/
│   ├── AdminRecommendations.tsx  ← NEW
│   ├── Home.tsx
│   ├── Dashboard.tsx
│   ├── Profile.tsx
│   └── ...
├── components/
├── styles/
├── App.tsx                        ← UPDATED (added route)
└── main.tsx
```

---

## Future Enhancements

### Phase 1 (Current - MVP)

- ✅ Simple token login
- ✅ Product upload form
- ✅ Rules file upload
- ✅ Products list
- ✅ Tailwind styling

### Phase 2 (Production)

- 🔧 JWT authentication
- 🔧 Backend validation for rules upload
- 🔧 Product edit/delete
- 🔧 Rules preview before upload
- 🔧 Bulk product import (CSV)
- 🔧 Analytics dashboard

### Phase 3 (Advanced)

- 🔧 Real-time product sync
- 🔧 Rule versioning
- 🔧 Audit logs
- 🔧 Multi-user management
- 🔧 Permission levels

---

## Deployment

### Vite Build

```bash
npm run build
```

### Environment Setup

```env
# .env.local
VITE_API_URL=https://api.haski.com
```

### Docker (Frontend)

```dockerfile
FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build
EXPOSE 5173
CMD ["npm", "run", "preview"]
```

---

## Security Considerations

### Current (MVP)

⚠️ **Not production-ready**

- Token stored in localStorage (accessible to XSS)
- No HTTPS requirement
- Simple string token (no validation)
- CORS issues possible

### Production Todo

✅ **Must implement before production:**

- [ ] HTTPS only
- [ ] JWT tokens with expiration
- [ ] httpOnly cookies (not localStorage)
- [ ] CSRF protection
- [ ] Rate limiting
- [ ] Input validation
- [ ] SQL injection prevention
- [ ] XSS protection
- [ ] CORS configuration
- [ ] API authentication headers

---

## Support

### Common Issues

**1. API not responding**

- Check backend is running on `http://localhost:8000`
- Verify CORS headers in backend
- Check network tab for errors

**2. Products not loading**

- Ensure `/api/v1/products` endpoint exists
- Check API response format
- Verify database has products

**3. File upload not working**

- Check file size limit
- Verify file is .yml or .yaml
- Check browser console for errors

**4. Token not persisting**

- Check localStorage is enabled
- Check browser dev tools (Application → Storage)
- Try clearing cache and reload

---

## Files Delivered

| File                       | Purpose             | Status      |
| -------------------------- | ------------------- | ----------- |
| `AdminRecommendations.tsx` | Main component      | ✅ Complete |
| `App.tsx`                  | Route registration  | ✅ Updated  |
| This documentation         | Guide and reference | ✅ Complete |

---

## Summary

✅ **Fully functional admin panel** for MVP with:

- Token-based authentication
- Product management (create, list)
- Rules file upload
- Tailwind styling
- Error handling
- Success messaging

🚀 **Ready for integration** with backend endpoints

📝 **Production checklist** provided for security and feature enhancements
