# Admin API Quick Reference

## Start Backend with Admin Enabled

```bash
# Linux/Mac
export ADMIN_SECRET="your-secret-token"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000

# Windows PowerShell
$env:ADMIN_SECRET="your-secret-token"
python -m uvicorn backend.app.main:app --host 127.0.0.1 --port 8000
```

## Reload Rules (without restart)

```bash
curl -X POST http://127.0.0.1:8000/admin/recommender/reload-rules \
  -H "Authorization: Bearer your-secret-token"
```

## Check Engine Status

```bash
curl http://127.0.0.1:8000/admin/recommender/status \
  -H "Authorization: Bearer your-secret-token"
```

## Python Example

```python
import requests
import os

token = os.getenv("ADMIN_SECRET")
headers = {"Authorization": f"Bearer {token}"}

# Reload rules
resp = requests.post(
    "http://127.0.0.1:8000/admin/recommender/reload-rules",
    headers=headers
)
print(resp.json())

# Get status
resp = requests.get(
    "http://127.0.0.1:8000/admin/recommender/status",
    headers=headers
)
print(resp.json())
```

## JavaScript Example

```javascript
const token = "your-secret-token";
const headers = { Authorization: `Bearer ${token}` };

// Reload rules
fetch("http://127.0.0.1:8000/admin/recommender/reload-rules", {
  method: "POST",
  headers,
})
  .then((r) => r.json())
  .then((data) => console.log("Rules reloaded:", data));

// Get status
fetch("http://127.0.0.1:8000/admin/recommender/status", {
  headers,
})
  .then((r) => r.json())
  .then((data) => console.log("Status:", data));
```

## Response Examples

### Reload Rules Success

```json
{
  "status": "success",
  "rules_loaded": 42,
  "rules_path": "/path/to/rules.yaml",
  "timestamp": "2025-10-25T00:26:40.123456"
}
```

### Engine Status

```json
{
  "status": "ready",
  "rules_loaded": 42,
  "rules_path": "/path/to/rules.yaml",
  "engine_initialized": true
}
```

## Error Codes

| Code | Meaning              | Solution                                          |
| ---- | -------------------- | ------------------------------------------------- |
| 200  | Success              | Request worked                                    |
| 401  | No auth header       | Add `Authorization: Bearer <token>`               |
| 403  | Bad token            | Check token matches `ADMIN_SECRET`                |
| 500  | No secret configured | Set `ADMIN_SECRET` env var                        |
| 500  | Rules file not found | Check `backend/app/recommender/rules.yaml` exists |

## Files

- **Implementation:** `backend/app/api/admin/`
- **Full Docs:** `backend/app/api/admin/ADMIN_API_DOCUMENTATION.md`
- **Test Script:** `backend/app/api/admin/test_admin_api.py`
- **Summary:** `ADMIN_API_IMPLEMENTATION.md` (root)

## Run Tests

```bash
cd backend
python app/api/admin/test_admin_api.py
```
