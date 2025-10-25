# Quick Reference: App Shell Architecture

## Component Tree

```
App
├── AuthProvider
│   └── Routes
│       └── AppShell (Layout)
│           ├── Navbar (Sticky)
│           ├── Outlet (Page Content)
│           │   ├── Home
│           │   ├── Login
│           │   ├── Signup
│           │   ├── ProtectedRoute
│           │   │   ├── Dashboard
│           │   │   ├── Analyze
│           │   │   ├── Capture
│           │   │   ├── Recommendations
│           │   │   ├── Profile
│           │   │   └── AdminRecommendations
│           └── ToastContainer (Fixed)
```

## File Locations

```
frontend/src/
├── App.tsx (Main routes & AppShell)
├── main.tsx (Entry point)
├── index.css (Global styles)
├── components/
│   ├── Navbar.tsx (Navigation)
│   ├── ProtectedRoute.tsx (Auth guard) ⭐ NEW
│   └── ToastContainer.tsx (Notifications) ⭐ NEW
└── routes/
    ├── Home.tsx
    ├── Login.tsx
    ├── Signup.tsx
    ├── Dashboard.tsx (Protected)
    ├── Analyze.tsx (Protected)
    ├── Capture.tsx (Protected)
    ├── Recommendations.tsx (Protected)
    ├── Profile.tsx (Protected)
    └── AdminRecommendations.tsx (Protected)
```

## Using ProtectedRoute

```tsx
// In App.tsx
<Route
  path="/dashboard"
  element={
    <ProtectedRoute>
      <Dashboard />
    </ProtectedRoute>
  }
/>
```

## Dark Mode Classes Reference

```tsx
// Text colors
dark: text - white; // Dark background white text
dark: text - slate - 300; // Secondary text in dark mode
dark: text - slate - 400; // Tertiary text in dark mode
dark: text - cyan - 400; // Accent links

// Background colors
dark: bg - slate - 800; // Card background
dark: bg - slate - 900; // Secondary background
dark: from - blue - 700; // Gradient start
dark: to - cyan - 700; // Gradient end

// Border colors
dark: border - slate - 700; // Card borders

// Focus states
dark: focus: border - cyan - 500; // Input focus
dark: focus: ring - cyan - 500 / 50; // Focus ring

// Hover states
dark: hover: bg - blue - 700; // Button hover
dark: hover: text - cyan - 300; // Link hover
```

## Container System

```tsx
// Standard max-width container
<div className="max-w-7xl mx-auto px-4 md:px-6 lg:px-8">
  {/* Content - constrained width, responsive padding */}
</div>

// Full width (for hero sections)
<div className="w-full">
  {/* Content - full browser width */}
</div>
```

## Gradient Backgrounds

```tsx
// Light mode
className = "bg-gradient-to-br from-blue-50 via-cyan-50 to-slate-100";

// Dark mode
className = "dark:from-slate-950 dark:via-slate-900 dark:to-slate-950";

// Combined
className =
  "bg-gradient-to-br from-blue-50 via-cyan-50 to-slate-100 dark:from-slate-950 dark:via-slate-900 dark:to-slate-950";
```

## Responsive Breakpoints

```tsx
// Mobile-first approach
className = "text-sm sm:text-base md:text-lg lg:text-xl";
// sm:640px, md:768px, lg:1024px, xl:1280px

className = "px-4 md:px-6 lg:px-8";
// Responsive padding

className = "grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3";
// Responsive grid
```

## Authentication Flow

```
1. User visits app
   ↓
2. Check isAuthenticated + authToken
   ↓
3a. No auth → Public routes (Home, Login, Signup)
   ↓
3b. Has auth → Access protected routes
   ↓
4. Try protected route without auth → Redirect to /login
```

## Current Build Stats

- **Modules:** 803 compiled
- **Build Time:** 680ms
- **CSS Size:** 42.91 kB (8.34 kB gzipped)
- **JS Size:** 630.73 kB (189.88 kB gzipped)
- **Dev Server:** Ready in 174ms
- **HMR:** Enabled

## Testing Dark Mode

```bash
# On Windows 11/10
Settings → Personalization → Colors → Dark

# DevTools simulation
F12 → DevTools → Command palette → "light/dark mode"
```

## Customization Examples

### Adding a new protected route

```tsx
<Route
  path="/new-page"
  element={
    <ProtectedRoute>
      <NewPageComponent />
    </ProtectedRoute>
  }
/>
```

### Adding toast notification

```tsx
// In future - integrate with react-hot-toast
import { Toaster } from "react-hot-toast";

// In ToastContainer.tsx
export default function ToastContainer() {
  return <Toaster position="bottom-right" />;
}
```

### Custom dark mode override

```tsx
// Force light mode
<html className="light">

// Force dark mode
<html className="dark">

// Auto (respects OS preference)
<html>  {/* default */}
```
