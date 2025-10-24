# Audit Logger Module - Documentation

## Overview

The Audit Logger tracks all recommendation engine activity by logging to:

1. **Database** (RuleLog table) - for queryable audit trail
2. **Rotating Log Files** - for compliance and backup

## Features

✅ Automatic daily log rotation (keeps 30 days)  
✅ Structured logging with timestamps  
✅ Database persistence for queries  
✅ User ID, Analysis ID, Rules, and Recommendation tracking  
✅ Error handling with graceful fallbacks  
✅ Rule categorization (skincare, diet, hair, escalation)

## Usage

### Basic Usage

```python
from backend.app.recommender.audit_logger import get_audit_logger

logger = get_audit_logger()

logger.log_recommendation(
    user_id=5,
    analysis_id=10,
    applied_rules=["r001_acne_routine", "r002_acne_diet"],
    recommendation={
        "routines": [...],
        "products": [...],
        "diet": [...]
    },
    confidence_score=0.87,
    product_ids=[12, 15, 18]
)
```

### With FastAPI Endpoint

```python
from fastapi import APIRouter, Depends
from backend.app.recommender.audit_logger import get_audit_logger
from backend.app.recommender.engine import RuleEngine

router = APIRouter()

@router.post("/api/v1/recommendations")
def create_recommendation(
    user_id: int,
    analysis_id: int,
    analysis_data: dict,
    profile_data: dict,
    db: Session = Depends(get_db)
):
    logger = get_audit_logger()

    try:
        engine = RuleEngine()
        recommendation, applied_rules = engine.apply_rules(
            analysis=analysis_data,
            profile=profile_data
        )

        # Log successful recommendation
        logger.log_recommendation(
            user_id=user_id,
            analysis_id=analysis_id,
            applied_rules=applied_rules,
            recommendation=recommendation,
            confidence_score=recommendation.get("confidence", 0.0)
        )

        return recommendation

    except Exception as e:
        # Log error
        logger.log_analysis_error(
            user_id=user_id,
            analysis_id=analysis_id,
            error_message=str(e)
        )
        raise
```

## Log File Format

Location: `backend/logs/recommendations_audit.log`

### Rotating Schedule

- Rotates daily at midnight
- Keeps 30 days of backups
- Old files: `recommendations_audit.log.2025-10-25`, `recommendations_audit.log.2025-10-24`, etc.

### Log Entry Examples

**Successful Recommendation:**

```
2025-10-25 14:32:15 | INFO     | user_id=5 | analysis_id=10 | rules=3 | score=0.87 | routines=3, products=5, diet=2
```

**Rule Not Applied:**

```
2025-10-25 14:35:22 | INFO     | user_id=5 | analysis_id=10 | rule_not_applied=r007_anti_aging | reason=User age 25 - anti-aging not applicable
```

**Error:**

```
2025-10-25 14:38:45 | ERROR    | user_id=5 | analysis_id=10 | recommendation_error=Invalid skin type in analysis
```

## Database Logging

Logs are also written to the `rule_logs` table for querying:

```sql
SELECT
    id,
    analysis_id,
    rule_id,
    rule_name,
    rule_category,
    applied,
    reason_not_applied,
    details,
    created_at
FROM rule_logs
WHERE analysis_id = 10;
```

### RuleLog Fields

| Field                | Type     | Description                                                   |
| -------------------- | -------- | ------------------------------------------------------------- |
| `analysis_id`        | INT      | Analysis record ID                                            |
| `rule_id`            | STRING   | Rule identifier (e.g., "r001_acne_routine")                   |
| `rule_name`          | STRING   | Human-readable rule name                                      |
| `rule_category`      | STRING   | skincare, diet, hair, escalation                              |
| `applied`            | BOOLEAN  | Whether rule was applied                                      |
| `reason_not_applied` | STRING   | Why rule wasn't applied (if applicable)                       |
| `details`            | JSON     | Additional metadata (user_id, confidence, summary, timestamp) |
| `created_at`         | DATETIME | Log entry timestamp                                           |

### Example RuleLog Entry

```json
{
  "analysis_id": 10,
  "rule_id": "r001_acne_routine",
  "rule_name": "Acne Skincare Routine",
  "rule_category": "skincare",
  "applied": true,
  "details": {
    "user_id": 5,
    "confidence_score": 0.87,
    "recommendation_summary": "routines=3, products=5, diet=2",
    "total_rules_applied": 3,
    "generated_at": "2025-10-25T14:32:15.123456"
  }
}
```

## API Methods

### log_recommendation()

Logs a successful recommendation generation.

```python
def log_recommendation(
    user_id: int,
    analysis_id: int,
    applied_rules: List[str],
    recommendation: Dict[str, Any],
    confidence_score: float = 0.0,
    product_ids: Optional[List[int]] = None
) -> None
```

**Parameters:**

- `user_id` - User ID
- `analysis_id` - Analysis record ID
- `applied_rules` - List of rule IDs applied
- `recommendation` - Complete recommendation dict
- `confidence_score` - Recommendation confidence (0-1)
- `product_ids` - List of recommended product IDs

### log_rule_not_applied()

Logs when a rule was evaluated but not applied.

```python
def log_rule_not_applied(
    user_id: int,
    analysis_id: int,
    rule_id: str,
    reason: str
) -> None
```

### log_analysis_error()

Logs when recommendation generation fails.

```python
def log_analysis_error(
    user_id: int,
    analysis_id: int,
    error_message: str
) -> None
```

## Querying Logs

### Get all recommendations for a user

```python
from backend.app.db.session import SessionLocal
from backend.app.recommender.models import RuleLog

db = SessionLocal()

# Get all rules applied for a user's analyses
user_logs = db.query(RuleLog).join(
    Analysis, RuleLog.analysis_id == Analysis.id
).filter(
    Analysis.user_id == 5
).all()

for log in user_logs:
    print(f"{log.rule_name}: {log.applied}")
```

### Get only applied rules for analysis

```python
applied_rules = db.query(RuleLog).filter(
    RuleLog.analysis_id == 10,
    RuleLog.applied == True
).all()
```

### Get rules by category

```python
diet_rules = db.query(RuleLog).filter(
    RuleLog.analysis_id == 10,
    RuleLog.rule_category == "diet"
).all()
```

### Analyze effectiveness

```python
from sqlalchemy import func

stats = db.query(
    RuleLog.rule_id,
    func.count(RuleLog.id).label('count'),
    func.count(RuleLog.applied).label('applied_count'),
    (func.count(RuleLog.applied) / func.count(RuleLog.id) * 100).label('apply_rate')
).group_by(RuleLog.rule_id).all()
```

## Configuration

### Custom Log Directory

```python
from backend.app.recommender.audit_logger import RecommendationAuditLogger

logger = RecommendationAuditLogger(log_dir="/custom/path/logs")
```

### Log Rotation Settings

Edit `audit_logger.py` to change rotation:

```python
file_handler = logging.handlers.TimedRotatingFileHandler(
    filename=str(log_file),
    when="midnight",      # Change to "weekly", "monthly" etc
    interval=1,           # Interval (1 day, 1 week, etc)
    backupCount=30,       # Keep 30 backups (change as needed)
    encoding="utf-8"
)
```

## Performance Considerations

- **Database logging** happens asynchronously with error handling
- **File logging** uses buffered I/O for efficiency
- **No blocking** - errors in logging don't affect recommendations
- **Database operations** use SessionLocal instances and close properly

## Compliance & Auditing

This logger helps with:

- **Compliance audits** - Complete trail of recommendations
- **Analytics** - Track which rules work best
- **Debugging** - Trace why specific recommendations were made
- **User support** - Show users what rules applied to their analysis
- **A/B testing** - Compare rule effectiveness over time

## Testing

Run audit logger tests:

```bash
pytest backend/app/recommender/test_audit_logger.py -v
```

Tests cover:

- File creation and rotation
- Database entry creation
- Error handling
- Log formatting
- Rule naming and categorization

## Troubleshooting

### Logs not appearing in file

1. Check `backend/logs/` directory exists
2. Verify file permissions
3. Check disk space
4. Review stderr for logging errors

### Database entries not created

1. Verify database connection works
2. Check RuleLog table exists
3. Review error logs for SQL errors

### Logs growing too large

- Rotation is automatic (30-day retention)
- Customize `backupCount` in audit_logger.py
- Archive old logs periodically

## Future Enhancements

- [ ] Elasticsearch integration for distributed logging
- [ ] Grafana dashboards for rule effectiveness
- [ ] Real-time alerting for unusual patterns
- [ ] Export logs to CSV for compliance
- [ ] Rule performance metrics and heatmaps
- [ ] User feedback correlation with applied rules
