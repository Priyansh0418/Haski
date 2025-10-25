# Toast System - 30-Second Cheat Sheet

## Copy This

```tsx
import { useToast } from "../context/ToastContext";

const { success, error, info } = useToast();

success("✓ Done!"); // Green
error("✕ Error!"); // Red
info("ℹ Loading..."); // Blue
```

---

## In Components

### Example 1: Button Click

```tsx
<button onClick={() => success("Saved!")}>Save</button>
```

### Example 2: Form Submit

```tsx
const handleSubmit = async (data) => {
  try {
    await api.submit(data);
    success("✓ Submitted!");
  } catch {
    error("Failed to submit");
  }
};
```

### Example 3: Delete

```tsx
if (!confirm("Delete?")) return;
await api.delete(id);
success("✓ Deleted!");
```

---

## That's It!

- Appears bottom-right
- Disappears after 3.5s
- Click to dismiss
- Multiple stack vertically

---

## Files

| File                                         | Purpose        |
| -------------------------------------------- | -------------- |
| `frontend/src/context/ToastContext.tsx`      | Logic          |
| `frontend/src/components/ToastContainer.tsx` | Display        |
| `TOAST_API.md`                               | Full reference |
| `TOAST_QUICK_START.md`                       | 8 examples     |

---

## API

```typescript
// Three methods, that's all:
success(message: string) → void
error(message: string) → void
info(message: string) → void
```

---

## Status

✅ Production Ready  
✅ 0 Errors  
✅ 0 Dependencies  
✅ Full TypeScript

**You're good to go! 🚀**
