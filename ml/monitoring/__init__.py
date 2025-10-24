"""
ML Monitoring Package

Model monitoring and drift detection system for production models.

Usage:
    from ml.monitoring import DatasetAnalyzer, DriftDetector
    
    analyzer = DatasetAnalyzer('ml/data/val', model_path='model.tflite')
    baseline = analyzer.analyze()
    
    drift_report = analyzer.detect_drift(baseline)
    if drift_report['overall_drift_detected']:
        print("Drift detected!")
"""

from .model_monitor import (
    InputDistributionMonitor,
    ModelPredictionMonitor,
    DriftDetector,
    DatasetAnalyzer,
    generate_html_report
)

__all__ = [
    'InputDistributionMonitor',
    'ModelPredictionMonitor',
    'DriftDetector',
    'DatasetAnalyzer',
    'generate_html_report',
]

__version__ = '1.0.0'
