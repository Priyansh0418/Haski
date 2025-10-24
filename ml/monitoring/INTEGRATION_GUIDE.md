# Model Monitoring - Integration Guide

## Integration Overview

The model monitoring system is designed for seamless integration with:

- **Backend APIs** (FastAPI, Django)
- **Monitoring dashboards** (Grafana, custom)
- **Retraining pipelines**
- **Alert systems** (Slack, PagerDuty, email)

---

## Backend API Integration

### FastAPI Example

```python
from fastapi import FastAPI, UploadFile, File, HTTPException
from ml.monitoring import DatasetAnalyzer, generate_html_report
import json
from pathlib import Path

app = FastAPI()

# Store baseline
BASELINE_PATH = "ml/exports/baseline_metrics.json"

@app.post("/api/v1/monitoring/generate-baseline")
async def generate_baseline(data_dir: str):
    """Generate baseline metrics from validation data."""
    try:
        analyzer = DatasetAnalyzer(
            data_dir,
            model_path='ml/exports/skin_classifier.tflite'
        )
        baseline = analyzer.analyze()

        # Save baseline
        with open(BASELINE_PATH, 'w') as f:
            json.dump(baseline, f)

        return {
            "status": "success",
            "image_count": baseline['dataset_info']['image_count'],
            "baseline_path": BASELINE_PATH
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/api/v1/monitoring/check-drift")
async def check_drift(data_dir: str):
    """Check for drift in production data."""
    try:
        # Load baseline
        if not Path(BASELINE_PATH).exists():
            raise HTTPException(status_code=404, detail="Baseline not found")

        with open(BASELINE_PATH, 'r') as f:
            baseline = json.load(f)

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
                "pixel_drift": drift_report['pixel_distribution_drift']['severity'],
                "confidence_drift": drift_report.get('confidence_drift', {}).get('severity', 'N/A'),
                "class_distribution_drift": drift_report.get('class_distribution_drift', {}).get('severity', 'N/A')
            },
            "metrics": {
                "baseline_images": drift_report['baseline_image_count'],
                "current_images": drift_report['current_image_count'],
                "pixel_mean_shift": drift_report['pixel_distribution_drift']['overall_mean_shift']
            }
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.get("/api/v1/monitoring/report/{report_id}")
async def get_report(report_id: str):
    """Retrieve stored monitoring report."""
    report_path = f"ml/exports/monitor_report_{report_id}.json"

    if not Path(report_path).exists():
        raise HTTPException(status_code=404, detail="Report not found")

    with open(report_path, 'r') as f:
        return json.load(f)


@app.get("/api/v1/monitoring/report/{report_id}/html")
async def get_report_html(report_id: str):
    """Get HTML version of report."""
    html_path = f"ml/exports/monitor_report_{report_id}.html"

    if not Path(html_path).exists():
        raise HTTPException(status_code=404, detail="Report not found")

    from fastapi.responses import HTMLResponse
    with open(html_path, 'r') as f:
        return HTMLResponse(content=f.read())
```

### Django Example

```python
from django.http import JsonResponse
from django.views import View
from ml.monitoring import DatasetAnalyzer
import json

class BaselineView(View):
    def post(self, request):
        """Generate baseline metrics."""
        data_dir = request.POST.get('data_dir')

        analyzer = DatasetAnalyzer(
            data_dir,
            model_path='ml/exports/skin_classifier.tflite'
        )
        baseline = analyzer.analyze()

        # Save to database or file
        baseline_path = 'ml/exports/baseline_metrics.json'
        with open(baseline_path, 'w') as f:
            json.dump(baseline, f)

        return JsonResponse({
            'status': 'success',
            'image_count': baseline['dataset_info']['image_count']
        })


class DriftCheckView(View):
    def post(self, request):
        """Check for data drift."""
        data_dir = request.POST.get('data_dir')

        # Load baseline
        with open('ml/exports/baseline_metrics.json', 'r') as f:
            baseline = json.load(f)

        # Analyze
        analyzer = DatasetAnalyzer(
            data_dir,
            model_path='ml/exports/skin_classifier.tflite'
        )
        drift_report = analyzer.detect_drift(baseline)

        return JsonResponse({
            'drift_detected': drift_report['overall_drift_detected'],
            'severity': drift_report['pixel_distribution_drift']['severity']
        })
```

---

## Monitoring Dashboard Integration

### Grafana JSON Model

```json
{
  "dashboard": {
    "title": "Model Monitoring",
    "panels": [
      {
        "title": "Drift Status",
        "targets": [
          {
            "datasource": "API",
            "url": "http://localhost:8000/api/v1/monitoring/latest"
          }
        ]
      },
      {
        "title": "Confidence Trend",
        "targets": [
          {
            "datasource": "TimescaleDB",
            "query": "SELECT time, confidence FROM model_metrics"
          }
        ]
      }
    ]
  }
}
```

### Custom Dashboard Integration

```python
from datetime import datetime, timedelta
import json

def get_monitoring_dashboard():
    """Get current monitoring status for dashboard."""

    # Load latest report
    reports_dir = Path('ml/exports')
    latest_report = max(
        reports_dir.glob('monitor_report_*.json'),
        key=lambda p: p.stat().st_mtime,
        default=None
    )

    if not latest_report:
        return {"status": "no_reports"}

    with open(latest_report, 'r') as f:
        report = json.load(f)

    # Extract key metrics
    return {
        "timestamp": report['timestamp'],
        "drift_detected": report['overall_drift_detected'],
        "severity_level": max(
            report['pixel_distribution_drift']['severity'],
            report.get('confidence_drift', {}).get('severity', 'none')
        ),
        "metrics": {
            "pixel_mean_shift": report['pixel_distribution_drift']['overall_mean_shift'],
            "confidence_shift": report.get('confidence_drift', {}).get('mean_confidence_shift', 0),
            "class_drift_distance": report.get('class_distribution_drift', {}).get('wasserstein_distance', 0)
        },
        "images_analyzed": report['current_image_count']
    }
```

---

## Alert System Integration

### Slack Alerts

```python
from slack_sdk import WebClient
import json

def send_drift_alert(drift_report, webhook_url):
    """Send drift alert to Slack."""

    severity = drift_report['pixel_distribution_drift']['severity']
    color_map = {
        'none': '#36a64f',
        'low': '#ffaa00',
        'medium': '#ff6600',
        'high': '#ff0000'
    }

    client = WebClient(token=webhook_url)

    client.chat_postMessage(
        channel='#ml-monitoring',
        blocks=[
            {
                "type": "header",
                "text": {
                    "type": "plain_text",
                    "text": f"⚠️ Model Drift Alert - {severity.upper()}"
                }
            },
            {
                "type": "section",
                "fields": [
                    {
                        "type": "mrkdwn",
                        "text": f"*Drift Detected:*\n{drift_report['overall_drift_detected']}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Severity:*\n{severity}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Pixel Shift:*\n{drift_report['pixel_distribution_drift']['overall_mean_shift']:.4f}"
                    },
                    {
                        "type": "mrkdwn",
                        "text": f"*Images:*\n{drift_report['current_image_count']}"
                    }
                ]
            }
        ]
    )
```

### Email Alerts

```python
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

def send_email_alert(drift_report, recipients):
    """Send drift alert via email."""

    severity = drift_report['pixel_distribution_drift']['severity']

    msg = MIMEMultipart('alternative')
    msg['Subject'] = f"Model Drift Alert - {severity.upper()}"
    msg['From'] = 'monitoring@example.com'
    msg['To'] = ', '.join(recipients)

    # HTML email
    html = f"""
    <html>
        <body>
            <h2>Model Monitoring Alert</h2>
            <p><strong>Drift Detected:</strong> {drift_report['overall_drift_detected']}</p>
            <p><strong>Severity:</strong> {severity}</p>

            <table border="1">
                <tr>
                    <td>Metric</td>
                    <td>Value</td>
                </tr>
                <tr>
                    <td>Pixel Mean Shift</td>
                    <td>{drift_report['pixel_distribution_drift']['overall_mean_shift']:.4f}</td>
                </tr>
                <tr>
                    <td>Images Analyzed</td>
                    <td>{drift_report['current_image_count']}</td>
                </tr>
            </table>
        </body>
    </html>
    """

    part = MIMEText(html, 'html')
    msg.attach(part)

    # Send
    with smtplib.SMTP('smtp.gmail.com', 587) as server:
        server.starttls()
        server.login('your_email@gmail.com', 'your_password')
        server.send_message(msg)
```

---

## Model Retraining Pipeline Integration

### Trigger Retraining

```python
from ml.monitoring import DatasetAnalyzer
import json
import subprocess

def check_and_trigger_retraining(baseline_path, production_dir, config):
    """Check drift and trigger retraining if needed."""

    # Load baseline
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)

    # Analyze production data
    analyzer = DatasetAnalyzer(
        production_dir,
        model_path=config['model_path']
    )
    drift_report = analyzer.detect_drift(baseline)

    # Check severity
    severity = drift_report['pixel_distribution_drift']['severity']

    if severity == 'high':
        # Trigger high-priority retraining
        trigger_retraining(
            priority='high',
            reason='high_drift',
            drift_report=drift_report,
            config=config
        )
    elif severity == 'medium':
        # Schedule for later
        schedule_retraining(
            priority='normal',
            reason='medium_drift',
            config=config
        )

    return {
        'drift_detected': drift_report['overall_drift_detected'],
        'retraining_triggered': severity in ['high', 'medium']
    }


def trigger_retraining(priority, reason, drift_report, config):
    """Trigger the model retraining pipeline."""

    # Option 1: Execute training script
    subprocess.Popen([
        'python', 'ml/training/train.py',
        '--config', config['training_config'],
        '--priority', priority,
        '--reason', reason
    ])

    # Option 2: Use task queue (Celery)
    from celery import shared_task

    @shared_task
    def retrain_model():
        # Training logic
        pass

    retrain_model.apply_async(
        kwargs={'priority': priority, 'reason': reason},
        priority=10 if priority == 'high' else 5
    )
```

---

## Batch Processing Pipeline

### Scheduled Daily Monitoring

```python
# schedule_monitoring.py
from apscheduler.schedulers.background import BackgroundScheduler
from ml.monitoring import DatasetAnalyzer, generate_html_report
from pathlib import Path
import json
from datetime import datetime

scheduler = BackgroundScheduler()

def daily_monitoring():
    """Run daily monitoring."""

    # Load baseline
    baseline_path = 'ml/exports/baseline_metrics.json'
    with open(baseline_path, 'r') as f:
        baseline = json.load(f)

    # Get today's production data
    today = datetime.now().strftime('%Y%m%d')
    prod_dir = f'ml/data/production/{today}'

    # Analyze
    analyzer = DatasetAnalyzer(
        prod_dir,
        model_path='ml/exports/skin_classifier.tflite'
    )
    drift_report = analyzer.detect_drift(baseline)

    # Save reports
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    json_path = f'ml/exports/monitor_report_{timestamp}.json'
    html_path = f'ml/exports/monitor_report_{timestamp}.html'

    with open(json_path, 'w') as f:
        json.dump(drift_report, f)

    generate_html_report(drift_report, html_path)

    # Send alerts if drift
    if drift_report['overall_drift_detected']:
        send_slack_alert(drift_report)

# Schedule for 2 AM daily
scheduler.add_job(
    daily_monitoring,
    'cron',
    hour=2,
    minute=0,
    id='daily_monitoring'
)

scheduler.start()
```

---

## Database Integration

### Store Metrics in TimescaleDB

```python
import psycopg2
from datetime import datetime

def store_monitoring_report(drift_report):
    """Store monitoring report in TimescaleDB."""

    conn = psycopg2.connect(
        "dbname=monitoring user=postgres password=secret"
    )
    cur = conn.cursor()

    # Insert metrics
    cur.execute("""
        INSERT INTO monitoring_metrics (timestamp, metric_name, value)
        VALUES
            (%s, 'pixel_mean_shift', %s),
            (%s, 'confidence_shift', %s),
            (%s, 'drift_detected', %s)
    """, [
        datetime.now(),
        drift_report['pixel_distribution_drift']['overall_mean_shift'],
        datetime.now(),
        drift_report.get('confidence_drift', {}).get('mean_confidence_shift', 0),
        datetime.now(),
        drift_report['overall_drift_detected']
    ])

    conn.commit()
    cur.close()
    conn.close()
```

---

## Summary

The monitoring system integrates with:

✅ **Backend APIs** - FastAPI, Django endpoints  
✅ **Dashboards** - Grafana, custom dashboards  
✅ **Alerts** - Slack, email, PagerDuty  
✅ **Retraining** - Trigger pipelines on drift  
✅ **Batch jobs** - Scheduled monitoring via cron  
✅ **Databases** - Store metrics for analysis

Use these examples as templates for your specific setup!

---

_Ready for production integration_ ✅
