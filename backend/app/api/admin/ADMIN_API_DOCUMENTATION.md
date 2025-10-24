# Admin Recommender API Documentation

## Overview

The Admin Recommender API provides endpoints to manage the recommendation engine during runtime, including hot-reloading rules without restarting the server.

## Base URL

```
http://127.0.0.1:8000/admin/recommender
```

## Authentication

All admin endpoints require authentication using an `ADMIN_SECRET` token.

### Setup

1. Set the `ADMIN_SECRET` environment variable before starting the server:

```bash
export ADMIN_SECRET="your-secret-token"
```

Or on Windows PowerShell:

```powershell
$env:ADMIN_SECRET="your-secret-token"
```

### Authorization Header

Include the token in all requests using the Authorization header:

```
Authorization: Bearer <ADMIN_SECRET>
```

## Endpoints

### 1. Reload Rules

**Endpoint:** `POST /admin/recommender/reload-rules`

**Description:** Force reload the recommendation rules from the YAML file.

**Authentication:** Required (Bearer token)

**Request:**

```bash
curl -X POST http://127.0.0.1:8000/admin/recommender/reload-rules \
  -H "Authorization: Bearer your-secret-token" \
  -H "Content-Type: application/json"
```

**Response (200 OK):**

```json
{
  "status": "success",
  "rules_loaded": 42,
  "rules_path": "/path/to/backend/app/recommender/rules.yaml",
  "timestamp": "2025-10-25T00:22:41.123456"
}
```

**Error Responses:**

- `401 Unauthorized`: Missing Authorization header
- `403 Forbidden`: Invalid admin token
- `500 Internal Server Error`: Failed to load rules file

### 2. Get Engine Status

**Endpoint:** `GET /admin/recommender/status`

**Description:** Get the current status of the recommendation engine.

**Authentication:** Required (Bearer token)

**Request:**

```bash
curl http://127.0.0.1:8000/admin/recommender/status \
  -H "Authorization: Bearer your-secret-token"
```

**Response (200 OK):**

```json
{
  "status": "ready",
  "rules_loaded": 42,
  "rules_path": "/path/to/backend/app/recommender/rules.yaml",
  "engine_initialized": true
}
```

**Error Responses:**

- `401 Unauthorized`: Missing Authorization header
- `403 Forbidden`: Invalid admin token

## Usage Examples

### Python

```python
import requests

ADMIN_TOKEN = "your-secret-token"
BASE_URL = "http://127.0.0.1:8000/admin/recommender"

headers = {
    "Authorization": f"Bearer {ADMIN_TOKEN}",
    "Content-Type": "application/json"
}

# Reload rules
response = requests.post(f"{BASE_URL}/reload-rules", headers=headers)
print(response.json())

# Get status
response = requests.get(f"{BASE_URL}/status", headers=headers)
print(response.json())
```

### JavaScript/Fetch

```javascript
const ADMIN_TOKEN = "your-secret-token";
const BASE_URL = "http://127.0.0.1:8000/admin/recommender";

const headers = {
  Authorization: `Bearer ${ADMIN_TOKEN}`,
  "Content-Type": "application/json",
};

// Reload rules
fetch(`${BASE_URL}/reload-rules`, {
  method: "POST",
  headers,
})
  .then((r) => r.json())
  .then(console.log);

// Get status
fetch(`${BASE_URL}/status`, {
  headers,
})
  .then((r) => r.json())
  .then(console.log);
```

### cURL

```bash
# Set token
ADMIN_TOKEN="your-secret-token"

# Reload rules
curl -X POST http://127.0.0.1:8000/admin/recommender/reload-rules \
  -H "Authorization: Bearer $ADMIN_TOKEN"

# Get status
curl http://127.0.0.1:8000/admin/recommender/status \
  -H "Authorization: Bearer $ADMIN_TOKEN"
```

## Workflow

### Development Setup

1. **Start the backend with ADMIN_SECRET:**

```bash
export ADMIN_SECRET="dev-secret"
cd backend
python -m uvicorn app.main:app --reload
```

2. **Test the endpoints:**

```bash
# Check initial status
curl http://127.0.0.1:8000/admin/recommender/status \
  -H "Authorization: Bearer dev-secret"

# Edit rules.yaml file
# Then reload without restarting server
curl -X POST http://127.0.0.1:8000/admin/recommender/reload-rules \
  -H "Authorization: Bearer dev-secret"

# Verify new rules loaded
curl http://127.0.0.1:8000/admin/recommender/status \
  -H "Authorization: Bearer dev-secret"
```

### Production Deployment

1. **Set ADMIN_SECRET in environment:**

```bash
# In your deployment configuration (Docker, K8s, etc.)
export ADMIN_SECRET="<strong-random-token>"
```

2. **Use only through authorized admin dashboard/CLI**

3. **Monitor rule reload operations:**

```bash
# Watch server logs for reload confirmations
# Look for: "Admin request: Reloading recommendation rules"
# And: "Successfully reloaded X rules"
```

## Security Considerations

- **ADMIN_SECRET**: Use a strong, randomly-generated token
- **HTTPS**: Always use HTTPS in production
- **Token Rotation**: Consider implementing token rotation for production
- **Logging**: All admin operations are logged at INFO level
- **Rate Limiting**: Consider adding rate limiting in production
- **Audit Trail**: All successful and failed attempts are logged

## Troubleshooting

### Token Not Working

**Error:** `403 Forbidden - Invalid admin token`

**Solution:** Verify ADMIN_SECRET is set correctly:

```bash
echo $ADMIN_SECRET  # Check the token value
```

### Rules File Not Found

**Error:** `500 Internal Server Error - Rules file error`

**Solution:** Verify the rules.yaml file exists:

```bash
ls -la backend/app/recommender/rules.yaml
```

### YAML Parse Error

**Error:** `500 Internal Server Error - Failed to reload rules`

**Solution:** Validate the YAML syntax:

```bash
python -c "import yaml; yaml.safe_load(open('backend/app/recommender/rules.yaml'))"
```

## Implementation Details

### File Structure

```
backend/app/api/
├── admin/
│   ├── __init__.py           # Package initialization
│   ├── recommender.py        # Recommender admin endpoints
│   └── test_admin_api.py     # Test script
└── v1/
    └── ... (existing)
```

### Architecture

- **Global Engine Instance**: The RuleEngine is loaded once and cached
- **Hot-Reload**: POST `/reload-rules` creates a new instance
- **Atomic Updates**: Engine is replaced atomically to avoid race conditions
- **Graceful Fallback**: If reload fails, previous rules remain active

### Logging

All admin operations are logged at the recommender level:

```
INFO - Admin request: Reloading recommendation rules
INFO - Successfully reloaded 42 rules from /path/to/rules.yaml
WARNING - Invalid admin token attempt from authorization header
ERROR - Failed to reload rules: <error details>
```

## API Reference

See `backend/app/api/admin/recommender.py` for full docstrings and type hints.
