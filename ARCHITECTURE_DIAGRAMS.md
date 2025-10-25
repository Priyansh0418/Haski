# 📐 App Shell Architecture Diagrams

## Component Hierarchy

```
┌─────────────────────────────────────────────────┐
│                   main.tsx                       │
│           StrictMode → BrowserRouter             │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│                    App.tsx                       │
│              AuthProvider (Context)              │
└──────────────────┬──────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────┐
│                  Routes                          │
│         React Router Route definitions           │
└──────────────────┬──────────────────────────────┘
                   │
       ┌───────────┴────────────┐
       │                        │
       │                        │
┌──────▼──────┐      ┌─────────▼─────────────┐
│  Public     │      │   AppShell (Layout)   │
│  Routes     │      │                       │
│  (Home,     │      │  ┌─────────────────┐  │
│  Login,     │      │  │ Navbar (Sticky) │  │
│  Signup)    │      │  └─────────────────┘  │
└─────────────┘      │                       │
                     │  ┌─────────────────┐  │
                     │  │    Outlet       │  │
                     │  │  (Page Content) │  │
                     │  ├─────────────────┤  │
                     │  │ Protected       │  │
                     │  │ Routes:         │  │
                     │  │ • Dashboard     │  │
                     │  │ • Analyze       │  │
                     │  │ • Capture       │  │
                     │  │ • etc.          │  │
                     │  └─────────────────┘  │
                     │                       │
                     │  ┌─────────────────┐  │
                     │  │ ToastContainer  │  │
                     │  │ (Fixed Bottom)  │  │
                     │  └─────────────────┘  │
                     └───────────────────────┘
```

## Route Flow Diagram

```
User Visits App
      │
      ▼
   ┌─────────────────┐
   │ Route Matched?  │
   └────┬────────┬───┘
        │        │
    No  │        │ Yes
        │        │
        ▼        ▼
    Error    ┌─────────────────┐
    404      │ Public Route?   │
             └────┬────────┬───┘
                  │        │
              No  │        │ Yes
                  │        │
                  ▼        ▼
          ┌──────────────┐ ┌──────────────┐
          │ Protected    │ │ Public Page  │
          │ Route?       │ │ Shown ✓      │
          └────┬────┬───┘ └──────────────┘
               │    │
           No  │    │ Yes
               │    │
               ▼    ▼
            ┌──────────────────┐
            │ ProtectedRoute   │
            │ checks auth      │
            └────┬─────────┬───┘
                 │         │
             No  │         │ Yes
                 │         │
                 ▼         ▼
        ┌──────────────┐ ┌──────────────┐
        │ Redirect to  │ │ Protected    │
        │ /login ◀───  │ │ Page Shown ✓ │
        └──────────────┘ └──────────────┘
```

## Layout Structure

```
┌──────────────────────────────────────┐
│                                      │
│      Navbar (max-w-7xl)              │  ◀─ Sticky (top: 0, z-50)
│  [Logo]  [Links]  [Avatar/Login]    │
│                                      │
├──────────────────────────────────────┤
│                                      │
│                                      │
│      Main Content (max-w-7xl)        │  ◀─ Flex-1 (fills space)
│                                      │
│    [Page-Specific Content]           │
│                                      │
│                                      │
├──────────────────────────────────────┤
│                                      │
│  Toast Container (Fixed)             │  ◀─ Bottom-right, z-50
│  [Notification bubbles]              │
│                                      │
└──────────────────────────────────────┘
```

## Data Flow: Authentication

```
┌──────────────┐
│ App Opens    │
└──────┬───────┘
       │
       ▼
┌──────────────────────────────┐
│ App.tsx checks:              │
│ 1. AuthContext              │
│ 2. localStorage['authToken']│
└──────┬───────────────────────┘
       │
       ▼
    ┌──┴──┐
    │ Yes │  No
    │     │
    ▼     ▼
 Set   Initialize
Logged  Not Logged
In Flag In Flag
    │     │
    │     │
    ▼     ▼
┌───────────────────┐
│ User tries to     │
│ access route      │
└────┬──────────┬───┘
     │          │
   Public   Protected
     │          │
     ▼          ▼
  Show Page  ┌────────────┐
             │ Has auth?  │
             └──┬──────┬──┘
                │      │
              No│      │Yes
                │      │
                ▼      ▼
        Redirect  Show
        to /login Page
```

## Responsive Container Layout

```
Mobile (320px)
┌──────────────────┐
│ px-4             │  ◀─ 16px padding
│ max-w-7xl        │
│                  │
└──────────────────┘

Tablet (768px+)
┌────────────────────────────────┐
│ px-6                           │  ◀─ 24px padding
│ max-w-7xl                      │
│                                │
└────────────────────────────────┘

Desktop (1024px+)
┌─────────────────────────────────────┐
│ px-8                                │  ◀─ 32px padding
│ max-w-7xl (1280px max)              │
│                                     │
└─────────────────────────────────────┘
```

## Dark Mode Toggle (System-Based)

```
OS Settings
    │
    ▼
┌─────────────────────┐
│ prefers-color-scheme│
└────┬────────────┬───┘
     │            │
  light       dark
     │            │
     ▼            ▼
┌──────────┐  ┌──────────┐
│ Light    │  │ Dark     │
│ Theme    │  │ Theme    │
│          │  │          │
│ Blue/    │  │ Darker   │
│ Cyan     │  │ Blue/    │
│ Colors   │  │ Cyan     │
│          │  │ Colors   │
└──────────┘  └──────────┘
```

## Protected Route Flow

```
┌─────────────────────────────┐
│ ProtectedRoute Component    │
│ {children}                  │
└──────────┬──────────────────┘
           │
           ▼
┌─────────────────────────────┐
│ Check:                      │
│ 1. useAuth() context        │
│ 2. localStorage['authToken']│
└──────┬──────────────────┬───┘
       │                  │
    Both   Either one
     found missing
       │                  │
       ▼                  ▼
   ┌────────┐    ┌──────────────────┐
   │ Return │    │ Navigate to      │
   │children│    │ /login (replace) │
   └────────┘    └──────────────────┘
```

## Color System (Tailwind Classes)

```
Light Mode (default)
├── Text
│   ├── Primary: text-slate-900
│   ├── Secondary: text-slate-700
│   └── Tertiary: text-slate-600
├── Background
│   ├── Primary: bg-white
│   ├── Secondary: bg-slate-50
│   └── Gradient: from-blue-50 via-cyan-50 to-slate-100
├── Accent
│   ├── Primary: from-blue-600 to-cyan-600
│   └── Hover: from-blue-700 to-cyan-700
└── Borders
    ├── Primary: border-gray-100
    └── Secondary: border-gray-200

Dark Mode (media query)
├── Text
│   ├── Primary: dark:text-white
│   ├── Secondary: dark:text-slate-300
│   └── Tertiary: dark:text-slate-400
├── Background
│   ├── Primary: dark:bg-slate-800
│   ├── Secondary: dark:bg-slate-900
│   └── Gradient: dark:from-slate-950 dark:via-slate-900 dark:to-slate-950
├── Accent
│   ├── Primary: dark:from-blue-700 dark:to-cyan-700
│   └── Hover: dark:from-blue-800 dark:to-cyan-800
└── Borders
    ├── Primary: dark:border-slate-700
    └── Secondary: dark:border-slate-600
```

## File Organization

```
frontend/
├── src/
│   ├── main.tsx ━━━━━━━━━━━━━━━┐
│   │                            │ Entry point
│   ├── App.tsx ◀────────────────┘
│   │   (Route definitions, AppShell)
│   │
│   ├── index.css
│   │   (Global styles, dark mode)
│   │
│   ├── components/
│   │   ├── Navbar.tsx ⭐
│   │   ├── ProtectedRoute.tsx ⭐ (NEW)
│   │   ├── ToastContainer.tsx ⭐ (NEW)
│   │   ├── CameraCapture.tsx
│   │   ├── ResultCard.tsx
│   │   └── ...
│   │
│   ├── routes/
│   │   ├── Home.tsx ⭐
│   │   ├── Login.tsx ⭐
│   │   ├── Signup.tsx ⭐
│   │   ├── Dashboard.tsx
│   │   ├── Analyze.tsx
│   │   └── ...
│   │
│   └── context/
│       └── AuthContext.tsx
│
└── public/
    └── index.html
```

## TypeScript Type System

```
ProtectedRoute
├── Props
│   └── children: React.ReactNode
├── Context Check
│   └── useAuth(): { isAuthenticated: boolean }
├── Storage Check
│   └── localStorage.getItem('authToken'): string | null
└── Return
    ├── If authenticated: <>{children}</>
    └── If not: <Navigate to="/login" replace />
```

---

**Legend:**

- ⭐ = New/Updated in refactor
- ◀─ = Important note
- → = Data flow
- ▼ = Process flow
- ✓ = Success/Active state
