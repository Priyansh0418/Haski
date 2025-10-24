"""
Model Monitoring and Drift Detection System

Monitors production model performance and input distribution drift:
- Computes input statistics (mean/std of pixel values)
- Tracks class prediction distribution
- Compares against baseline metrics from training
- Generates JSON and HTML drift reports
- Detects data distribution shift and model performance degradation

Usage:
    # Generate baseline metrics during training
    python model_monitor.py --mode baseline --data-dir ml/data/train --output baseline_metrics.json
    
    # Monitor production data for drift
    python model_monitor.py --mode monitor --data-dir ml/data/production \
        --baseline baseline_metrics.json --output report.json
    
    # Generate HTML report
    python model_monitor.py --mode monitor --data-dir ml/data/production \
        --baseline baseline_metrics.json --html
    
    # Compare two datasets
    python model_monitor.py --mode compare \
        --data-dir-1 ml/data/val \
        --data-dir-2 ml/data/production \
        --output comparison.json
"""

import argparse
import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import tempfile
import os

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Import inference utilities
try:
    from sys import path
    ml_exports_path = Path(__file__).parent.parent / "exports"
    if str(ml_exports_path) not in path:
        path.insert(0, str(ml_exports_path))
    from ml_infer import TFLiteInference, ONNXInference, preprocess_image
except ImportError:
    logger.warning("Could not import inference utilities, will use mock inference")
    TFLiteInference = None
    ONNXInference = None


class InputDistributionMonitor:
    """Monitor input data distribution statistics."""
    
    def __init__(self, input_size: Tuple[int, int] = (224, 224)):
        """
        Initialize monitor.
        
        Args:
            input_size: Expected input image size (H, W)
        """
        self.input_size = input_size
        self.pixel_values = []
        self.image_count = 0
        
    def compute_statistics(self, image_path: str) -> None:
        """
        Compute and accumulate pixel statistics from image.
        
        Args:
            image_path: Path to image file
        """
        try:
            image = Image.open(image_path).convert('RGB')
            image = image.resize(self.input_size)
            image_array = np.array(image, dtype=np.float32) / 255.0
            
            # Store for aggregation
            self.pixel_values.append(image_array.flatten())
            self.image_count += 1
            
        except Exception as e:
            logger.warning(f"Failed to process {image_path}: {e}")
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregated pixel distribution statistics.
        
        Returns:
            Dictionary with mean, std, min, max, median per channel and overall
        """
        if not self.pixel_values:
            return {
                'image_count': 0,
                'error': 'No images processed'
            }
        
        all_pixels = np.concatenate(self.pixel_values)
        
        # Reshape to compute per-channel stats
        # All images are 224x224 RGB = 224*224*3 pixels
        pixels_per_image = 224 * 224 * 3
        all_pixels_2d = all_pixels.reshape(-1, pixels_per_image)
        
        # Per-channel statistics (approximate by dividing into R, G, B)
        pixels_reshaped = all_pixels.reshape(-1, 3)  # N x 3 channels
        
        return {
            'image_count': self.image_count,
            'pixel_statistics': {
                'overall': {
                    'mean': float(np.mean(all_pixels)),
                    'std': float(np.std(all_pixels)),
                    'min': float(np.min(all_pixels)),
                    'max': float(np.max(all_pixels)),
                    'median': float(np.median(all_pixels)),
                    'q25': float(np.percentile(all_pixels, 25)),
                    'q75': float(np.percentile(all_pixels, 75)),
                },
                'per_channel': {
                    'mean': [float(np.mean(pixels_reshaped[:, i])) for i in range(3)],
                    'std': [float(np.std(pixels_reshaped[:, i])) for i in range(3)],
                    'min': [float(np.min(pixels_reshaped[:, i])) for i in range(3)],
                    'max': [float(np.max(pixels_reshaped[:, i])) for i in range(3)],
                }
            },
            'histograms': {
                'overall': {
                    'bins': 20,
                    'values': np.histogram(all_pixels, bins=20)[0].tolist(),
                    'edges': np.histogram(all_pixels, bins=20)[1].tolist(),
                }
            }
        }


class ModelPredictionMonitor:
    """Monitor model predictions and confidence distributions."""
    
    def __init__(self, model_path: Optional[str] = None, model_type: str = 'tflite'):
        """
        Initialize prediction monitor.
        
        Args:
            model_path: Path to model file
            model_type: Type of model ('tflite', 'onnx')
        """
        self.model_path = model_path
        self.model_type = model_type
        self.model = None
        self.predictions = []
        self.confidences = []
        self.per_class_counts = {}
        
        if model_path and Path(model_path).exists():
            try:
                self._load_model()
            except Exception as e:
                logger.warning(f"Could not load model: {e}")
    
    def _load_model(self) -> None:
        """Load model for inference."""
        if self.model_type == 'tflite' and TFLiteInference:
            self.model = TFLiteInference(self.model_path)
        elif self.model_type == 'onnx' and ONNXInference:
            self.model = ONNXInference(self.model_path)
    
    def predict_image(self, image_path: str) -> Optional[Dict[str, Any]]:
        """
        Run prediction on image.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Dictionary with prediction results or None if model unavailable
        """
        if not self.model:
            return None
        
        try:
            result = self.model.predict(image_path)
            
            # Track metrics
            predicted_class = result['predicted_class']
            confidence = result['confidence']
            
            self.predictions.append(predicted_class)
            self.confidences.append(confidence)
            
            if predicted_class not in self.per_class_counts:
                self.per_class_counts[predicted_class] = 0
            self.per_class_counts[predicted_class] += 1
            
            return result
            
        except Exception as e:
            logger.warning(f"Prediction failed for {image_path}: {e}")
            return None
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get aggregated prediction statistics.
        
        Returns:
            Dictionary with class distribution and confidence metrics
        """
        if not self.predictions:
            return {
                'prediction_count': 0,
                'error': 'No predictions made'
            }
        
        confidences = np.array(self.confidences)
        
        return {
            'prediction_count': len(self.predictions),
            'unique_classes': len(set(self.predictions)),
            'class_distribution': {
                int(k): int(v) for k, v in self.per_class_counts.items()
            },
            'confidence_statistics': {
                'mean': float(np.mean(confidences)),
                'std': float(np.std(confidences)),
                'min': float(np.min(confidences)),
                'max': float(np.max(confidences)),
                'median': float(np.median(confidences)),
                'q25': float(np.percentile(confidences, 25)),
                'q75': float(np.percentile(confidences, 75)),
            }
        }


class DriftDetector:
    """Detect distribution drift between datasets."""
    
    # Thresholds for drift detection
    PIXEL_MEAN_THRESHOLD = 0.05  # Threshold for mean pixel value shift
    PIXEL_STD_THRESHOLD = 0.1    # Threshold for std pixel value shift
    CONFIDENCE_THRESHOLD = 0.1   # Threshold for mean confidence shift
    CLASS_DIST_THRESHOLD = 0.15  # Threshold for class distribution shift (Wasserstein)
    
    def __init__(self):
        """Initialize drift detector."""
        self.drifts_detected = []
    
    def compute_pixel_drift(
        self,
        baseline_stats: Dict[str, Any],
        current_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute pixel-level distribution drift.
        
        Args:
            baseline_stats: Baseline input statistics
            current_stats: Current input statistics
        
        Returns:
            Drift metrics and detection results
        """
        if 'error' in baseline_stats or 'error' in current_stats:
            return {'error': 'Missing statistics'}
        
        baseline_pixel_stats = baseline_stats['pixel_statistics']['overall']
        current_pixel_stats = current_stats['pixel_statistics']['overall']
        
        # Compute differences
        mean_diff = abs(
            baseline_pixel_stats['mean'] - current_pixel_stats['mean']
        )
        std_diff = abs(
            baseline_pixel_stats['std'] - current_pixel_stats['std']
        )
        
        # Per-channel analysis
        baseline_means = np.array(baseline_stats['pixel_statistics']['per_channel']['mean'])
        current_means = np.array(current_stats['pixel_statistics']['per_channel']['mean'])
        per_channel_diffs = np.abs(baseline_means - current_means)
        
        # Detect drift
        pixel_drift_detected = (
            mean_diff > self.PIXEL_MEAN_THRESHOLD or
            std_diff > self.PIXEL_STD_THRESHOLD or
            np.any(per_channel_diffs > self.PIXEL_MEAN_THRESHOLD)
        )
        
        return {
            'overall_mean_shift': float(mean_diff),
            'overall_std_shift': float(std_diff),
            'per_channel_shifts': per_channel_diffs.tolist(),
            'mean_threshold': self.PIXEL_MEAN_THRESHOLD,
            'std_threshold': self.PIXEL_STD_THRESHOLD,
            'drift_detected': bool(pixel_drift_detected),
            'severity': self._classify_drift_severity(mean_diff + std_diff),
            'baseline_mean': float(baseline_pixel_stats['mean']),
            'current_mean': float(current_pixel_stats['mean']),
            'baseline_std': float(baseline_pixel_stats['std']),
            'current_std': float(current_pixel_stats['std']),
        }
    
    def compute_confidence_drift(
        self,
        baseline_stats: Dict[str, Any],
        current_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute prediction confidence drift.
        
        Args:
            baseline_stats: Baseline prediction statistics
            current_stats: Current prediction statistics
        
        Returns:
            Drift metrics and detection results
        """
        if 'error' in baseline_stats or 'error' in current_stats:
            return {'error': 'Missing statistics'}
        
        baseline_conf = baseline_stats['confidence_statistics']
        current_conf = current_stats['confidence_statistics']
        
        # Compute differences
        mean_conf_diff = abs(baseline_conf['mean'] - current_conf['mean'])
        
        # Detect drift
        confidence_drift_detected = mean_conf_diff > self.CONFIDENCE_THRESHOLD
        
        return {
            'mean_confidence_shift': float(mean_conf_diff),
            'threshold': self.CONFIDENCE_THRESHOLD,
            'drift_detected': bool(confidence_drift_detected),
            'severity': self._classify_drift_severity(mean_conf_diff),
            'baseline_mean_confidence': float(baseline_conf['mean']),
            'current_mean_confidence': float(current_conf['mean']),
            'baseline_std_confidence': float(baseline_conf['std']),
            'current_std_confidence': float(current_conf['std']),
        }
    
    def compute_class_distribution_drift(
        self,
        baseline_stats: Dict[str, Any],
        current_stats: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Compute class prediction distribution drift (Wasserstein distance).
        
        Args:
            baseline_stats: Baseline prediction statistics
            current_stats: Current prediction statistics
        
        Returns:
            Drift metrics and detection results
        """
        if 'error' in baseline_stats or 'error' in current_stats:
            return {'error': 'Missing statistics'}
        
        baseline_dist = baseline_stats['class_distribution']
        current_dist = current_stats['class_distribution']
        
        # Get all class IDs
        all_classes = set(baseline_dist.keys()) | set(current_dist.keys())
        all_classes = sorted(list(all_classes))
        
        # Normalize to probabilities
        baseline_counts = np.array([baseline_dist.get(c, 0) for c in all_classes])
        current_counts = np.array([current_dist.get(c, 0) for c in all_classes])
        
        baseline_probs = baseline_counts / (np.sum(baseline_counts) + 1e-8)
        current_probs = current_counts / (np.sum(current_counts) + 1e-8)
        
        # Compute Wasserstein distance (L1 norm of sorted differences)
        wasserstein_dist = np.sum(np.abs(baseline_probs - current_probs)) / 2.0
        
        # Detect drift
        dist_drift_detected = wasserstein_dist > self.CLASS_DIST_THRESHOLD
        
        return {
            'wasserstein_distance': float(wasserstein_dist),
            'threshold': self.CLASS_DIST_THRESHOLD,
            'drift_detected': bool(dist_drift_detected),
            'severity': self._classify_drift_severity(wasserstein_dist * 10),  # Scale for severity
            'class_shift_details': {
                int(c): {
                    'baseline_prob': float(baseline_probs[i]),
                    'current_prob': float(current_probs[i]),
                    'shift': float(abs(baseline_probs[i] - current_probs[i]))
                }
                for i, c in enumerate(all_classes)
            }
        }
    
    @staticmethod
    def _classify_drift_severity(metric_value: float) -> str:
        """
        Classify drift severity.
        
        Args:
            metric_value: Computed drift metric
        
        Returns:
            Severity level: 'none', 'low', 'medium', 'high'
        """
        if metric_value < 0.02:
            return 'none'
        elif metric_value < 0.05:
            return 'low'
        elif metric_value < 0.1:
            return 'medium'
        else:
            return 'high'


class DatasetAnalyzer:
    """Analyze dataset and generate baseline or monitoring reports."""
    
    def __init__(
        self,
        data_dir: str,
        model_path: Optional[str] = None,
        model_type: str = 'tflite',
        input_size: Tuple[int, int] = (224, 224)
    ):
        """
        Initialize analyzer.
        
        Args:
            data_dir: Directory containing images
            model_path: Path to model for predictions
            model_type: Type of model
            input_size: Input image size
        """
        self.data_dir = Path(data_dir)
        self.input_size = input_size
        
        self.input_monitor = InputDistributionMonitor(input_size)
        self.prediction_monitor = ModelPredictionMonitor(model_path, model_type)
        self.drift_detector = DriftDetector()
        
        # Find all images
        self.image_paths = self._find_images()
        logger.info(f"Found {len(self.image_paths)} images in {data_dir}")
    
    def _find_images(self) -> List[Path]:
        """Find all image files in directory recursively."""
        image_extensions = {'.jpg', '.jpeg', '.png', '.bmp', '.gif', '.webp'}
        images = []
        
        for ext in image_extensions:
            images.extend(self.data_dir.rglob(f'*{ext}'))
            images.extend(self.data_dir.rglob(f'*{ext.upper()}'))
        
        return sorted(list(set(images)))
    
    def analyze(self, show_progress: bool = True) -> Dict[str, Any]:
        """
        Analyze dataset.
        
        Args:
            show_progress: Whether to show progress
        
        Returns:
            Dictionary with analysis results
        """
        logger.info(f"Analyzing {len(self.image_paths)} images...")
        
        for i, image_path in enumerate(self.image_paths):
            if show_progress and (i + 1) % max(1, len(self.image_paths) // 10) == 0:
                logger.info(f"  Progress: {i + 1}/{len(self.image_paths)}")
            
            # Compute input statistics
            self.input_monitor.compute_statistics(str(image_path))
            
            # Make prediction if model available
            if self.prediction_monitor.model:
                self.prediction_monitor.predict_image(str(image_path))
        
        logger.info("Analysis complete")
        
        # Compile results
        results = {
            'timestamp': datetime.now().isoformat(),
            'dataset_info': {
                'directory': str(self.data_dir),
                'image_count': len(self.image_paths),
                'input_size': self.input_size,
            },
            'input_distribution': self.input_monitor.get_statistics(),
            'predictions': self.prediction_monitor.get_statistics(),
        }
        
        return results
    
    def detect_drift(self, baseline_report: Dict[str, Any]) -> Dict[str, Any]:
        """
        Detect drift against baseline.
        
        Args:
            baseline_report: Baseline analysis report
        
        Returns:
            Drift detection results
        """
        current_report = self.analyze()
        
        drift_results = {
            'timestamp': datetime.now().isoformat(),
            'baseline_timestamp': baseline_report.get('timestamp'),
            'baseline_image_count': baseline_report['dataset_info']['image_count'],
            'current_image_count': current_report['dataset_info']['image_count'],
        }
        
        # Analyze pixel distribution drift
        pixel_drift = self.drift_detector.compute_pixel_drift(
            baseline_report['input_distribution'],
            current_report['input_distribution']
        )
        drift_results['pixel_distribution_drift'] = pixel_drift
        
        # Analyze prediction confidence drift
        if self.prediction_monitor.model:
            confidence_drift = self.drift_detector.compute_confidence_drift(
                baseline_report['predictions'],
                current_report['predictions']
            )
            drift_results['confidence_drift'] = confidence_drift
            
            # Analyze class distribution drift
            class_dist_drift = self.drift_detector.compute_class_distribution_drift(
                baseline_report['predictions'],
                current_report['predictions']
            )
            drift_results['class_distribution_drift'] = class_dist_drift
        
        # Overall drift assessment
        all_drifts = [
            pixel_drift.get('drift_detected', False),
            drift_results.get('confidence_drift', {}).get('drift_detected', False),
            drift_results.get('class_distribution_drift', {}).get('drift_detected', False),
        ]
        
        drift_results['overall_drift_detected'] = any(all_drifts)
        drift_results['drift_summary'] = {
            'pixel_drift': pixel_drift.get('drift_detected', False),
            'confidence_drift': drift_results.get('confidence_drift', {}).get('drift_detected', False),
            'class_distribution_drift': drift_results.get('class_distribution_drift', {}).get('drift_detected', False),
        }
        
        return drift_results


def generate_html_report(drift_report: Dict[str, Any], output_path: str) -> str:
    """
    Generate HTML report from drift detection results.
    
    Args:
        drift_report: Drift detection results
        output_path: Path to save HTML report
    
    Returns:
        Path to generated HTML file
    """
    html_content = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Model Monitoring Report</title>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            
            body {{
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: #333;
                line-height: 1.6;
                padding: 20px;
            }}
            
            .container {{
                max-width: 1200px;
                margin: 0 auto;
                background: white;
                border-radius: 8px;
                box-shadow: 0 10px 40px rgba(0, 0, 0, 0.2);
                overflow: hidden;
            }}
            
            .header {{
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 40px;
                text-align: center;
            }}
            
            .header h1 {{
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            
            .header p {{
                font-size: 1.1em;
                opacity: 0.9;
            }}
            
            .content {{
                padding: 40px;
            }}
            
            .section {{
                margin-bottom: 40px;
                border: 1px solid #e0e0e0;
                border-radius: 6px;
                padding: 20px;
                background: #f9f9f9;
            }}
            
            .section h2 {{
                color: #667eea;
                margin-bottom: 20px;
                padding-bottom: 10px;
                border-bottom: 2px solid #667eea;
            }}
            
            .metric {{
                display: grid;
                grid-template-columns: 1fr 1fr;
                gap: 20px;
                margin-bottom: 15px;
            }}
            
            .metric-item {{
                background: white;
                padding: 15px;
                border-radius: 4px;
                border-left: 4px solid #667eea;
            }}
            
            .metric-label {{
                font-weight: 600;
                color: #555;
                margin-bottom: 5px;
            }}
            
            .metric-value {{
                font-size: 1.3em;
                color: #667eea;
                font-weight: bold;
            }}
            
            .alert {{
                padding: 15px;
                border-radius: 4px;
                margin-bottom: 15px;
                border-left: 4px solid;
            }}
            
            .alert-info {{
                background: #d1ecf1;
                border-left-color: #0c5460;
                color: #0c5460;
            }}
            
            .alert-warning {{
                background: #fff3cd;
                border-left-color: #856404;
                color: #856404;
            }}
            
            .alert-danger {{
                background: #f8d7da;
                border-left-color: #721c24;
                color: #721c24;
            }}
            
            .alert-success {{
                background: #d4edda;
                border-left-color: #155724;
                color: #155724;
            }}
            
            .status-badge {{
                display: inline-block;
                padding: 6px 12px;
                border-radius: 20px;
                font-weight: 600;
                font-size: 0.9em;
            }}
            
            .status-ok {{
                background: #d4edda;
                color: #155724;
            }}
            
            .status-warning {{
                background: #fff3cd;
                color: #856404;
            }}
            
            .status-alert {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            
            th, td {{
                padding: 12px;
                text-align: left;
                border-bottom: 1px solid #ddd;
            }}
            
            th {{
                background: #f0f0f0;
                font-weight: 600;
                color: #333;
            }}
            
            tr:hover {{
                background: #f9f9f9;
            }}
            
            .footer {{
                background: #f0f0f0;
                padding: 20px;
                text-align: center;
                color: #666;
                border-top: 1px solid #ddd;
            }}
            
            .drift-badge {{
                display: inline-block;
                padding: 8px 16px;
                border-radius: 4px;
                font-weight: 600;
            }}
            
            .drift-detected {{
                background: #f8d7da;
                color: #721c24;
            }}
            
            .no-drift {{
                background: #d4edda;
                color: #155724;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>🔍 Model Monitoring Report</h1>
                <p>Distribution Drift Detection & Input Analysis</p>
            </div>
            
            <div class="content">
                <!-- Overall Status -->
                <div class="section">
                    <h2>Overall Status</h2>
    """
    
    # Add drift status
    if drift_report.get('overall_drift_detected'):
        html_content += f"""
                    <div class="alert alert-warning">
                        <strong>⚠️ Drift Detected!</strong> Model monitoring detected distribution changes.
                    </div>
                    <div class="drift-badge drift-detected">DRIFT DETECTED</div>
        """
    else:
        html_content += f"""
                    <div class="alert alert-success">
                        <strong>✓ No Drift Detected</strong> Input distribution remains stable.
                    </div>
                    <div class="drift-badge no-drift">NO DRIFT</div>
        """
    
    # Add dataset info
    html_content += f"""
                    <div class="metric">
                        <div class="metric-item">
                            <div class="metric-label">Baseline Images</div>
                            <div class="metric-value">{drift_report.get('baseline_image_count', 'N/A')}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Current Images</div>
                            <div class="metric-value">{drift_report.get('current_image_count', 'N/A')}</div>
                        </div>
                    </div>
                </div>
                
                <!-- Pixel Distribution Drift -->
                <div class="section">
                    <h2>Pixel Distribution Drift</h2>
    """
    
    pixel_drift = drift_report.get('pixel_distribution_drift', {})
    if 'error' not in pixel_drift:
        severity = pixel_drift.get('severity', 'unknown')
        alert_class = 'alert-success' if severity == 'none' else 'alert-warning' if severity in ['low', 'medium'] else 'alert-danger'
        html_content += f"""
                    <div class="alert {alert_class}">
                        Severity: <strong>{severity.upper()}</strong>
                    </div>
                    <div class="metric">
                        <div class="metric-item">
                            <div class="metric-label">Overall Mean Shift</div>
                            <div class="metric-value">{pixel_drift.get('overall_mean_shift', 0):.4f}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Threshold</div>
                            <div class="metric-value">{pixel_drift.get('mean_threshold', 0):.4f}</div>
                        </div>
                    </div>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Baseline</th>
                            <th>Current</th>
                            <th>Shift</th>
                        </tr>
                        <tr>
                            <td>Mean</td>
                            <td>{pixel_drift.get('baseline_mean', 0):.4f}</td>
                            <td>{pixel_drift.get('current_mean', 0):.4f}</td>
                            <td>{pixel_drift.get('overall_mean_shift', 0):.4f}</td>
                        </tr>
                        <tr>
                            <td>Std Dev</td>
                            <td>{pixel_drift.get('baseline_std', 0):.4f}</td>
                            <td>{pixel_drift.get('current_std', 0):.4f}</td>
                            <td>{pixel_drift.get('overall_std_shift', 0):.4f}</td>
                        </tr>
                    </table>
        """
    
    html_content += """
                </div>
                
                <!-- Confidence Drift -->
                <div class="section">
                    <h2>Prediction Confidence Drift</h2>
    """
    
    confidence_drift = drift_report.get('confidence_drift', {})
    if 'error' not in confidence_drift and confidence_drift:
        severity = confidence_drift.get('severity', 'unknown')
        alert_class = 'alert-success' if severity == 'none' else 'alert-warning' if severity in ['low', 'medium'] else 'alert-danger'
        html_content += f"""
                    <div class="alert {alert_class}">
                        Severity: <strong>{severity.upper()}</strong>
                    </div>
                    <div class="metric">
                        <div class="metric-item">
                            <div class="metric-label">Mean Confidence Shift</div>
                            <div class="metric-value">{confidence_drift.get('mean_confidence_shift', 0):.4f}</div>
                        </div>
                        <div class="metric-item">
                            <div class="metric-label">Threshold</div>
                            <div class="metric-value">{confidence_drift.get('threshold', 0):.4f}</div>
                        </div>
                    </div>
                    <table>
                        <tr>
                            <th>Metric</th>
                            <th>Baseline</th>
                            <th>Current</th>
                        </tr>
                        <tr>
                            <td>Mean Confidence</td>
                            <td>{confidence_drift.get('baseline_mean_confidence', 0):.4f}</td>
                            <td>{confidence_drift.get('current_mean_confidence', 0):.4f}</td>
                        </tr>
                        <tr>
                            <td>Std Dev</td>
                            <td>{confidence_drift.get('baseline_std_confidence', 0):.4f}</td>
                            <td>{confidence_drift.get('current_std_confidence', 0):.4f}</td>
                        </tr>
                    </table>
        """
    else:
        html_content += '<div class="alert alert-info">Model predictions not available</div>'
    
    html_content += """
                </div>
                
                <!-- Timestamp -->
                <div class="section">
                    <h2>Report Information</h2>
    """
    
    html_content += f"""
                    <div class="metric-item">
                        <div class="metric-label">Report Generated</div>
                        <div class="metric-value">{drift_report.get('timestamp', 'N/A')}</div>
                    </div>
                </div>
            </div>
            
            <div class="footer">
                <p>Model Monitoring System v1.0 | Generated on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    # Write HTML file
    with open(output_path, 'w') as f:
        f.write(html_content)
    
    return output_path


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description='Model monitoring and drift detection'
    )
    
    parser.add_argument(
        '--mode',
        type=str,
        choices=['baseline', 'monitor', 'compare'],
        default='baseline',
        help='Mode: baseline (generate), monitor (detect drift), or compare (two datasets)'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        help='Directory with images to analyze'
    )
    
    parser.add_argument(
        '--data-dir-1',
        type=str,
        help='First dataset directory (for compare mode)'
    )
    
    parser.add_argument(
        '--data-dir-2',
        type=str,
        help='Second dataset directory (for compare mode)'
    )
    
    parser.add_argument(
        '--baseline',
        type=str,
        help='Path to baseline metrics JSON (for monitor mode)'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        help='Path to model for predictions'
    )
    
    parser.add_argument(
        '--model-type',
        type=str,
        choices=['tflite', 'onnx'],
        default='tflite',
        help='Type of model'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        help='Output file path for JSON report'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='Also generate HTML report'
    )
    
    parser.add_argument(
        '--input-size',
        type=int,
        nargs=2,
        default=[224, 224],
        help='Input image size (H W)'
    )
    
    args = parser.parse_args()
    
    # Determine output path
    if args.output is None:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        args.output = f'ml/exports/monitor_report_{timestamp}.json'
    
    Path(args.output).parent.mkdir(parents=True, exist_ok=True)
    
    # Run requested mode
    if args.mode == 'baseline':
        if not args.data_dir:
            logger.error("--data-dir required for baseline mode")
            return
        
        logger.info("Generating baseline metrics...")
        analyzer = DatasetAnalyzer(
            args.data_dir,
            model_path=args.model,
            model_type=args.model_type,
            input_size=tuple(args.input_size)
        )
        report = analyzer.analyze()
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(report, f, indent=2)
        logger.info(f"✓ Baseline report saved to {args.output}")
    
    elif args.mode == 'monitor':
        if not args.data_dir or not args.baseline:
            logger.error("--data-dir and --baseline required for monitor mode")
            return
        
        # Load baseline
        with open(args.baseline, 'r') as f:
            baseline_report = json.load(f)
        logger.info(f"Loaded baseline from {args.baseline}")
        
        logger.info("Analyzing current data for drift...")
        analyzer = DatasetAnalyzer(
            args.data_dir,
            model_path=args.model,
            model_type=args.model_type,
            input_size=tuple(args.input_size)
        )
        
        drift_report = analyzer.detect_drift(baseline_report)
        
        # Save report
        with open(args.output, 'w') as f:
            json.dump(drift_report, f, indent=2)
        logger.info(f"✓ Drift report saved to {args.output}")
        
        # Generate HTML if requested
        if args.html:
            html_output = args.output.replace('.json', '.html')
            generate_html_report(drift_report, html_output)
            logger.info(f"✓ HTML report saved to {html_output}")
    
    elif args.mode == 'compare':
        if not args.data_dir_1 or not args.data_dir_2:
            logger.error("--data-dir-1 and --data-dir-2 required for compare mode")
            return
        
        logger.info(f"Analyzing dataset 1: {args.data_dir_1}")
        analyzer1 = DatasetAnalyzer(
            args.data_dir_1,
            model_path=args.model,
            model_type=args.model_type,
            input_size=tuple(args.input_size)
        )
        report1 = analyzer1.analyze()
        
        logger.info(f"Analyzing dataset 2: {args.data_dir_2}")
        analyzer2 = DatasetAnalyzer(
            args.data_dir_2,
            model_path=args.model,
            model_type=args.model_type,
            input_size=tuple(args.input_size)
        )
        report2 = analyzer2.analyze()
        
        # Create comparison by detecting drift between them
        drift_detector = DriftDetector()
        comparison = {
            'timestamp': datetime.now().isoformat(),
            'dataset_1': report1['dataset_info']['directory'],
            'dataset_2': report2['dataset_info']['directory'],
            'pixel_distribution_drift': drift_detector.compute_pixel_drift(
                report1['input_distribution'],
                report2['input_distribution']
            ),
        }
        
        if 'confidence_statistics' in report1.get('predictions', {}) and \
           'confidence_statistics' in report2.get('predictions', {}):
            comparison['confidence_drift'] = drift_detector.compute_confidence_drift(
                report1['predictions'],
                report2['predictions']
            )
        
        # Save comparison
        with open(args.output, 'w') as f:
            json.dump(comparison, f, indent=2)
        logger.info(f"✓ Comparison saved to {args.output}")


if __name__ == '__main__':
    main()
