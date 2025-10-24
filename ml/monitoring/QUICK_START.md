# Model Monitoring - Quick Reference

## One-Command Examples

### Generate Baseline (Once)

```bash
python ml/monitoring/model_monitor.py --mode baseline \
  --data-dir ml/data/val \
  --model ml/exports/skin_classifier.tflite \
  --output baseline_metrics.json
```

### Monitor for Drift (Recurring)

```bash
python ml/monitoring/model_monitor.py --mode monitor \
  --data-dir ml/data/production \
  --baseline baseline_metrics.json \
  --model ml/exports/skin_classifier.tflite \
  --output report.json --html
```

### Compare Two Datasets

```bash
python ml/monitoring/model_monitor.py --mode compare \
  --data-dir-1 ml/data/val \
  --data-dir-2 ml/data/production \
  --output comparison.json
```

---

## What Gets Monitored

| Metric          | What It Tracks          | Threshold       |
| --------------- | ----------------------- | --------------- |
| **Pixel Mean**  | Average brightness      | shift > 0.05    |
| **Pixel Std**   | Brightness variation    | shift > 0.1     |
| **Per-Channel** | R/G/B distribution      | shift > 0.05    |
| **Confidence**  | Model certainty         | shift > 0.1     |
| **Class Dist**  | Prediction distribution | distance > 0.15 |

---

## Report Outputs

### JSON Report

```json
{
  "overall_drift_detected": true/false,
  "pixel_distribution_drift": {
    "drift_detected": true/false,
    "severity": "none|low|medium|high"
  },
  "confidence_drift": {
    "drift_detected": true/false,
    "severity": "none|low|medium|high"
  },
  "class_distribution_drift": {
    "drift_detected": true/false,
    "severity": "none|low|medium|high"
  }
}
```

### HTML Report

Beautiful visual report with:

- ✓ Overall drift status
- 📊 Severity levels
- 📈 Baseline vs current metrics
- 📉 Confidence analysis
- 📋 Class distribution shifts

---

## Python API

```python
from ml.monitoring.model_monitor import DatasetAnalyzer, generate_html_report
import json

# Baseline
analyzer = DatasetAnalyzer('ml/data/val', model_path='model.tflite')
baseline = analyzer.analyze()

# Monitor
analyzer_prod = DatasetAnalyzer('ml/data/production', model_path='model.tflite')
drift_report = analyzer_prod.detect_drift(baseline)

# Check drift
if drift_report['overall_drift_detected']:
    print("⚠️ Drift detected!")

# HTML report
generate_html_report(drift_report, 'report.html')
```

---

## Drift Severity Guide

| Severity  | Meaning               | Action        |
| --------- | --------------------- | ------------- |
| ✅ None   | No significant change | Monitor       |
| ⚠️ Low    | Minor shift           | Investigate   |
| 🔶 Medium | Notable change        | Review data   |
| 🔴 High   | Significant drift     | Retrain/Alert |

---

## Common Use Cases

### 1. Daily Production Monitoring

```bash
# Create daily report
TIMESTAMP=$(date +%Y%m%d)
python ml/monitoring/model_monitor.py --mode monitor \
  --data-dir ml/data/production/$TIMESTAMP \
  --baseline baseline.json \
  --model model.tflite \
  --output reports/report_$TIMESTAMP.json \
  --html
```

### 2. New Dataset Validation

```bash
# Compare new dataset to baseline
python ml/monitoring/model_monitor.py --mode compare \
  --data-dir-1 ml/data/val \
  --data-dir-2 ml/data/new_dataset \
  --output validation.json
```

### 3. Camera/Lighting Change Detection

```bash
# Pixel drift indicates camera/environment change
python ml/monitoring/model_monitor.py --mode monitor \
  --data-dir ml/data/production \
  --baseline baseline.json \
  --output report.json
# Check: pixel_distribution_drift.severity
```

---

## Setup for Production

### 1. Initialize Once

```bash
# Generate baseline from validation data
python ml/monitoring/model_monitor.py --mode baseline \
  --data-dir ml/data/val \
  --model ml/exports/skin_classifier.tflite \
  --output /shared/baseline_metrics.json
```

### 2. Schedule Daily Check (cron)

```bash
# Add to crontab
0 2 * * * /usr/bin/python /app/ml/monitoring/model_monitor.py \
  --mode monitor \
  --data-dir /data/production/$(date +\%Y\%m\%d) \
  --baseline /shared/baseline_metrics.json \
  --model /app/ml/exports/skin_classifier.tflite \
  --output /reports/drift_$(date +\%Y\%m\%d).json \
  --html
```

### 3. Alert on Drift

```python
import json, subprocess

# Run monitor
subprocess.run([
    'python', 'ml/monitoring/model_monitor.py',
    '--mode', 'monitor',
    '--data-dir', 'ml/data/production',
    '--baseline', 'baseline.json',
    '--output', 'report.json'
])

# Check report
with open('report.json') as f:
    report = json.load(f)

if report['overall_drift_detected']:
    print("🚨 DRIFT DETECTED!")
    # Send alert, trigger retraining, etc.
```

---

## Troubleshooting

| Issue                  | Solution                                      |
| ---------------------- | --------------------------------------------- |
| "No images found"      | Check dataset structure: `ls ml/data/val/`    |
| "Model loading failed" | Verify path: `ls -lh ml/exports/model.tflite` |
| "Slow processing"      | Reduce image count or skip model inference    |
| "Memory issues"        | Process smaller batches                       |

---

## File Locations

```
ml/
├── monitoring/
│   ├── model_monitor.py (main module)
│   └── MODEL_MONITORING_GUIDE.md (full docs)
│
└── exports/
    ├── monitor_report_TIMESTAMP.json (reports)
    ├── monitor_report_TIMESTAMP.html (HTML reports)
    └── baseline_metrics.json (baseline)
```

---

## Performance

- **100 images**: ~5-10 seconds
- **500 images**: ~30-50 seconds
- **1000 images**: ~1-2 minutes

---

## Key Metrics at a Glance

```
Input Statistics:
  - Pixel mean/std
  - Per-channel (R/G/B) values
  - Min/max/median/percentiles

Model Predictions:
  - Confidence mean/std/distribution
  - Class frequencies
  - Unique classes

Drift Indicators:
  - Pixel shift: > 0.05 = concern
  - Confidence shift: > 0.1 = concern
  - Class drift: Wasserstein > 0.15 = concern
```

---

## Next Steps

1. **Generate baseline**: `python model_monitor.py --mode baseline ...`
2. **Test monitoring**: `python model_monitor.py --mode monitor ...`
3. **Check HTML report**: Open in browser
4. **Schedule daily**: Add to cron/scheduler
5. **Setup alerts**: Check report and notify on drift

---

_Model Monitoring System v1.0 - Production Ready_ ✅
