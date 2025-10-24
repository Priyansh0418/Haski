# Audit Logger - Quick Reference

## Quick Start

```python
from backend.app.recommender.audit_logger import get_audit_logger

logger = get_audit_logger()

# Log successful recommendation
logger.log_recommendation(
    user_id=5,
    analysis_id=10,
    applied_rules=["r001_acne_routine", "r002_acne_diet"],
    recommendation={"routines": [...], "products": [...], "diet": [...]},
    confidence_score=0.87
)

# Log rule that didn't apply
logger.log_rule_not_applied(
    user_id=5,
    analysis_id=10,
    rule_id="r007_anti_aging",
    reason="User age too young"
)

# Log error
logger.log_analysis_error(
    user_id=5,
    analysis_id=10,
    error_message="Invalid analysis data"
)
```

## API Methods

| Method                   | Purpose                   | Logs To   |
| ------------------------ | ------------------------- | --------- |
| `log_recommendation()`   | Successful recommendation | DB + File |
| `log_rule_not_applied()` | Rule wasn't applied       | DB + File |
| `log_analysis_error()`   | Generation failed         | File      |

## Log Locations

**File Logs:** `backend/logs/recommendations_audit.log`  
**Rotates:** Daily at midnight (keeps 30 days)  
**Database:** `rule_logs` table

## Log Entry Format

```
2025-10-25 14:32:15 | INFO | user_id=5 | analysis_id=10 | rules=3 | score=0.87 | routines=3, products=5, diet=2
```

## Database Query Examples

```python
from backend.app.db.session import SessionLocal
from backend.app.recommender.models import RuleLog

db = SessionLocal()

# Get all logs for an analysis
logs = db.query(RuleLog).filter(RuleLog.analysis_id == 10).all()

# Get only applied rules
applied = db.query(RuleLog).filter(
    RuleLog.analysis_id == 10,
    RuleLog.applied == True
).all()

# Get rules by category
skincare_rules = db.query(RuleLog).filter(
    RuleLog.rule_category == "skincare"
).all()
```

## Integration with Recommendation Engine

```python
from backend.app.recommender.engine import RuleEngine
from backend.app.recommender.audit_logger import get_audit_logger

engine = RuleEngine()
logger = get_audit_logger()

recommendation, applied_rules = engine.apply_rules(
    analysis=analysis_data,
    profile=profile_data
)

logger.log_recommendation(
    user_id=user_id,
    analysis_id=analysis_id,
    applied_rules=applied_rules,
    recommendation=recommendation,
    confidence_score=recommendation.get("confidence", 0.0)
)
```

## Recommendation Summary Format

Logs automatically generate summaries:

```
routines=3, products=5, diet=2
```

Or with escalation:

```
routines=2, products=3, diet=1, escalation=urgent
```

## Rule Categories

| Category     | Examples                           |
| ------------ | ---------------------------------- |
| `skincare`   | r001, r004, r005, r006, r008, r009 |
| `diet`       | r002, r003                         |
| `hair`       | r009_hair_care                     |
| `escalation` | Any rule with "escalation"         |

## Common Queries

**Analyze rule effectiveness:**

```python
from sqlalchemy import func

effectiveness = db.query(
    RuleLog.rule_id,
    RuleLog.rule_name,
    func.count(RuleLog.id).label('times_applied'),
    func.count(RuleLog.applied).label('successful')
).filter(
    RuleLog.applied == True
).group_by(
    RuleLog.rule_id
).order_by(
    func.count(RuleLog.id).desc()
).all()
```

**Find failed analyses:**

```python
from backend.app.models.db_models import Analysis

failed = db.query(Analysis).filter(
    ~Analysis.id.in_(
        db.query(RuleLog.analysis_id).filter(RuleLog.applied == True)
    )
).all()
```

**Latest recommendations:**

```python
latest = db.query(RuleLog).order_by(
    RuleLog.created_at.desc()
).limit(10).all()
```

## File Operations

**View recent logs:**

```bash
tail -f backend/logs/recommendations_audit.log
```

**Search for user:**

```bash
grep "user_id=5" backend/logs/recommendations_audit.log
```

**Count recommendations today:**

```bash
grep "$(date +%Y-%m-%d)" backend/logs/recommendations_audit.log | wc -l
```

## Configuration

**Custom log directory:**

```python
from backend.app.recommender.audit_logger import RecommendationAuditLogger
logger = RecommendationAuditLogger(log_dir="/path/to/logs")
```

**Change rotation (edit audit_logger.py):**

```python
file_handler = logging.handlers.TimedRotatingFileHandler(
    ...
    when="midnight",    # daily
    backupCount=30      # keep 30 days
)
```

## Testing

```bash
# Run all tests
pytest backend/app/recommender/test_audit_logger.py -v

# Run specific test
pytest backend/app/recommender/test_audit_logger.py::TestFileLogging -v
```

## Troubleshooting

| Issue              | Solution                          |
| ------------------ | --------------------------------- |
| No log files       | Check `backend/logs/` permissions |
| DB entries missing | Verify database connection        |
| Large log files    | Automatic rotation is 30 days     |
| Slow performance   | Logging uses async error handling |

## Rule Name Mapping

| Rule ID | Name                  |
| ------- | --------------------- |
| r001    | Acne Skincare Routine |
| r002    | Acne-Friendly Diet    |
| r003    | Hydration Tips        |
| r004    | Dry Skin Treatment    |
| r005    | Oily Skin Management  |
| r006    | Sensitive Skin Care   |
| r007    | Anti-Aging Routine    |
| r008    | Sun Protection        |
| r009    | Hair Care Routine     |

## Files

- **Module:** `backend/app/recommender/audit_logger.py` (300+ lines)
- **Integration:** `backend/app/recommender/audit_logger_integration.py`
- **Tests:** `backend/app/recommender/test_audit_logger.py`
- **Documentation:** `AUDIT_LOGGER_DOCUMENTATION.md`
- **Logs:** `backend/logs/recommendations_audit.log`
- **Database:** `rule_logs` table
