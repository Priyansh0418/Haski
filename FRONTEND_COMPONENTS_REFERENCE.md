# 📚 Haski Frontend - Component & Route Reference Guide

## 🗂️ File Structure Overview

```
frontend/
├── src/
│   ├── routes/              # Page components (8 files)
│   ├── components/          # Reusable UI components (10 files)
│   ├── context/             # State management
│   ├── lib/                 # Utilities & API client
│   ├── assets/              # Images, icons
│   ├── App.tsx              # Main app shell with routing
│   ├── main.tsx             # Entry point
│   └── index.css            # Global styles
├── public/
│   ├── service-worker.js    # PWA offline support
│   └── manifest.json        # Web app configuration
├── vite.config.ts           # Vite configuration
├── tailwind.config.js       # Tailwind CSS setup
├── tsconfig.json            # TypeScript config
├── .env                     # Environment variables
└── package.json             # Dependencies
```

---

## 📄 Routes (Page Components)

### 1. **Home.tsx** (282 lines)

**Purpose:** Landing page  
**Path:** `/`  
**Status:** Public (no auth required)  
**What it does:**

- Hero section with "Haski" gradient title
- 3 feature cards (Capture, Analyze, Insights)
- CTAs: "Get Started" → `/analyze` & "Sign In" → `/login`
- Trust section with privacy guarantees
- Medical disclaimer banner

**Key UI:**

```tsx
<a href="/analyze" className="...">
  🚀 Get Started →
</a>
```

---

### 2. **Login.tsx** (297 lines)

**Purpose:** User authentication  
**Path:** `/login`  
**Status:** Public (no auth required)  
**What it does:**

- Email field with validation (must be valid email format)
- Password field
- Form validation (real-time on blur, after first edit)
- API call to `/auth/login`
- Stores token in localStorage
- Redirects to `/dashboard` on success
- Displays API errors (invalid credentials, server errors)
- Link to `/signup` for new users

**Key flow:**

```tsx
const { login } = useAuth();
// On submit:
await login(email, password);
navigate("/dashboard");
```

---

### 3. **Signup.tsx** (359 lines)

**Purpose:** User registration  
**Path:** `/signup`  
**Status:** Public (no auth required)  
**What it does:**

- Email field with validation
- Password field with requirements:
  - Min 8 characters
  - Must include uppercase (A-Z)
  - Must include lowercase (a-z)
  - Must include number (0-9)
- Confirm password field (must match)
- Real-time validation feedback
- API call to `/auth/signup`
- Token stored, redirects to `/dashboard`
- Link to `/login` for existing users

**Key validation:**

```tsx
const PASSWORD_REGEX = /^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)/;
```

---

### 4. **Analyze.tsx** (242 lines)

**Purpose:** Image analysis page  
**Path:** `/analyze`  
**Status:** Protected (requires token)  
**What it does:**

- Integrates `CameraCapture` component
- Displays analysis results via `ResultCard` when available
- Shows loading state: "Analyzing your photo..."
- Handles errors gracefully
- Sends image to `/api/v1/analyze/image` endpoint

**Key flow:**

```tsx
const response = await fetch("http://localhost:8000/api/v1/analyze/image", {
  method: "POST",
  body: formData,
  headers: { Authorization: "Bearer " + token },
});
const data = await response.json();
setResult(data);
```

---

### 5. **Recommendations.tsx** (612 lines)

**Purpose:** Display AI recommendations  
**Path:** `/recommendations`  
**Status:** Protected (requires token)  
**What it does:**

- Receives analysis data via route state
- Extracts `analysis_id` from location.state
- Auto-fetches recommendations on mount
- Displays `RecommendationsDisplay` component
- Shows "No Analysis Available" if missing data
- Handles API errors

**Key usage:**

```tsx
const analysisData = location.state?.result;
const recs = await api.getRecommendations(analysisData.analysis_id);
```

---

### 6. **Dashboard.tsx** (329 lines)

**Purpose:** User dashboard with analytics  
**Path:** `/dashboard`  
**Status:** Protected (requires token)  
**What it does:**

- Welcome card: "Welcome, [User's Name]!"
- Quick stats: Last analysis, analyses this week, scores
- Action buttons: New Analysis, Set Reminder, Settings
- Integrates `HistoryTrend` (line chart)
- Loads from API with localStorage fallback
- Displays `ReminderModal` and `SettingsModal`

**Key components:**

```tsx
<HistoryTrend />
<ReminderModal isOpen={reminderModalOpen} />
<SettingsModal isOpen={settingsModalOpen} />
```

---

### 7. **Settings.tsx** (42 lines)

**Purpose:** Settings page  
**Path:** `/settings`  
**Status:** Protected (requires token)  
**What it does:**

- Full-page wrapper for `SettingsModal`
- Back button to `/dashboard`
- Displays privacy settings, data management, permissions

**Simple layout:**

```tsx
<SettingsModal isOpen={true} onClose={() => navigate("/dashboard")} />
```

---

### 8. **Capture.tsx** (28 lines - Basic)

**Purpose:** Capture page (placeholder)  
**Path:** `/capture`  
**Status:** Protected (requires token)  
**What it does:**

- Simple page that might redirect to `/analyze`
- Could be used for direct camera-only mode

---

## 🎨 Components (Reusable UI)

### 1. **CameraCapture.tsx** (483 lines)

**Purpose:** Camera/file upload interface  
**Used by:** `Analyze.tsx`  
**What it does:**

- Live camera preview using `getUserMedia()`
- Camera permission request & status tracking
- File picker (hidden input) as fallback
- Capture button (takes snapshot from video)
- Upload button (opens file picker)
- Preview of captured image
- Retake button
- Real-time lighting analysis (brightness detection)
- "Good lighting" / "Poor lighting" indicator
- Stream cleanup (stops tracks on unmount)
- Browser compatibility check

**Key API:**

```tsx
const stream = await navigator.mediaDevices.getUserMedia({
  video: { facingMode: "user", width: { ideal: 1280 }, height: { ideal: 720 } },
  audio: false,
});
```

**Props:**

```tsx
interface CameraCaptureProps {
  onCapture?: (file: File) => void;
  onError?: (error: string) => void;
}
```

---

### 2. **ResultCard.tsx** (261 lines)

**Purpose:** Display analysis results in modal  
**Used by:** `Analyze.tsx`  
**What it does:**

- Modal overlay (fixed position, semi-transparent bg)
- Sticky header with close button
- Medical disclaimer banner
- Displays:
  - Skin type with emoji & confidence score
  - Hair type with emoji & confidence score
  - Conditions detected (list)
- "Get Recommendations" button
- "Save to History" button
- Fetches & displays recommendations inline
- Error handling

**Key structure:**

```tsx
<div className="fixed inset-0 bg-black bg-opacity-50 ...">
  <div className="...">{/* Header, content, buttons */}</div>
</div>
```

**Props:**

```tsx
interface ResultCardProps {
  data: AnalysisResult;
  onClose: () => void;
  onRecommend?: () => void;
}
```

---

### 3. **RecommendationsDisplay.tsx** (246 lines)

**Purpose:** Show routines, products, diet recommendations  
**Used by:** `ResultCard.tsx`, `Recommendations.tsx`  
**What it does:**

- 3 main sections:
  1. **Routines** (🔄): Name, frequency, description, steps
  2. **Products** (🛍️): Brand, price, rating, reason, link
  3. **Diet** (🍎): Food, benefits, frequency, reason
- Escalation banner (⚠️): Red/orange/yellow based on urgency
- Medical disclaimer
- Feedback system: "Was this helpful?" with 👍👎 buttons
- Responsive grid layout

**Key sections:**

```tsx
{/* Routines */}
{routines && routines.length > 0 && (
  <div>
    <h3>🔄 Recommended Routines</h3>
    {routines.map(routine => (...))}
  </div>
)}
```

**Props:**

```tsx
interface RecommendationsDisplayProps {
  data: RecommendationsData;
  onClear: () => void;
}
```

---

### 4. **HistoryTrend.tsx** (197 lines)

**Purpose:** Line chart of analysis history  
**Used by:** `Dashboard.tsx`  
**What it does:**

- Recharts LineChart component
- Plots last 5 analyses
- Blue line: Skin score trend
- Orange line: Hair score trend
- X-axis: Dates (formatted as "Oct 22", "Oct 24")
- Y-axis: Score 0-100
- Hover tooltip with exact values
- Legend identifying lines
- Responsive to screen width
- Loading spinner, error handling

**Key chart:**

```tsx
<ResponsiveContainer width="100%" height={400}>
  <LineChart data={chartData}>
    <Line type="monotone" dataKey="skin_score" stroke="#3b82f6" />
    <Line type="monotone" dataKey="hair_score" stroke="#f97316" />
  </LineChart>
</ResponsiveContainer>
```

---

### 5. **ReminderModal.tsx** (274 lines)

**Purpose:** Schedule daily skincare reminder  
**Used by:** `Dashboard.tsx`  
**What it does:**

- Modal dialog with backdrop
- Time picker (HH:MM format, default 09:00)
- Enable/Disable toggle
- Permission status display (Granted/Denied/Prompt)
- "Request Permission" button
- Local reminder logic (checks every minute)
- Shows browser Notification at scheduled time
- Fallback to alert() if notification denied
- Persistent storage (localStorage: reminderSettings)
- Save & Close buttons

**Key reminder check:**

```tsx
const checkReminder = () => {
  if (currentTime === settings.time && settings.notificationGranted) {
    new Notification("Haski Reminder", {
      body: "Time for your skincare routine! 🧴",
      icon: "/favicon.ico",
    });
  }
};
```

**Props:**

```tsx
interface ReminderModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

---

### 6. **SettingsModal.tsx** (514 lines)

**Purpose:** User privacy & data management  
**Used by:** `Settings.tsx`, `Dashboard.tsx`  
**What it does:**

- Tabs:
  1. **Privacy**: Allow image improvement toggle
  2. **Data Management**:
     - Show localStorage size
     - Clear All Data button (with confirmation)
     - Clear History button
  3. **Camera Permissions**:
     - Display current permission status
     - Request permission button
     - Revoke permission note
  4. **Legal**:
     - Privacy Policy link
     - Medical Disclaimer link
     - Terms of Service link
     - Delete Account button (placeholder)

**Key features:**

```tsx
const calculateStorageSize = () => {
  let total = 0;
  for (const key in localStorage) {
    total += localStorage[key].length + key.length;
  }
  setStorageSize(`${Math.ceil(total / 1024)} KB`);
};

const handleClearAllData = () => {
  localStorage.clear();
  setStorageSize("0 KB");
};
```

**Props:**

```tsx
interface SettingsModalProps {
  isOpen: boolean;
  onClose: () => void;
}
```

---

### 7. **ProtectedRoute.tsx** (30 lines)

**Purpose:** Route guard for authenticated pages  
**Used by:** `App.tsx`  
**What it does:**

- Checks `isAuthenticated` from AuthContext
- Checks `authToken` in localStorage (fallback)
- If both false: Redirect to `/login` with replace
- Otherwise: Render children

**Simple logic:**

```tsx
export default function ProtectedRoute({ children }: ProtectedRouteProps) {
  const { isAuthenticated } = useAuth();
  const token = localStorage.getItem("authToken");

  if (!isAuthenticated && !token) {
    return <Navigate to="/login" replace />;
  }

  return <>{children}</>;
}
```

**Props:**

```tsx
interface ProtectedRouteProps {
  children: React.ReactNode;
}
```

---

### 8. **Navbar.tsx** (200+ lines)

**Purpose:** Top navigation bar  
**Used by:** `App.tsx` (AppShell)  
**What it does:**

- Sticky positioning
- Logo/brand: "Haski"
- Navigation links (auth-aware)
- Dark mode toggle
- User menu dropdown (when authenticated)
- Hamburger menu on mobile
- Active link highlighting
- Logout functionality

**Key structure:**

```tsx
<nav className="sticky top-0 ...">
  <div className="flex justify-between items-center">
    <Logo />
    <NavLinks />
    <DarkModeToggle />
    {isAuthenticated && <UserMenu />}
  </div>
</nav>
```

---

### 9. **ToastContainer.tsx** (60 lines)

**Purpose:** Display toast notifications  
**Used by:** `App.tsx` (AppShell)  
**What it does:**

- Renders list of active toasts
- Each toast has:
  - Message text
  - Type: success (green) / error (red) / info (blue)
  - Close button (X)
  - Auto-dismiss after 3.5 seconds
  - Smooth fade/slide animation

**Key render:**

```tsx
<div className="fixed bottom-4 right-4 space-y-2 z-50">
  {toasts.map((toast) => (
    <Toast key={toast.id} {...toast} />
  ))}
</div>
```

---

### 10. **AnalysisCard.tsx** (80 lines - Optional)

**Purpose:** Display single analysis in history  
**Used by:** Potentially in future history view  
**What it does:**

- Shows analysis summary (skin type, hair type, date)
- Quick stats (scores, conditions)
- Click to view full details

---

## 🧠 State Management

### 1. **AuthContext.tsx**

**Purpose:** Authentication state & token management  
**Exports:**

```tsx
interface AuthContextType {
  isAuthenticated: boolean;
  user: User | null;
  token: string | null;
  login(email: string, password: string): Promise<void>;
  signup(email: string, username: string, password: string): Promise<void>;
  logout(): void;
}

// Usage in components:
const { isAuthenticated, token, login } = useAuth();
```

---

### 2. **ToastContext.tsx**

**Purpose:** Toast notification state  
**Exports:**

```tsx
interface ToastContextType {
  toasts: Toast[];
  addToast(message: string, type: "success" | "error" | "info"): void;
}

// Usage in components:
const { addToast } = useToast();
addToast("Login successful!", "success");
```

---

## 🔧 Utilities

### 1. **api.ts** (500+ lines)

**Purpose:** Centralized API client  
**Features:**

- Axios instance with VITE_API_URL from .env
- Automatic Bearer token injection
- Token persistence (localStorage key: authToken)
- Centralized error handling
- TypeScript interfaces for all responses

**Export functions:**

```tsx
export const signup(email, username, password): Promise<SignupResponse>
export const login(email, password): Promise<LoginResponse>
export const getProfile(): Promise<UserProfile>
export const updateProfile(data): Promise<UserProfile>
export const analyzeImage(file): Promise<AnalysisResult>
export const getRecommendations(analysis): Promise<RecommendationsResponse>
export const getAnalysisHistory(): Promise<AnalysisHistoryResponse>
export const postFeedback(recommendationId, rating, comment): Promise<FeedbackResponse>
export const submitFeedback(recommendationId, rating, helpful, comment): Promise<FeedbackResponse>
```

**Usage:**

```tsx
import * as api from "../lib/api";
const result = await api.analyzeImage(file);
```

---

### 2. **pwa.ts** (140 lines)

**Purpose:** PWA utilities & service worker management  
**Export functions:**

```tsx
export const registerServiceWorker(): Promise<void>
export const clearServiceWorkerCache(): Promise<void>
export const isServiceWorkerActive(): boolean
export const getCacheStats(): Promise<CacheStats>
export const updateServiceWorker(): Promise<void>
export const unregisterServiceWorker(): Promise<void>
```

**Usage:**

```tsx
import { registerServiceWorker, getCacheStats } from "../lib/pwa";

// In main.tsx:
registerServiceWorker();

// In components:
if (isServiceWorkerActive()) {
  const stats = await getCacheStats();
  console.log("Cache stats:", stats);
}
```

---

## 📦 Key Dependencies

```json
{
  "react": "^18.x",
  "react-router-dom": "^6.x",
  "axios": "^1.x",
  "recharts": "^2.x",
  "tailwindcss": "^3.x"
}
```

---

## 🔄 Data Flow Examples

### Authentication Flow

```
1. User fills signup form
   ↓
2. Submit button → signup(email, username, password)
   ↓
3. AuthContext calls api.signup()
   ↓
4. API returns access_token
   ↓
5. Token stored in localStorage (key: authToken)
   ↓
6. setAuthToken() adds to API headers
   ↓
7. navigate("/dashboard")
```

### Analysis Flow

```
1. User grants camera permission
   ↓
2. CameraCapture shows live stream
   ↓
3. User clicks "Capture"
   ↓
4. Canvas converts video frame to blob
   ↓
5. FormData sent to /api/v1/analyze/image
   ↓
6. Backend returns AnalysisResult
   ↓
7. ResultCard displays results
   ↓
8. User clicks "Get Recommendations"
   ↓
9. RecommendationsDisplay shows suggestions
```

### Recommendation Feedback Flow

```
1. User views recommendations
   ↓
2. Clicks "Was this helpful?"
   ↓
3. Chooses 👍 (helpful) or 👎 (not helpful)
   ↓
4. postFeedback() sends to /api/v1/feedback
   ↓
5. API stores feedback with recommendation_id
   ↓
6. Success message displays
```

---

## 📋 File Reference Quick Lookup

| Feature          | Component                | File                                                   |
| ---------------- | ------------------------ | ------------------------------------------------------ |
| Landing page     | Home                     | `routes/Home.tsx`                                      |
| User signup      | Signup                   | `routes/Signup.tsx`                                    |
| User login       | Login                    | `routes/Login.tsx`                                     |
| Image analysis   | Analyze + CameraCapture  | `routes/Analyze.tsx` + `components/CameraCapture.tsx`  |
| Analysis results | ResultCard               | `components/ResultCard.tsx`                            |
| Recommendations  | RecommendationsDisplay   | `components/RecommendationsDisplay.tsx`                |
| User dashboard   | Dashboard + HistoryTrend | `routes/Dashboard.tsx` + `components/HistoryTrend.tsx` |
| Daily reminder   | ReminderModal            | `components/ReminderModal.tsx`                         |
| Settings         | Settings + SettingsModal | `routes/Settings.tsx` + `components/SettingsModal.tsx` |
| Route protection | ProtectedRoute           | `components/ProtectedRoute.tsx`                        |
| Top navigation   | Navbar                   | `components/Navbar.tsx`                                |
| Toast alerts     | ToastContainer           | `components/ToastContainer.tsx`                        |
| API client       | api                      | `lib/api.ts`                                           |
| PWA              | pwa                      | `lib/pwa.ts`                                           |
| Auth state       | AuthContext              | `context/AuthContext.tsx`                              |
| Toast state      | ToastContext             | `context/ToastContext.tsx`                             |

---

**Generated:** October 25, 2025  
**Version:** 1.0  
**Status:** Complete Reference Guide
