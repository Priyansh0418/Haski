# Model Monitoring & Drift Detection System

## Overview

The `model_monitor.py` system provides production-ready monitoring and drift detection for machine learning models. It tracks:

- **Input Distribution Statistics** - Mean, std, min, max, percentiles of pixel values
- **Prediction Confidence** - Distribution of model confidence scores
- **Class Predictions** - Distribution of predicted classes
- **Distribution Drift** - Compares current data against baseline metrics
- **Performance Degradation** - Detects model output changes

## Quick Start

### 1. Generate Baseline Metrics (During Training/Validation)

```bash
python ml/monitoring/model_monitor.py \
  --mode baseline \
  --data-dir ml/data/val \
  --model ml/exports/skin_classifier.tflite \
  --output baseline_metrics.json
```

**Output:** `baseline_metrics.json` containing:

```json
{
  "timestamp": "2024-10-24T10:30:00",
  "dataset_info": {
    "image_count": 500,
    "input_size": [224, 224]
  },
  "input_distribution": {
    "pixel_statistics": {
      "overall": {
        "mean": 0.45,
        "std": 0.25,
        ...
      }
    }
  },
  "predictions": {
    "confidence_statistics": {
      "mean": 0.92,
      ...
    }
  }
}
```

### 2. Monitor Production Data for Drift

```bash
python ml/monitoring/model_monitor.py \
  --mode monitor \
  --data-dir ml/data/production \
  --baseline baseline_metrics.json \
  --model ml/exports/skin_classifier.tflite \
  --output report.json \
  --html
```

**Output:**

- `report.json` - Detailed drift metrics
- `report.html` - Beautiful HTML report

### 3. Compare Two Datasets

```bash
python ml/monitoring/model_monitor.py \
  --mode compare \
  --data-dir-1 ml/data/val \
  --data-dir-2 ml/data/production \
  --output comparison.json
```

## Key Features

### ✅ Input Distribution Monitoring

Tracks pixel-level statistics:

- **Per-image**: Mean, std, min, max, median
- **Per-channel**: R, G, B channel analysis
- **Histograms**: Pixel value distributions
- **Comparison**: Against baseline metrics

**Use Case:** Detects camera changes, lighting issues, image quality degradation

### ✅ Prediction Confidence Monitoring

Tracks model confidence:

- **Mean confidence**: Overall model certainty
- **Confidence distribution**: Min/max/median/percentiles
- **Degradation detection**: Drops in average confidence
- **Anomaly detection**: Unusual confidence patterns

**Use Case:** Detects when model becomes uncertain, data distribution changes

### ✅ Class Distribution Monitoring

Tracks prediction patterns:

- **Class frequencies**: Which classes are being predicted
- **Distribution shifts**: Changes in class balance
- **Wasserstein distance**: Statistical distance between distributions

**Use Case:** Detects class imbalance, production preference shifts

### ✅ Drift Detection

Multiple drift metrics:

1. **Pixel-Level Drift**

   - Overall mean/std changes
   - Per-channel shifts
   - Thresholds: mean_shift > 0.05, std_shift > 0.1

2. **Confidence Drift**

   - Mean confidence changes
   - Threshold: shift > 0.1

3. **Class Distribution Drift**
   - Wasserstein distance between distributions
   - Threshold: distance > 0.15

Severity levels: `none` → `low` → `medium` → `high`

### ✅ HTML Reports

Beautiful, interactive HTML reports showing:

- Overall drift status (✓ No Drift / ⚠️ Drift Detected)
- Severity levels with color coding
- Baseline vs current metrics comparison
- Confidence drift analysis
- Responsive design for mobile viewing

## Detailed Usage

### Generate Baseline (One-Time)

```bash
# Analyze validation set as baseline
python ml/monitoring/model_monitor.py \
  --mode baseline \
  --data-dir ml/data/val \
  --model ml/exports/skin_classifier.tflite \
  --output baseline_metrics.json

# Output:
# ✓ 1000 images analyzed
# ✓ Baseline report saved to baseline_metrics.json
```

### Continuous Monitoring

```bash
# Daily monitoring
python ml/monitoring/model_monitor.py \
  --mode monitor \
  --data-dir ml/data/production/daily_batch_2024_10_24 \
  --baseline baseline_metrics.json \
  --model ml/exports/skin_classifier.tflite \
  --output monitor_report_2024_10_24.json \
  --html

# Output:
# ✓ 250 images analyzed
# ✓ Drift report saved to monitor_report_2024_10_24.json
# ✓ HTML report saved to monitor_report_2024_10_24.html
```

### Python API

```python
from ml.monitoring.model_monitor import (
    DatasetAnalyzer,
    DriftDetector,
    generate_html_report
)
import json

# Generate baseline
analyzer = DatasetAnalyzer(
    'ml/data/val',
    model_path='ml/exports/skin_classifier.tflite',
    input_size=(224, 224)
)
baseline = analyzer.analyze()

with open('baseline.json', 'w') as f:
    json.dump(baseline, f)

# Monitor for drift
analyzer_prod = DatasetAnalyzer(
    'ml/data/production',
    model_path='ml/exports/skin_classifier.tflite'
)
drift_report = analyzer_prod.detect_drift(baseline)

print(f"Drift detected: {drift_report['overall_drift_detected']}")
print(f"Pixel drift: {drift_report['pixel_distribution_drift']['drift_detected']}")

# Generate HTML
generate_html_report(drift_report, 'report.html')
```

## Command-Line Reference

### Baseline Mode

Generate baseline metrics from dataset.

```bash
python ml/monitoring/model_monitor.py --mode baseline \
  --data-dir <directory> \
  [--model <path>] \
  [--model-type tflite|onnx] \
  [--output <path>] \
  [--input-size H W]
```

**Options:**

- `--data-dir` (required): Directory containing images
- `--model`: Model path for predictions (optional)
- `--model-type`: Type of model - `tflite` or `onnx` (default: tflite)
- `--output`: Output JSON path (default: monitor_report_TIMESTAMP.json)
- `--input-size`: Input image size (default: 224 224)

**Example:**

```bash
python ml/monitoring/model_monitor.py --mode baseline \
  --data-dir ml/data/val \
  --model ml/exports/skin_classifier.tflite \
  --output baseline.json
```

### Monitor Mode

Detect drift in current data against baseline.

```bash
python ml/monitoring/model_monitor.py --mode monitor \
  --data-dir <directory> \
  --baseline <baseline_json> \
  [--model <path>] \
  [--model-type tflite|onnx] \
  [--output <path>] \
  [--html] \
  [--input-size H W]
```

**Options:**

- `--data-dir` (required): Current data directory
- `--baseline` (required): Baseline metrics JSON file
- `--model`: Model path for predictions (optional)
- `--model-type`: Type of model (default: tflite)
- `--output`: Output JSON path (default: monitor_report_TIMESTAMP.json)
- `--html`: Also generate HTML report
- `--input-size`: Input image size (default: 224 224)

**Example:**

```bash
python ml/monitoring/model_monitor.py --mode monitor \
  --data-dir ml/data/production \
  --baseline baseline_metrics.json \
  --model ml/exports/skin_classifier.tflite \
  --output drift_report.json \
  --html
```

### Compare Mode

Compare two datasets directly.

```bash
python ml/monitoring/model_monitor.py --mode compare \
  --data-dir-1 <directory> \
  --data-dir-2 <directory> \
  [--model <path>] \
  [--model-type tflite|onnx] \
  [--output <path>] \
  [--input-size H W]
```

**Example:**

```bash
python ml/monitoring/model_monitor.py --mode compare \
  --data-dir-1 ml/data/val \
  --data-dir-2 ml/data/production \
  --output comparison.json
```

## JSON Report Format

### Baseline Report

```json
{
  "timestamp": "2024-10-24T10:30:00",
  "dataset_info": {
    "directory": "ml/data/val",
    "image_count": 500,
    "input_size": [224, 224]
  },
  "input_distribution": {
    "image_count": 500,
    "pixel_statistics": {
      "overall": {
        "mean": 0.45,
        "std": 0.25,
        "min": 0.0,
        "max": 1.0,
        "median": 0.44,
        "q25": 0.25,
        "q75": 0.65
      },
      "per_channel": {
        "mean": [0.48, 0.45, 0.42],
        "std": [0.26, 0.25, 0.24],
        "min": [0.0, 0.0, 0.0],
        "max": [1.0, 1.0, 1.0]
      }
    }
  },
  "predictions": {
    "prediction_count": 500,
    "unique_classes": 5,
    "class_distribution": {
      "0": 100,
      "1": 120,
      "2": 150,
      "3": 80,
      "4": 50
    },
    "confidence_statistics": {
      "mean": 0.92,
      "std": 0.08,
      "min": 0.65,
      "max": 0.99,
      "median": 0.94,
      "q25": 0.88,
      "q75": 0.97
    }
  }
}
```

### Drift Report

```json
{
  "timestamp": "2024-10-24T11:00:00",
  "baseline_timestamp": "2024-10-24T10:30:00",
  "baseline_image_count": 500,
  "current_image_count": 250,
  "pixel_distribution_drift": {
    "overall_mean_shift": 0.08,
    "overall_std_shift": 0.12,
    "per_channel_shifts": [0.05, 0.08, 0.12],
    "mean_threshold": 0.05,
    "std_threshold": 0.1,
    "drift_detected": true,
    "severity": "high",
    "baseline_mean": 0.45,
    "current_mean": 0.53,
    "baseline_std": 0.25,
    "current_std": 0.37
  },
  "confidence_drift": {
    "mean_confidence_shift": 0.15,
    "threshold": 0.1,
    "drift_detected": true,
    "severity": "high",
    "baseline_mean_confidence": 0.92,
    "current_mean_confidence": 0.77,
    "baseline_std_confidence": 0.08,
    "current_std_confidence": 0.18
  },
  "class_distribution_drift": {
    "wasserstein_distance": 0.25,
    "threshold": 0.15,
    "drift_detected": true,
    "severity": "medium",
    "class_shift_details": {
      "0": {
        "baseline_prob": 0.2,
        "current_prob": 0.15,
        "shift": 0.05
      }
    }
  },
  "overall_drift_detected": true,
  "drift_summary": {
    "pixel_drift": true,
    "confidence_drift": true,
    "class_distribution_drift": true
  }
}
```

## Drift Thresholds

Default thresholds can be customized in `DriftDetector` class:

```python
PIXEL_MEAN_THRESHOLD = 0.05        # Threshold for mean pixel value shift
PIXEL_STD_THRESHOLD = 0.1          # Threshold for std pixel value shift
CONFIDENCE_THRESHOLD = 0.1         # Threshold for mean confidence shift
CLASS_DIST_THRESHOLD = 0.15        # Threshold for class distribution shift
```

To customize:

```python
from ml.monitoring.model_monitor import DriftDetector

detector = DriftDetector()
detector.PIXEL_MEAN_THRESHOLD = 0.03  # More sensitive
detector.CONFIDENCE_THRESHOLD = 0.05  # More sensitive
```

## Dataset Structure

Supports both flat and hierarchical structures:

```
ml/data/
├── image1.jpg
├── image2.jpg
├── class1/
│   ├── img1.jpg
│   └── img2.jpg
└── class2/
    └── img3.jpg

ml/data/output/
├── images/
│   ├── val/
│   │   ├── img1.jpg
│   │   └── img2.jpg
│   └── test/
└── labels/
```

Supports: `.jpg`, `.jpeg`, `.png`, `.bmp`, `.gif`, `.webp`

## Integration with Backend

### Backend API Integration

```python
from ml.monitoring.model_monitor import DatasetAnalyzer, generate_html_report
import json

# In your FastAPI endpoint
@app.post("/api/v1/monitoring/drift-check")
async def check_model_drift(
    baseline_file: UploadFile,
    data_dir: str
):
    """Check for model drift in production data."""

    # Load baseline
    baseline_content = await baseline_file.read()
    baseline = json.loads(baseline_content)

    # Analyze current data
    analyzer = DatasetAnalyzer(
        data_dir,
        model_path='ml/exports/skin_classifier.tflite'
    )
    drift_report = analyzer.detect_drift(baseline)

    return {
        "drift_detected": drift_report['overall_drift_detected'],
        "drift_summary": drift_report['drift_summary'],
        "severity": {
            "pixel": drift_report['pixel_distribution_drift']['severity'],
            "confidence": drift_report.get('confidence_drift', {}).get('severity', 'N/A')
        }
    }
```

## Performance

### Processing Speed

- **Per-image**: ~50-100 ms (includes I/O, preprocessing, inference)
- **100 images**: ~5-10 seconds
- **1000 images**: ~50-100 seconds

### Memory Usage

- Streaming processing: ~200-500 MB peak
- Scales linearly with image count
- No need to load entire dataset into memory

### Typical Usage

- Baseline generation (500 images): ~30-50 seconds
- Daily monitoring (250 images): ~15-25 seconds
- Weekly reports: 2-3 minutes

## Troubleshooting

### "No images found"

**Solution:** Verify dataset structure and supported formats

```bash
# Check image count
find ml/data -type f \( -iname "*.jpg" -o -iname "*.png" \) | wc -l

# Show first few images
find ml/data -type f -iname "*.jpg" | head -5
```

### "Model loading failed"

**Solution:** Verify model path and type

```bash
# Check model exists
ls -lh ml/exports/skin_classifier.tflite

# Use correct model type
--model-type tflite  # or onnx
```

### "Failed to process image"

**Solution:** Images may be corrupted or in unsupported format

```bash
# Verify images are valid
file ml/data/*.jpg
identify ml/data/*.jpg  # ImageMagick
```

## Production Workflow

### 1. Setup (One-time)

```bash
# Generate baseline from validation set
python ml/monitoring/model_monitor.py \
  --mode baseline \
  --data-dir ml/data/val \
  --model ml/exports/skin_classifier.tflite \
  --output baseline_metrics.json
```

### 2. Daily Monitoring (Automated)

```bash
# Run daily via cron or scheduler
0 2 * * * cd /app && python ml/monitoring/model_monitor.py \
  --mode monitor \
  --data-dir ml/data/production/daily_$(date +\%Y\%m\%d) \
  --baseline baseline_metrics.json \
  --model ml/exports/skin_classifier.tflite \
  --output reports/drift_$(date +\%Y\%m\%d).json \
  --html
```

### 3. Alerting

```python
# Check report and send alerts
import json

with open('drift_report.json', 'r') as f:
    report = json.load(f)

if report['overall_drift_detected']:
    severity = max(
        report['pixel_distribution_drift']['severity'],
        report.get('confidence_drift', {}).get('severity', 'none')
    )

    # Send alert
    send_slack_message(f"⚠️ Model drift detected: {severity}")

    # Optional: Retrain model
    if severity == 'high':
        trigger_retraining()
```

## Advanced Usage

### Custom Drift Thresholds

```python
from ml.monitoring.model_monitor import DriftDetector

detector = DriftDetector()

# More sensitive for critical applications
detector.PIXEL_MEAN_THRESHOLD = 0.02
detector.CONFIDENCE_THRESHOLD = 0.05
detector.CLASS_DIST_THRESHOLD = 0.1
```

### Custom Preprocessing

```python
from ml.monitoring.model_monitor import InputDistributionMonitor

class CustomMonitor(InputDistributionMonitor):
    def compute_statistics(self, image_path):
        # Custom preprocessing
        image = Image.open(image_path)
        # Your custom logic
        super().compute_statistics(image_path)
```

### Export Metrics

```bash
# Export detailed statistics
python ml/monitoring/model_monitor.py \
  --mode baseline \
  --data-dir ml/data/val \
  --output stats.json

# Process with pandas
python -c "
import pandas as pd, json
with open('stats.json') as f: stats = json.load(f)
print(pd.DataFrame([stats['input_distribution']['pixel_statistics']['overall']]))
"
```

## Summary

The Model Monitoring system provides:

✅ **Input distribution tracking** - Pixel-level statistics  
✅ **Prediction monitoring** - Confidence and class distributions  
✅ **Drift detection** - Multiple statistical metrics  
✅ **Beautiful reports** - JSON and HTML outputs  
✅ **Production ready** - Fast, scalable, well-documented  
✅ **Easy integration** - CLI and Python API

**Result:** Continuous monitoring of model performance and input data quality in production!

---

_Model Monitoring System v1.0_  
_Ready for Production Deployment_
