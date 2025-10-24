# Feedback Processor Quick Reference

## Overview

The FeedbackProcessor exports anonymized feedback data to CSV for ML model training. It handles privacy through ID hashing and age bucketing.

---

## Quick Start

### Basic Usage

```python
from backend.app.recommender.feedback_processor import FeedbackProcessor
from backend.app.db.session import SessionLocal

# Create processor
db = SessionLocal()
processor = FeedbackProcessor(
    db_session=db,
    output_dir="ml/feedback_training"
)

# Export last 30 days of feedback
stats = processor.process_and_export(
    days_back=30,
    min_feedback_fields=2  # Minimum ratings required
)

print(f"Exported {stats.exported_records} records to {stats.export_filename}")
```

### Command Line

```bash
# Export last 7 days
python backend/app/recommender/feedback_processor.py --days 7

# Bulk export last 90 days
python backend/app/recommender/feedback_processor.py --days 90 --bulk

# Specify output directory
python backend/app/recommender/feedback_processor.py --days 30 --output ml/training_data/
```

---

## Core Classes

### FeedbackProcessor

Main class for processing and exporting feedback.

**Methods:**

```python
def process_and_export(
    days_back: int = 1,
    min_feedback_fields: int = 1
) -> FeedbackProcessingStats
```

- Main entry point
- Returns: FeedbackProcessingStats with results
- Creates CSV in output_dir

```python
def _hash_id(id_value: int) -> str
```

- Anonymize user/analysis IDs
- Returns: 16-char SHA256 hash

```python
def _bucket_age(age: int | None) -> str | None
```

- Bucket age into ranges
- Returns: "<18" | "18-25" | "25-35" | "35-50" | "50+" | None

```python
def _get_pair_hash(pair: FeedbackTrainingPair) -> str
```

- Generate deduplication hash
- Combines: analysis_hash + recommendation_id + timestamp

```python
def _export_to_csv(pairs: List[FeedbackTrainingPair]) -> str
```

- Export to CSV file
- Returns: Filename with full path

### FeedbackTrainingPair

Output data format for training records.

**Fields:**

```python
analysis_hash: str              # SHA256 hashed analysis_id
recommendation_id: str          # Pseudo-anonymized ID
helpful_rating: int | None      # 1-5 scale
product_satisfaction: int | None # 1-5 scale
routine_completion_pct: int | None # 0-100%
would_recommend: bool | None    # True/False
conditions_detected: str        # Comma-separated
rules_applied: str              # Comma-separated
timeframe: str                  # "1_week", "2_weeks", etc.
age_range: str                  # "<18", "18-25", "25-35", "35-50", "50+"
feedback_timestamp: str         # ISO format
export_date: str                # ISO format when exported
```

### FeedbackProcessingStats

Statistics from processing run.

**Fields:**

```python
total_feedback_records: int     # Total records queried
exported_records: int           # Records with min fields
deduplicated_records: int       # Duplicates removed
anonymized_records: int         # Anonymization applied
skipped_records: int            # Records with <min fields
errors: int                     # Processing errors
execution_time_seconds: float   # Time elapsed
export_filename: str            # Output CSV filename
```

---

## Anonymization Strategy

### User ID → Analysis Hash

```
Original: user_id=42
Process:  SHA256(42)
Result:   "8f1c5a7d2e9b3..."  # 16 chars (shortened)
CSV:      8f1c5a7d2e9b3...
```

**Purpose:** Prevent identification of users while preserving data linking

### Age → Age Range

```
Age: 28
Ranges: <18 | 18-25 | 25-35 | 35-50 | 50+
Result: 25-35
```

**Purpose:** Group users for demographics while hiding exact age

### Data Removal

```
❌ Removed: user_id, raw image URLs (unless opted-in)
✅ Kept:    conditions, ratings, timestamps, rules applied
✅ Derived: age ranges, hashed IDs, feedback aggregates
```

---

## CSV Output Format

**Filename:** `feedback_training_YYYYMMDD_HHMMSS.csv`

**Headers:**

```
analysis_hash,recommendation_id,helpful_rating,product_satisfaction,routine_completion_pct,would_recommend,conditions_detected,rules_applied,timeframe,age_range,feedback_timestamp,export_date
```

**Example Row:**

```
8f1c5a7d,rec_20251025_001,5,4,80,True,"acne,oily_skin","r001,r002",2_weeks,25-35,2025-10-25T10:00:00,2025-10-25T12:00:00
```

**Characteristics:**

- One row per feedback record
- No user IDs
- Ages bucketed
- All sensitive data removed
- Ready for ML training

---

## Integration Examples

### FastAPI Endpoint - Trigger Export

```python
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.app.db.session import get_db
from backend.app.recommender.feedback_processor import FeedbackProcessor

router = APIRouter()

@router.post("/admin/export-feedback")
async def trigger_feedback_export(
    days_back: int = 30,
    db: Session = Depends(get_db)
):
    """Trigger manual feedback export."""
    processor = FeedbackProcessor(
        db_session=db,
        output_dir="ml/feedback_training"
    )

    stats = processor.process_and_export(
        days_back=days_back,
        min_feedback_fields=2
    )

    return {
        "status": "success",
        "exported_records": stats.exported_records,
        "deduplicated_records": stats.deduplicated_records,
        "filename": stats.export_filename,
        "execution_time_seconds": stats.execution_time_seconds
    }
```

### Scheduled Task - Daily Export

```python
from apscheduler.schedulers.background import BackgroundScheduler
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.recommender.feedback_processor import FeedbackProcessor

scheduler = BackgroundScheduler()

def daily_feedback_export_job():
    """Export feedback daily at 2 AM UTC."""
    db = SessionLocal()
    processor = FeedbackProcessor(
        db_session=db,
        output_dir="ml/feedback_training"
    )

    stats = processor.process_and_export(
        days_back=1,  # Last 24 hours
        min_feedback_fields=2
    )

    print(f"Daily export: {stats.exported_records} records, "
          f"{stats.deduplicated_records} deduped, "
          f"in {stats.execution_time_seconds:.2f}s")

    db.close()

# Schedule job
scheduler.add_job(
    daily_feedback_export_job,
    'cron',
    hour=2,
    minute=0,
    timezone='UTC',
    id='daily_feedback_export'
)

scheduler.start()
```

### Background Task - Bulk Export

```python
from celery import shared_task
from sqlalchemy.orm import Session

from backend.app.db.session import SessionLocal
from backend.app.recommender.feedback_processor import FeedbackProcessor

@shared_task
def bulk_export_feedback_task(days_back: int = 90):
    """Celery task for bulk historical export."""
    db = SessionLocal()
    processor = FeedbackProcessor(
        db_session=db,
        output_dir="ml/feedback_training"
    )

    stats = processor.process_and_export(
        days_back=days_back,
        min_feedback_fields=2
    )

    db.close()

    return {
        "exported": stats.exported_records,
        "deduped": stats.deduplicated_records,
        "filename": stats.export_filename
    }
```

### Event Hook - Auto Export After Feedback

```python
from backend.app.recommender.feedback_processor import FeedbackProcessor

async def on_feedback_submitted(
    feedback_id: int,
    db: Session
):
    """Called when feedback is submitted."""
    # Process and export immediately for realtime updates
    processor = FeedbackProcessor(
        db_session=db,
        output_dir="ml/feedback_training"
    )

    stats = processor.process_and_export(
        days_back=1,
        min_feedback_fields=1  # Include partial feedback
    )

    # Log or track exports
    logger.info(f"Feedback export triggered: {stats.export_filename}")
```

---

## Testing

### Run All Tests

```bash
pytest backend/app/recommender/test_feedback_processor.py -v
```

**Expected Output:**

```
22 passed in 0.73s ✅
```

### Test Coverage

```bash
pytest backend/app/recommender/test_feedback_processor.py \
    --cov=backend.app.recommender.feedback_processor \
    --cov-report=html
```

### Individual Test Classes

```bash
# Test anonymization
pytest backend/app/recommender/test_feedback_processor.py::TestAnonymization -v

# Test CSV export
pytest backend/app/recommender/test_feedback_processor.py::TestCSVExport -v

# Test integration
pytest backend/app/recommender/test_feedback_processor.py::TestProcessAndExport -v
```

---

## Configuration

### Age Bucketing Ranges

Can be customized in `_bucket_age()` method:

```python
def _bucket_age(self, age: int | None) -> str | None:
    if age is None:
        return None
    elif age < 18:
        return "<18"
    elif age < 25:
        return "18-25"
    elif age < 35:
        return "25-35"
    elif age < 50:
        return "35-50"
    else:
        return "50+"
```

### Minimum Feedback Fields

Control data quality by adjusting `min_feedback_fields`:

```python
# Require at least 2 ratings per record
stats = processor.process_and_export(
    days_back=30,
    min_feedback_fields=2  # Strict: drop records with <2 fields
)

# Include partial feedback (1+ field)
stats = processor.process_and_export(
    days_back=30,
    min_feedback_fields=1  # Lenient: include partial records
)
```

### Output Directory

Configure where CSV files are saved:

```python
processor = FeedbackProcessor(
    db_session=db,
    output_dir="/absolute/path/to/ml/feedback_training"
)

# Or use relative path (from project root)
processor = FeedbackProcessor(
    db_session=db,
    output_dir="ml/feedback_training"
)
```

---

## Privacy Checklist

Before production deployment:

- [ ] Verify no raw user_ids in CSV export
- [ ] Confirm age values bucketed (not exact)
- [ ] Check image URLs not included (unless opted-in)
- [ ] Validate SHA256 hashing applied
- [ ] Test deduplication working
- [ ] Confirm file permissions restricted (600 or similar)
- [ ] Setup data retention policy (keep 90 days?)
- [ ] Document privacy processing for compliance
- [ ] Add data deletion for GDPR requests
- [ ] Audit logs for exports

---

## Common Workflows

### Export Last Week of Feedback

```python
processor = FeedbackProcessor(db_session=db, output_dir="ml/training")
stats = processor.process_and_export(days_back=7, min_feedback_fields=2)
print(f"Exported {stats.exported_records} records to {stats.export_filename}")
```

### Export All Feedback (Historical)

```python
processor = FeedbackProcessor(db_session=db, output_dir="ml/training")
stats = processor.process_and_export(days_back=365, min_feedback_fields=1)
# Note: Very large exports may take time, consider pagination
```

### Check Statistics

```python
processor = FeedbackProcessor(db_session=db, output_dir="ml/training")
stats = processor.process_and_export(days_back=30)

print(f"Total records: {stats.total_feedback_records}")
print(f"Exported: {stats.exported_records}")
print(f"Deduped: {stats.deduplicated_records}")
print(f"Skipped (insufficient data): {stats.skipped_records}")
print(f"Errors: {stats.errors}")
print(f"Time: {stats.execution_time_seconds:.2f}s")
```

### Handle Errors Gracefully

```python
processor = FeedbackProcessor(db_session=db, output_dir="ml/training")

try:
    stats = processor.process_and_export(days_back=30)
    if stats.errors > 0:
        logger.warning(f"Export completed with {stats.errors} errors")
    print(f"Successfully exported to {stats.export_filename}")
except Exception as e:
    logger.error(f"Export failed: {e}")
    # Fallback: retry or alert admin
```

---

## Troubleshooting

### No Records Exported

**Problem:** `exported_records=0` despite feedback in database

**Solutions:**

1. Check `min_feedback_fields` threshold - too high?
2. Verify feedback records have at least one rating field
3. Check date range - use `days_back=-1` to include all records
4. Confirm database has RecommendationFeedback records

### CSV File Not Created

**Problem:** `export_filename=""` after export

**Solutions:**

1. No feedback records met criteria (check stats.skipped_records)
2. `min_feedback_fields` too high
3. Output directory doesn't exist - create it
4. File permissions issue - check directory is writable

### Slow Performance

**Problem:** Export taking >10 seconds for 30 days

**Solutions:**

1. Reduce `days_back` parameter
2. Add database indexes on feedback tables
3. Run during off-peak hours
4. Consider pagination for very large exports

---

## File Locations

```
backend/
  app/
    recommender/
      feedback_processor.py          # Main module
      test_feedback_processor.py     # Test suite (22 tests)
      FEEDBACK_PROCESSOR_TESTS.md    # Test documentation
      FEEDBACK_PROCESSOR_QUICK_REF.md # This file

ml/
  feedback_training/                # CSV export directory
    feedback_training_20251025_120000.csv
    feedback_training_20251026_120000.csv
```

---

## Version Info

- **Module:** feedback_processor.py
- **Tests:** 22 passing (100% success rate)
- **Python:** 3.10+
- **Dependencies:** SQLAlchemy, Pydantic, datetime
- **Optional:** APScheduler (for scheduling)
