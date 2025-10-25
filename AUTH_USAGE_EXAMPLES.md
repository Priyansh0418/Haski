# 📖 Authentication Usage Examples

**Last Updated**: October 25, 2025  
**Status**: ✅ Complete Reference Guide

---

## 🔐 Example 1: Using Login Form Component

File: `frontend/src/routes/Login.tsx`

```typescript
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Login() {
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { login } = useAuth(); // ← Get login function from context
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");
    setIsLoading(true);

    try {
      // Call login from useAuth hook
      await login(email, password); // ← Calls api.login() internally

      // Token is automatically:
      // 1. Stored in localStorage
      // 2. Set in authorization header
      // 3. Available via useAuth context

      navigate("/dashboard"); // ← Redirect on success
    } catch (err) {
      setError(err instanceof Error ? err.message : "Login failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          Login
        </h1>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="your@email.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder=""
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition disabled:opacity-50"
          >
            {isLoading ? "Logging in..." : "Login"}
          </button>
        </form>

        <p className="text-center mt-6 text-gray-600">
          Don't have an account?{" "}
          <Link
            to="/signup"
            className="text-indigo-600 hover:text-indigo-700 font-semibold"
          >
            Sign up
          </Link>
        </p>
      </div>
    </div>
  );
}
```

**Key Points**:

- ✅ `useAuth()` provides `login()` function
- ✅ Call `login(email, password)` with user credentials
- ✅ Token automatically stored in localStorage
- ✅ Redirect to dashboard on success
- ✅ Display error message on failure

---

## ✍️ Example 2: Using Signup Form Component

File: `frontend/src/routes/Signup.tsx`

```typescript
import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function Signup() {
  const [email, setEmail] = useState("");
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [confirmPassword, setConfirmPassword] = useState("");
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const { signup } = useAuth(); // ← Get signup function from context
  const navigate = useNavigate();

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError("");

    // Client-side validation
    if (password !== confirmPassword) {
      setError("Passwords do not match");
      return;
    }

    setIsLoading(true);

    try {
      // Call signup from useAuth hook
      await signup(email, username, password); // ← Calls api.signup() internally

      // Token is automatically:
      // 1. Stored in localStorage
      // 2. Set in authorization header
      // 3. Available via useAuth context

      navigate("/dashboard"); // ← Redirect on success
    } catch (err) {
      setError(err instanceof Error ? err.message : "Signup failed");
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-indigo-600 to-purple-600 flex items-center justify-center p-4">
      <div className="bg-white rounded-lg shadow-lg p-8 w-full max-w-md">
        <h1 className="text-3xl font-bold text-center mb-6 text-gray-800">
          Sign Up
        </h1>

        {error && (
          <div className="bg-red-50 border border-red-200 rounded-lg p-4 mb-4">
            <p className="text-red-700 text-sm">{error}</p>
          </div>
        )}

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Email
            </label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="your@example.com"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Username
            </label>
            <input
              type="text"
              value={username}
              onChange={(e) => setUsername(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder="username"
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Password
            </label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder=""
              required
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Confirm Password
            </label>
            <input
              type="password"
              value={confirmPassword}
              onChange={(e) => setConfirmPassword(e.target.value)}
              className="w-full border border-gray-300 rounded-lg px-4 py-2 focus:ring-2 focus:ring-indigo-500 focus:border-transparent"
              placeholder=""
              required
            />
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-indigo-600 hover:bg-indigo-700 text-white font-semibold py-2 px-4 rounded-lg transition disabled:opacity-50"
          >
            {isLoading ? "Creating account..." : "Sign Up"}
          </button>
        </form>

        <p className="text-center mt-6 text-gray-600">
          Already have an account?{" "}
          <Link
            to="/login"
            className="text-indigo-600 hover:text-indigo-700 font-semibold"
          >
            Log in
          </Link>
        </p>
      </div>
    </div>
  );
}
```

**Key Points**:

- ✅ `useAuth()` provides `signup()` function
- ✅ Call `signup(email, username, password)` with user data
- ✅ Validate passwords match before submission
- ✅ Token automatically stored in localStorage
- ✅ Redirect to dashboard on success
- ✅ Display validation errors

---

## 🏠 Example 3: Using Auth Context in Other Components

File: `frontend/src/routes/Dashboard.tsx`

```typescript
import { useAuth } from "../context/useAuth";
import { useNavigate } from "react-router-dom";

export default function Dashboard() {
  const { user, token, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = () => {
    logout();
    navigate("/login");
  };

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">Dashboard</h1>

      {user ? (
        <div>
          <p className="text-lg">Welcome, {user.username || user.email}!</p>
          <p className="text-sm text-gray-600">Email: {user.email}</p>

          {token && (
            <p className="text-xs text-gray-500 mt-4">
              Token: {token.substring(0, 20)}...
            </p>
          )}
        </div>
      ) : (
        <p>Not authenticated</p>
      )}

      <button
        onClick={handleLogout}
        className="mt-8 px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700"
      >
        Logout
      </button>
    </div>
  );
}
```

**Key Points**:

- ✅ Access user info: `user.username`, `user.email`
- ✅ Access token: `token`
- ✅ Check authentication status: `isAuthenticated`
- ✅ Call logout function to clear auth

---

## 📊 Example 4: Using API Functions Directly

File: `frontend/src/routes/Profile.tsx`

```typescript
import { useEffect, useState } from "react";
import * as api from "../lib/api";
import { useAuth } from "../context/useAuth";

export default function Profile() {
  const { token, isAuthenticated } = useAuth();
  const [profile, setProfile] = useState(null);
  const [error, setError] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  useEffect(() => {
    if (isAuthenticated) {
      loadProfile();
    }
  }, [isAuthenticated]);

  const loadProfile = async () => {
    setIsLoading(true);
    setError("");
    try {
      const data = await api.getProfile(); // ← Calls authenticated endpoint
      setProfile(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to load profile");
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateProfile = async () => {
    try {
      const updated = await api.updateProfile({
        // ← Calls authenticated endpoint
        age: 30,
        gender: "female",
        skin_type: "combination",
      });
      setProfile(updated);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to update profile");
    }
  };

  if (!isAuthenticated) return <div>Please log in first</div>;
  if (isLoading) return <div>Loading...</div>;

  return (
    <div className="p-8">
      <h1 className="text-3xl font-bold mb-4">My Profile</h1>

      {error && <div className="text-red-600 mb-4">{error}</div>}

      {profile ? (
        <div className="bg-gray-100 p-4 rounded-lg">
          <p>
            <strong>Age:</strong> {profile.age}
          </p>
          <p>
            <strong>Gender:</strong> {profile.gender}
          </p>
          <p>
            <strong>Skin Type:</strong> {profile.skin_type}
          </p>
          <p>
            <strong>Hair Type:</strong> {profile.hair_type}
          </p>
        </div>
      ) : (
        <p>No profile data</p>
      )}

      <button
        onClick={handleUpdateProfile}
        className="mt-4 px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700"
      >
        Update Profile
      </button>
    </div>
  );
}
```

**Key Points**:

- ✅ Import API functions: `import * as api from '../lib/api'`
- ✅ Call `api.getProfile()` for authenticated endpoints
- ✅ Call `api.updateProfile(data)` to update
- ✅ Token is automatically included in header
- ✅ Handle loading and error states

---

## 🔒 Example 5: Protected Route Wrapper

File: `frontend/src/components/ProtectedRoute.tsx`

```typescript
import { Navigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import type { ReactNode } from "react";

export function ProtectedRoute({ children }: { children: ReactNode }) {
  const { isAuthenticated, isLoading } = useAuth();

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <p className="text-lg text-gray-600">Loading...</p>
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace />;
  }

  return children;
}
```

**Usage in App.tsx**:

```typescript
import { ProtectedRoute } from "./components/ProtectedRoute";

<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/signup" element={<Signup />} />
  <Route
    path="/dashboard"
    element={
      <ProtectedRoute>
        <Dashboard />
      </ProtectedRoute>
    }
  />
</Routes>;
```

**Key Points**:

- ✅ Redirect to login if not authenticated
- ✅ Show loading state during initial auth check
- ✅ Use for any route that requires authentication

---

## 🔧 Example 6: Complete App Setup

File: `frontend/src/main.tsx`

```typescript
import React from "react";
import ReactDOM from "react-dom/client";
import { BrowserRouter } from "react-router-dom";
import App from "./App.tsx";
import { AuthProvider } from "./context/AuthContext";
import "./index.css";

ReactDOM.createRoot(document.getElementById("root")!).render(
  <React.StrictMode>
    <AuthProvider>
      <BrowserRouter>
        <App />
      </BrowserRouter>
    </AuthProvider>
  </React.StrictMode>
);
```

**Key Points**:

- ✅ Wrap app with `AuthProvider`
- ✅ Wrap with `BrowserRouter` for routing
- ✅ AuthProvider must be inside BrowserRouter

---

## 🧪 Example 7: Testing the Auth Flow

### Browser Console Testing

```javascript
// 1. Check if user is logged in
localStorage.getItem("auth_token");
// Returns: "eyJ0eXAiOiJKV1QiLCJhbGc..." or null

// 2. Check user info
JSON.parse(localStorage.getItem("auth_user") || "{}");
// Returns: { email: "user@example.com", username: "john_doe" }

// 3. Simulate logout
localStorage.removeItem("auth_token");
localStorage.removeItem("auth_user");
// Reload page - should redirect to /login

// 4. Check authorization header in Network tab
// Open DevTools → Network tab
// Try to make API request (click button, upload image, etc)
// Check Request Headers for: Authorization: Bearer {token}
```

### Manual Flow Testing

```bash
# 1. Start frontend dev server
cd frontend
npm run dev
# Open http://localhost:5173

# 2. Test signup
- Click "Sign Up" link
- Fill in: email, username, password
- Click "Sign Up" button
- Should redirect to /dashboard
- Check localStorage: should have auth_token

# 3. Log out (add logout button or clear localStorage)
localStorage.removeItem('auth_token')
localStorage.removeItem('auth_user')
# Reload page - should redirect to /login

# 4. Test login
- Fill in: email, password
- Click "Login" button
- Should redirect to /dashboard
- Check localStorage: should have auth_token

# 5. Test protected route
- Reload page
- Should still be on /dashboard (session restored)
- Try to access /dashboard while logged out (manually clear localStorage)
- Should redirect to /login
```

---

## ❌ Example 8: Error Handling Patterns

### Signup Error Handling

```typescript
try {
  await signup("test@example.com", "user", "pass123");
} catch (error) {
  if (error instanceof Error) {
    if (error.message.includes("already registered")) {
      // Email already in use
      setError("This email is already registered");
    } else if (error.message.includes("Invalid")) {
      // Validation error
      setError("Please check your input");
    } else {
      // Generic error
      setError(error.message);
    }
  }
}
```

### Login Error Handling

```typescript
try {
  await login("user@example.com", "wrongpassword");
} catch (error) {
  // error.message = "Unauthorized. Please check your credentials."
  setError("Invalid email or password");
}
```

### API Call Error Handling

```typescript
try {
  await getProfile(); // Will fail if token not set
} catch (error) {
  // error.message = "Unauthorized. Please check your credentials."
  if (error instanceof Error) {
    if (error.message.includes("Unauthorized")) {
      // Token expired or invalid - redirect to login
      navigate("/login");
    } else {
      setError(error.message);
    }
  }
}
```

---

## 📋 API Function Reference

### Import API Functions

```typescript
import * as api from "../lib/api";

// Available functions:
api.signup(email, username, password);
api.login(email, password);
api.setAuthToken(token);
api.getProfile();
api.updateProfile(profileData);
api.analyzeImage(file);
api.getRecommendations(analysisId);
api.submitFeedback(recommendationId, rating, helpful, comment);
```

### Usage Examples

```typescript
// Signup
const response = await api.signup(
  "user@example.com",
  "john_doe",
  "SecurePass123!"
);
console.log(response.access_token);

// Login
const response = await api.login("user@example.com", "SecurePass123!");
console.log(response.access_token);

// Set token for all requests
api.setAuthToken(token);

// Get profile
const profile = await api.getProfile();
console.log(profile.age, profile.skin_type);

// Update profile
const updated = await api.updateProfile({
  age: 30,
  gender: "female",
  skin_type: "combination",
});

// Analyze image
const file = document.getElementById("imageInput").files[0];
const result = await api.analyzeImage(file);
console.log(result.skin_type, result.conditions_detected);

// Get recommendations
const recs = await api.getRecommendations(analysisId);
console.log(recs.routines, recs.products);

// Submit feedback
const feedback = await api.submitFeedback(
  "rec_20251025_001",
  5,
  true,
  "Great recommendations!"
);
```

---

## ✅ Checklist

- [x] Signup form created and working
- [x] Login form created and working
- [x] Token stored in localStorage
- [x] Token set in API authorization header
- [x] Navigation to dashboard after auth
- [x] Session restored on page reload
- [x] Protected routes redirect to login
- [x] API functions called with auth token
- [x] Error handling and display working
- [x] All examples documented

---

## 🎯 Summary

The authentication system provides:

✅ **Signup**: Create new account with email, username, password  
✅ **Login**: Authenticate with email and password  
✅ **Token Management**: JWT tokens stored and used automatically  
✅ **Session Persistence**: Auto-restore from localStorage  
✅ **Protected Routes**: Redirect unauthenticated users to login  
✅ **Authenticated API Calls**: All API functions include token  
✅ **Error Handling**: User-friendly error messages  
✅ **TypeScript**: Full type safety throughout

Users can now sign up, log in, and make authenticated API calls for profiles, image analysis, recommendations, and feedback.
