"""
Detector Inference Module - Skin Condition Detection

Provides inference interface for YOLOv8 object detection models with fallback support.

Features:
- YOLOv8 detector loading and inference
- OpenCV DNN fallback for environments without Ultralytics
- Flexible bbox coordinate formats
- Per-class detection counts and summaries
- Confidence-based filtering

Usage:
    from detector_infer import ConditionDetector
    
    detector = ConditionDetector(model_path='path/to/best.pt')
    results = detector.detect(image_path='photo.jpg', conf_thresh=0.3)
    
    # Results include:
    # {
    #     'detections': [...],
    #     'summary': {'acne': 2, 'eczema': 1, ...},
    #     'model_type': 'yolov8' or 'opencv',
    #     'total_detections': 3
    # }
"""

import os
import sys
import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from dataclasses import dataclass
from collections import defaultdict

import numpy as np
import cv2
from PIL import Image

# Try to import Ultralytics
try:
    from ultralytics import YOLO
    ULTRALYTICS_AVAILABLE = True
except ImportError:
    ULTRALYTICS_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


@dataclass
class Detection:
    """Single detection result."""
    class_id: int
    class_name: str
    confidence: float
    bbox_xyxy: Tuple[float, float, float, float]  # pixel coordinates
    bbox_norm: Tuple[float, float, float, float]  # normalized (0-1)
    area: float  # relative area (0-1)
    
    def to_dict(self) -> Dict:
        """Convert to dictionary."""
        return {
            'class_id': self.class_id,
            'class_name': self.class_name,
            'confidence': float(self.confidence),
            'bbox_xyxy': [float(x) for x in self.bbox_xyxy],  # pixels
            'bbox_norm': [float(x) for x in self.bbox_norm],  # normalized
            'bbox_xywh': [
                float(self.bbox_norm[0]),
                float(self.bbox_norm[1]),
                float(self.bbox_norm[2] - self.bbox_norm[0]),
                float(self.bbox_norm[3] - self.bbox_norm[1]),
            ],  # normalized center format
            'area': float(self.area),
        }


class ConditionDetector:
    """
    Skin condition detector using YOLOv8 with OpenCV fallback.
    
    Supports loading YOLOv8 models and running inference with confidence filtering.
    Falls back to OpenCV DNN if Ultralytics is not available.
    """
    
    def __init__(
        self,
        model_path: Optional[str] = None,
        class_names: Optional[List[str]] = None,
        device: str = 'cpu',
        conf_thresh: float = 0.3,
    ):
        """
        Initialize detector.
        
        Args:
            model_path: Path to YOLOv8 weights (.pt) or OpenCV model files
            class_names: List of class names (auto-detected if using .pt)
            device: 'cpu', 'cuda', or specific GPU ID
            conf_thresh: Default confidence threshold
        """
        self.model_path = Path(model_path) if model_path else None
        self.class_names = class_names or self._default_class_names()
        self.device = device
        self.conf_thresh = conf_thresh
        self.model_type = None
        self.model = None
        
        # Load model
        if self.model_path:
            self._load_model()
        else:
            logger.warning("No model path provided. Initialize with load_model()")
    
    @staticmethod
    def _default_class_names() -> List[str]:
        """Default class names for skin conditions."""
        return [
            'acne',
            'eczema',
            'psoriasis',
            'dandruff',
            'rosacea',
        ]
    
    def _load_model(self):
        """Load model from path."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        # Try loading as YOLOv8
        if str(self.model_path).endswith('.pt') and ULTRALYTICS_AVAILABLE:
            self._load_yolov8_model()
        # Try loading as OpenCV model
        elif str(self.model_path).endswith(('.onnx', '.xml', '.bin')):
            self._load_opencv_model()
        else:
            if ULTRALYTICS_AVAILABLE:
                self._load_yolov8_model()
            else:
                raise ValueError(
                    f"Could not determine model type for {self.model_path}. "
                    f"Ensure Ultralytics is installed or provide ONNX model."
                )
    
    def _load_yolov8_model(self):
        """Load YOLOv8 model using Ultralytics."""
        if not ULTRALYTICS_AVAILABLE:
            raise ImportError(
                "Ultralytics not available. Install with: pip install ultralytics"
            )
        
        logger.info(f"Loading YOLOv8 model: {self.model_path}")
        
        try:
            self.model = YOLO(str(self.model_path))
            
            # Extract class names from model
            if hasattr(self.model, 'names'):
                model_classes = self.model.names
                if isinstance(model_classes, dict):
                    # Convert dict to list (indexed by class_id)
                    self.class_names = [
                        model_classes[i] 
                        for i in sorted(model_classes.keys())
                    ]
                else:
                    self.class_names = model_classes
            
            self.model_type = 'yolov8'
            logger.info(
                f"✓ YOLOv8 model loaded successfully. "
                f"Classes: {len(self.class_names)}"
            )
        
        except Exception as e:
            logger.error(f"Failed to load YOLOv8 model: {e}")
            raise
    
    def _load_opencv_model(self):
        """Load OpenCV DNN model (ONNX or similar)."""
        logger.info(f"Loading OpenCV model: {self.model_path}")
        
        try:
            self.model = cv2.dnn.readNet(str(self.model_path))
            self.model_type = 'opencv'
            logger.info("✓ OpenCV model loaded successfully")
        
        except Exception as e:
            logger.error(f"Failed to load OpenCV model: {e}")
            raise
    
    def load_model(self, model_path: str):
        """
        Load a new model.
        
        Args:
            model_path: Path to model file
        """
        self.model_path = Path(model_path)
        self._load_model()
    
    def detect(
        self,
        image_path: str,
        conf_thresh: Optional[float] = None,
        return_summary: bool = True,
    ) -> Dict[str, Any]:
        """
        Run inference on image.
        
        Args:
            image_path: Path to input image
            conf_thresh: Confidence threshold (uses default if None)
            return_summary: Whether to return per-class summary
            
        Returns:
            Dict with detections and metadata:
            {
                'detections': [Detection.to_dict(), ...],
                'summary': {'class_name': count, ...},
                'model_type': 'yolov8' or 'opencv',
                'total_detections': int,
                'image_shape': (height, width),
            }
        """
        if self.model is None:
            raise RuntimeError("Model not loaded. Call load_model() first.")
        
        if conf_thresh is None:
            conf_thresh = self.conf_thresh
        
        # Load image
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = cv2.imread(str(image_path))
        if image is None:
            raise ValueError(f"Failed to load image: {image_path}")
        
        height, width = image.shape[:2]
        
        # Run inference
        if self.model_type == 'yolov8':
            detections = self._detect_yolov8(image, conf_thresh, width, height)
        elif self.model_type == 'opencv':
            detections = self._detect_opencv(image, conf_thresh, width, height)
        else:
            raise RuntimeError(f"Unknown model type: {self.model_type}")
        
        # Build result dict
        result = {
            'detections': [d.to_dict() for d in detections],
            'model_type': self.model_type,
            'total_detections': len(detections),
            'image_shape': (height, width),
        }
        
        # Add summary if requested
        if return_summary:
            summary = defaultdict(int)
            for detection in detections:
                summary[detection.class_name] += 1
            result['summary'] = dict(summary)
        
        return result
    
    def _detect_yolov8(
        self,
        image: np.ndarray,
        conf_thresh: float,
        width: int,
        height: int,
    ) -> List[Detection]:
        """
        Run YOLOv8 inference.
        
        Args:
            image: Input image (BGR)
            conf_thresh: Confidence threshold
            width: Image width
            height: Image height
            
        Returns:
            List of Detection objects
        """
        detections = []
        
        # Run prediction
        results = self.model.predict(
            source=image,
            conf=conf_thresh,
            verbose=False,
        )
        
        # Process results
        for result in results:
            for box in result.boxes:
                class_id = int(box.cls[0])
                confidence = float(box.conf[0])
                
                # Get class name
                class_name = self.class_names[class_id] if class_id < len(self.class_names) else f"class_{class_id}"
                
                # Get bounding box (xyxy format)
                x1, y1, x2, y2 = box.xyxy[0].cpu().numpy()
                x1, y1, x2, y2 = float(x1), float(y1), float(x2), float(y2)
                
                # Normalize coordinates
                bbox_norm = (x1 / width, y1 / height, x2 / width, y2 / height)
                
                # Calculate relative area
                area = ((x2 - x1) / width) * ((y2 - y1) / height)
                
                detection = Detection(
                    class_id=class_id,
                    class_name=class_name,
                    confidence=confidence,
                    bbox_xyxy=(x1, y1, x2, y2),
                    bbox_norm=bbox_norm,
                    area=area,
                )
                detections.append(detection)
        
        return detections
    
    def _detect_opencv(
        self,
        image: np.ndarray,
        conf_thresh: float,
        width: int,
        height: int,
    ) -> List[Detection]:
        """
        Run OpenCV DNN inference.
        
        Note: This is a fallback implementation. Requires proper model setup.
        
        Args:
            image: Input image (BGR)
            conf_thresh: Confidence threshold
            width: Image width
            height: Image height
            
        Returns:
            List of Detection objects
        """
        detections = []
        
        logger.warning(
            "OpenCV inference is not fully implemented. "
            "Please use YOLOv8 for full functionality."
        )
        
        # Placeholder implementation
        return detections
    
    def detect_batch(
        self,
        image_paths: List[str],
        conf_thresh: Optional[float] = None,
    ) -> List[Dict[str, Any]]:
        """
        Run inference on multiple images.
        
        Args:
            image_paths: List of image paths
            conf_thresh: Confidence threshold
            
        Returns:
            List of detection results
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.detect(image_path, conf_thresh)
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                results.append({
                    'error': str(e),
                    'image_path': str(image_path),
                })
        
        return results
    
    def draw_detections(
        self,
        image_path: str,
        output_path: str,
        conf_thresh: Optional[float] = None,
        line_thickness: int = 2,
        text_size: float = 0.6,
    ):
        """
        Draw detections on image and save.
        
        Args:
            image_path: Path to input image
            output_path: Path to save annotated image
            conf_thresh: Confidence threshold
            line_thickness: Line thickness for boxes
            text_size: Font size for labels
        """
        # Run detection
        result = self.detect(image_path, conf_thresh)
        
        # Load image
        image = cv2.imread(str(image_path))
        
        # Draw detections
        for detection_dict in result['detections']:
            x1, y1, x2, y2 = detection_dict['bbox_xyxy']
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            
            # Draw bounding box
            cv2.rectangle(image, (x1, y1), (x2, y2), (0, 255, 0), line_thickness)
            
            # Draw label
            label = (
                f"{detection_dict['class_name']} "
                f"{detection_dict['confidence']:.2f}"
            )
            cv2.putText(
                image,
                label,
                (x1, y1 - 5),
                cv2.FONT_HERSHEY_SIMPLEX,
                text_size,
                (0, 255, 0),
                1,
            )
        
        # Save image
        cv2.imwrite(str(output_path), image)
        logger.info(f"✓ Annotated image saved: {output_path}")


def analyze_detections(
    detections: Dict[str, Any],
    condition_thresholds: Optional[Dict[str, int]] = None,
) -> Dict[str, Any]:
    """
    Analyze detection results and provide insights.
    
    Args:
        detections: Detection result from ConditionDetector.detect()
        condition_thresholds: Dict mapping class name to severity threshold
        
    Returns:
        Analysis dict with insights
    """
    summary = detections.get('summary', {})
    total = detections.get('total_detections', 0)
    
    if condition_thresholds is None:
        condition_thresholds = {
            'acne': 5,
            'eczema': 3,
            'psoriasis': 3,
            'dandruff': 2,
            'rosacea': 2,
        }
    
    analysis = {
        'total_conditions_detected': total,
        'dominant_condition': max(summary.items())[0] if summary else None,
        'conditions_breakdown': summary,
        'severity_assessment': {},
    }
    
    # Assess severity for each condition
    for condition, count in summary.items():
        threshold = condition_thresholds.get(condition, 3)
        if count == 0:
            severity = 'none'
        elif count < threshold:
            severity = 'mild'
        elif count < threshold * 2:
            severity = 'moderate'
        else:
            severity = 'severe'
        
        analysis['severity_assessment'][condition] = {
            'count': count,
            'severity': severity,
        }
    
    return analysis


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Run skin condition detection on image'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model weights'
    )
    parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='Path to input image'
    )
    parser.add_argument(
        '--conf',
        type=float,
        default=0.3,
        help='Confidence threshold'
    )
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save annotated image'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Print results as JSON'
    )
    
    args = parser.parse_args()
    
    # Initialize detector
    detector = ConditionDetector(model_path=args.model)
    
    # Run detection
    results = detector.detect(args.image, conf_thresh=args.conf)
    
    # Print results
    if args.json:
        import json
        print(json.dumps(results, indent=2))
    else:
        print(f"\nDetections: {results['total_detections']}")
        print(f"Summary: {results['summary']}")
        
        for detection in results['detections']:
            print(
                f"  {detection['class_name']}: "
                f"conf={detection['confidence']:.3f}, "
                f"bbox={detection['bbox_norm']}"
            )
    
    # Draw and save if requested
    if args.output:
        detector.draw_detections(args.image, args.output, conf_thresh=args.conf)
