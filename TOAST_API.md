# Toast Notification System - API Reference

## Overview

Simple, lightweight toast notification system with a clean API for user feedback.

- **3 types**: `success`, `error`, `info`
- **Auto-dismiss**: 3.5 seconds
- **Queue-based**: Multiple toasts stack vertically
- **Smooth animations**: Enter/exit transitions
- **Zero dependencies**: Pure React Context API

---

## Quick Start

### 1. Use Hook in Any Component

```tsx
import { useToast } from "../context/ToastContext";

export default function MyComponent() {
  const { success, error, info } = useToast();

  return <button onClick={() => success("✓ Saved!")}>Save</button>;
}
```

### 2. Toast Types

```tsx
const { success, error, info } = useToast();

// Success - Green notification
success("✓ Operation completed!");

// Error - Red notification
error("✕ Something went wrong!");

// Info - Blue notification
info("ℹ Please wait...");
```

---

## Complete API

### `useToast()` Hook

Returns an object with three methods:

```typescript
interface Toast {
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
}
```

### Methods

#### `success(message: string)`

- Shows green success notification
- Auto-dismisses after 3.5 seconds
- Icon: ✓

```tsx
success("Profile updated successfully!");
```

#### `error(message: string)`

- Shows red error notification
- Auto-dismisses after 3.5 seconds
- Icon: ✕

```tsx
error("Failed to save changes!");
```

#### `info(message: string)`

- Shows blue info notification
- Auto-dismisses after 3.5 seconds
- Icon: ℹ

```tsx
info("Loading your data...");
```

---

## Common Patterns

### Form Submission

```tsx
import { useToast } from "../context/ToastContext";

export default function LoginForm() {
  const { success, error } = useToast();

  const handleSubmit = async (formData: any) => {
    try {
      await api.login(formData);
      success("Welcome back!");
      navigate("/dashboard");
    } catch (err) {
      error("Invalid email or password");
    }
  };

  return <form onSubmit={handleSubmit}>{/* form fields */}</form>;
}
```

### Delete Confirmation

```tsx
const handleDelete = async (id: string) => {
  if (!confirm("Are you sure?")) return;

  try {
    await api.delete(id);
    success("Item deleted!");
    refresh();
  } catch (err) {
    error("Failed to delete item");
  }
};
```

### API Error Handling

```tsx
const { error } = useToast();

try {
  const data = await api.fetch("/endpoint");
} catch (err: any) {
  error(err.response?.data?.message || "Server error");
}
```

### File Upload

```tsx
const handleUpload = async (file: File) => {
  try {
    info("Uploading...");
    await api.uploadFile(file);
    success("File uploaded successfully!");
  } catch (err) {
    error("Upload failed");
  }
};
```

---

## Behavior

### Auto-Dismiss

- All toasts automatically dismiss after **3.5 seconds**
- Manual dismiss available via close button (✕) or click on toast

### Stacking

- Multiple toasts stack vertically
- Latest toast appears at the bottom
- Gap of 12px between toasts

### Animations

- **Enter**: Slide in from right + fade in (300ms)
- **Exit**: Immediate removal on dismiss

---

## Styling

### Colors

| Type    | Background   | Icon | Hover           |
| ------- | ------------ | ---- | --------------- |
| success | bg-green-500 | ✓    | Enhanced shadow |
| error   | bg-red-500   | ✕    | Enhanced shadow |
| info    | bg-blue-500  | ℹ    | Enhanced shadow |

### Layout

- Fixed positioning: bottom-right corner
- Responsive: max-width on smaller screens
- Clickable to dismiss

---

## Implementation Details

### ToastContext

```tsx
export interface ToastContextType {
  toasts: Toast[];              // Current toast queue
  removeToast: (id: string) => void;  // Remove by ID
  success: (message: string) => void;
  error: (message: string) => void;
  info: (message: string) => void;
}

export const ToastProvider = ({ children }) => { ... };
export const useToast = () => { ... };
```

### Toast Interface

```tsx
export interface Toast {
  id: string; // Unique ID (timestamp + random)
  message: string; // Display text
  type: "success" | "error" | "info";
}
```

---

## Best Practices

✅ **DO**

- Use descriptive, user-friendly messages
- Call `success()` after successful operations
- Call `error()` with helpful error details
- Use `info()` for status updates during long operations

❌ **DON'T**

- Don't use `warning` type (not available, use `info` instead)
- Don't pass duration parameter (fixed at 3.5s)
- Don't nest multiple toast calls in rapid succession
- Don't include technical error codes, explain in user terms

---

## Files

- **Context**: `frontend/src/context/ToastContext.tsx`
- **Container**: `frontend/src/components/ToastContainer.tsx`
- **App Integration**: `frontend/src/App.tsx` (ToastProvider wraps app)

---

## Examples

### Complete Login Flow

```tsx
import { useToast } from "../context/ToastContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function Login() {
  const { success, error } = useToast();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await login(email, password);
      success("Login successful!");
      navigate("/dashboard");
    } catch (err) {
      error("Invalid credentials");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input value={email} onChange={(e) => setEmail(e.target.value)} />
      <input value={password} onChange={(e) => setPassword(e.target.value)} />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Analysis Upload

```tsx
export default function AnalyzePage() {
  const { success, error, info } = useToast();
  const [uploading, setUploading] = useState(false);

  const handleImageUpload = async (file: File) => {
    try {
      setUploading(true);
      info("Processing image...");
      const result = await api.analyzeImage(file);
      success("Analysis complete!");
      displayResults(result);
    } catch (err) {
      error("Failed to analyze image");
    } finally {
      setUploading(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        onChange={(e) => {
          if (e.target.files?.[0]) {
            handleImageUpload(e.target.files[0]);
          }
        }}
      />
    </div>
  );
}
```

---

## Migration from Old System

If you were using the old `warning` type or custom duration:

### Old (Remove)

```tsx
warning("Message", 5000); // ❌ Not supported
```

### New (Use)

```tsx
info("Message"); // ✅ Use info for warnings
```

---

## Support

For issues or questions:

1. Check the examples above
2. Review `ToastContext.tsx` implementation
3. Check `ToastContainer.tsx` rendering logic
