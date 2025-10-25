# Toast System - Quick Start & Examples

Simple, clean toast notification API. Copy & paste these examples into your components!

---

## 30-Second Setup

```tsx
import { useToast } from "../context/ToastContext";

export default function MyComponent() {
  const { success, error, info } = useToast();

  return <button onClick={() => success("✓ Done!")}>Show Toast</button>;
}
```

That's it! 🎉

---

## Common Examples

### Example 1: Login Form

```tsx
import { useToast } from "../context/ToastContext";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";

export default function LoginForm() {
  const { success, error } = useToast();
  const { login } = useAuth();
  const navigate = useNavigate();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();

    if (!email || !password) {
      error("Email and password required");
      return;
    }

    try {
      await login(email, password);
      success("✓ Welcome back!");
      navigate("/dashboard");
    } catch (err: any) {
      error(err.message || "Login failed");
    }
  };

  return (
    <form onSubmit={handleSubmit}>
      <input
        value={email}
        onChange={(e) => setEmail(e.target.value)}
        placeholder="Email"
        required
      />
      <input
        type="password"
        value={password}
        onChange={(e) => setPassword(e.target.value)}
        placeholder="Password"
        required
      />
      <button type="submit">Login</button>
    </form>
  );
}
```

### Example 2: Image Analysis with Status

```tsx
export default function AnalyzePage() {
  const { success, error, info } = useToast();
  const [analyzing, setAnalyzing] = useState(false);

  const handleAnalyze = async (file: File) => {
    try {
      setAnalyzing(true);
      info("Processing your image...");

      const result = await api.analyzeImage(file);

      success("✓ Analysis complete!");
      displayResults(result);
    } catch (err: any) {
      error(err.response?.data?.message || "Analysis failed");
    } finally {
      setAnalyzing(false);
    }
  };

  return (
    <div>
      <input
        type="file"
        accept="image/*"
        onChange={(e) => {
          if (e.target.files?.[0]) {
            handleAnalyze(e.target.files[0]);
          }
        }}
        disabled={analyzing}
      />
      {analyzing && <p>Processing...</p>}
    </div>
  );
}
```

### Example 3: Delete Confirmation

```tsx
const handleDelete = async (id: string) => {
  const { success, error } = useToast();

  if (!window.confirm("Are you sure? This cannot be undone.")) {
    return;
  }

  try {
    await api.delete(id);
    success("✓ Item deleted!");
    refresh();
  } catch (err) {
    error("Failed to delete item");
  }
};
```

### Example 4: Form Validation

```tsx
export default function UpdateProfileForm() {
  const { success, error } = useToast();
  const [age, setAge] = useState("");

  const handleSave = async () => {
    if (!age) {
      error("Age is required");
      return;
    }

    if (parseInt(age) < 18) {
      error("Age must be 18 or older");
      return;
    }

    try {
      await api.updateProfile({ age });
      success("✓ Profile updated!");
    } catch (err) {
      error("Failed to save");
    }
  };

  return (
    <>
      <input
        type="number"
        value={age}
        onChange={(e) => setAge(e.target.value)}
        placeholder="Age"
      />
      <button onClick={handleSave}>Save</button>
    </>
  );
}
```

### Example 5: API Error Handling

```tsx
const makeApiCall = async () => {
  const { error, info, success } = useToast();

  try {
    info("Loading...");
    const data = await api.fetchData();
    success("✓ Data loaded!");
    return data;
  } catch (err: any) {
    // Graceful error message fallback
    const message =
      err.response?.data?.message || // API error message
      err.response?.data?.detail || // Alternative API field
      err.message || // JavaScript error
      "Server error";

    error(message);
    throw err;
  }
};
```

### Example 6: Async Operations

```tsx
const handleBatchUpload = async (files: File[]) => {
  const { success, error, info } = useToast();

  try {
    info(`Uploading ${files.length} files...`);

    const results = await Promise.all(
      files.map((file) => api.uploadFile(file))
    );

    success(`✓ Uploaded ${results.length} files!`);
    refresh();
  } catch (err) {
    error("Failed to upload files");
  }
};
```

### Example 7: Conditional Feedback

```tsx
export default function RatingForm() {
  const { success, info } = useToast();
  const [rating, setRating] = useState(0);

  const handleSubmit = async () => {
    if (rating === 0) {
      error("Please select a rating");
      return;
    }

    try {
      await api.submitFeedback({ rating });

      if (rating >= 4) {
        success("✓ Thanks for the amazing feedback!");
      } else if (rating >= 2) {
        info("We'll work on improving!");
      } else {
        success("✓ Your feedback helps us improve!");
      }
    } catch (err) {
      error("Failed to submit");
    }
  };

  return (
    <>
      <RatingSelector value={rating} onChange={setRating} />
      <button onClick={handleSubmit}>Submit</button>
    </>
  );
}
```

### Example 8: Multi-Step Process

```tsx
const handleCheckout = async () => {
  const { success, error, info } = useToast();

  try {
    info("Validating cart...");
    await validateCart();

    info("Processing payment...");
    await processPayment();

    info("Confirming order...");
    await confirmOrder();

    success("✓ Order placed successfully!");
    navigate("/orders");
  } catch (err) {
    error("Checkout failed - please try again");
  }
};
```

---

## API Reference (Simple)

```typescript
// Three methods available:
const { success, error, info } = useToast();

// Show success (green, ✓ icon)
success("Message here");

// Show error (red, ✕ icon)
error("Error message here");

// Show info (blue, ℹ icon)
info("Info message here");
```

**Features:**

- Auto-dismisses after 3.5 seconds
- Click to dismiss manually
- Multiple toasts stack vertically
- Smooth slide-in animation

---

## Best Practices

✅ **DO**

- Use friendly, user-facing messages
- Call `success()` after successful operations
- Use descriptive error messages
- Use `info()` for loading states

❌ **DON'T**

- Use long, technical messages
- Include error codes
- Show sensitive information
- Spam toasts in loops

---

## Files

- **Context**: `frontend/src/context/ToastContext.tsx`
- **Container**: `frontend/src/components/ToastContainer.tsx`
- **Docs**: `TOAST_API.md` (full reference)

---

## That's it! 🚀

Copy examples above and customize for your needs. Happy toasting!
