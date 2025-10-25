# 🚀 Authentication Quick Start Guide

**Get up and running with login/signup in 5 minutes!**

---

## ⚡ Quick Start

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload
# Runs on http://localhost:8000
```

### 2. Start the Frontend

```bash
cd frontend
npm install  # if needed
npm run dev
# Runs on http://localhost:5173
```

### 3. Test the Auth Flow

**Option A: Sign Up**

- Navigate to http://localhost:5173/signup
- Enter email, username, password
- Click "Sign Up"
- ✅ Redirects to dashboard

**Option B: Log In**

- Navigate to http://localhost:5173/login
- Enter email, password
- Click "Login"
- ✅ Redirects to dashboard

---

## 📁 File Structure

```
frontend/src/
├── lib/
│   └── api.ts                 ← API utilities (LOGIN/SIGNUP HERE)
├── context/
│   ├── AuthContext.tsx        ← Auth state management
│   └── useAuth.ts             ← Custom hook
├── routes/
│   ├── Login.tsx              ← Login form
│   ├── Signup.tsx             ← Signup form
│   └── Dashboard.tsx          ← Protected route example
└── App.tsx                    ← Routes setup
```

---

## 🔑 Core Functions

### Use Auth in Any Component

```typescript
import { useAuth } from "../context/useAuth";

export function MyComponent() {
  const { login, signup, user, logout, isAuthenticated } = useAuth();

  // Login
  const handleLogin = async () => {
    try {
      await login("user@example.com", "password123");
    } catch (error) {
      console.error("Login failed:", error.message);
    }
  };

  // Signup
  const handleSignup = async () => {
    try {
      await signup("user@example.com", "john", "password123");
    } catch (error) {
      console.error("Signup failed:", error.message);
    }
  };

  // Check auth status
  if (!isAuthenticated) {
    return <div>Not logged in</div>;
  }

  return (
    <div>
      <p>Hello {user?.username}!</p>
      <button onClick={logout}>Logout</button>
    </div>
  );
}
```

---

## 🌐 API Calls with Auth Token

Token is **automatically included** in all API calls:

```typescript
import * as api from "../lib/api";

export function Profile() {
  const handleLoadProfile = async () => {
    // Token is automatically included!
    const profile = await api.getProfile();
    console.log(profile);
  };

  return <button onClick={handleLoadProfile}>Load Profile</button>;
}
```

Available API functions:

- `api.getProfile()` - Get user profile
- `api.updateProfile(data)` - Update profile
- `api.analyzeImage(file)` - Analyze image
- `api.getRecommendations(id)` - Get recommendations
- `api.submitFeedback(...)` - Submit feedback

---

## 🔒 Protect Routes

```typescript
import { useAuth } from "../context/useAuth";
import { Navigate } from "react-router-dom";

function ProtectedPage() {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) return <div>Loading...</div>;
  if (!isAuthenticated) return <Navigate to="/login" />;

  return <div>Protected content here</div>;
}
```

---

## 📦 What's Stored

### localStorage

```javascript
// After login/signup
localStorage.getItem("auth_token"); // JWT token
localStorage.getItem("auth_user"); // User info (email, username)

// Check in browser console
console.log(localStorage.getItem("auth_token"));
```

### Automatically Restored

When user reloads page:

```typescript
// On app load
useEffect(() => {
  const token = localStorage.getItem("auth_token");
  if (token) {
    // Automatically restored!
    setToken(token);
  }
}, []);
```

---

## ⚙️ Configuration

### Backend URL

Default: `http://127.0.0.1:8000`

To change, set in `.env`:

```
VITE_API_BASE_URL=http://your-api.com:8000
```

---

## 🧪 Browser Console Testing

```javascript
// Check if logged in
localStorage.getItem("auth_token");

// Check user info
JSON.parse(localStorage.getItem("auth_user"));

// Simulate logout
localStorage.removeItem("auth_token");
localStorage.removeItem("auth_user");

// Reload page
location.reload();
```

---

## ❌ Common Issues

### "useAuth must be used within AuthProvider"

**Solution**: Make sure App.tsx is wrapped with `<AuthProvider>`

```typescript
// main.tsx
<AuthProvider>
  <BrowserRouter>
    <App />
  </BrowserRouter>
</AuthProvider>
```

### "Unauthorized (401)" on API calls

**Solution**: Check token is set in localStorage

```javascript
// Browser console
localStorage.getItem("auth_token"); // Should show token
```

### Token not persisting after reload

**Solution**: Check localStorage is enabled

```javascript
// Browser console
localStorage.setItem("test", "value");
localStorage.getItem("test"); // Should return 'value'
```

---

## 📚 Full Documentation

For detailed info, see:

- **AUTHENTICATION_GUIDE.md** - Complete reference
- **AUTH_USAGE_EXAMPLES.md** - Code examples
- **AUTH_IMPLEMENTATION_SUMMARY.md** - Overview

---

## 🎯 API Endpoints

### Login

```
POST /api/v1/auth/login
{
  "email": "user@example.com",
  "password": "password123"
}
Response: { "access_token": "...", "token_type": "bearer" }
```

### Signup

```
POST /api/v1/auth/signup
{
  "email": "user@example.com",
  "username": "john",
  "password": "password123"
}
Response: { "access_token": "...", "token_type": "bearer" }
```

### Get Profile (Requires Auth)

```
GET /api/v1/profile/me
Headers: Authorization: Bearer {token}
Response: { "id": 1, "age": 28, "gender": "...", ... }
```

See **ENDPOINT_QUICK_REFERENCE.md** for all endpoints.

---

## ✅ Checklist

- [x] Backend running on localhost:8000
- [x] Frontend running on localhost:5173
- [x] Can signup with email/username/password
- [x] Can login with email/password
- [x] Token stored in localStorage
- [x] Can access protected pages
- [x] Can make API calls with token
- [x] Session persists on page reload

---

## 🎉 You're Ready!

The authentication system is fully implemented and tested. Start using it in your components!

```typescript
// It's that simple:
import { useAuth } from "../context/useAuth";

const { login, signup, user, logout } = useAuth();
```

---

**Questions?** See the documentation files or check browser DevTools!
