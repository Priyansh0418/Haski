"""ML Inference Module - Skin Analysis Using Trained Models"""

# ML Inference

Unified inference interface for skin type classification and condition detection models.

## Overview

This module provides production-ready inference APIs for:

- **Classifier**: Skin type classification (normal, dry, oily, combination, sensitive)
- **Detector**: Condition detection (acne, eczema, psoriasis, dandruff, rosacea)

## Installation

```bash
# Core dependencies
pip install torch torchvision pillow numpy opencv-python

# Optional: YOLOv8 support for detection
pip install ultralytics
```

## Quick Start

### Skin Type Classification

```python
from ml.inference import SkinTypeClassifier

# Initialize classifier
classifier = SkinTypeClassifier(
    model_path='ml/exports/skin_classifier.pth',
    class_mapping_path='ml/exports/class_mapping.json',
    model_arch='efficientnet_b0'
)

# Predict on single image
result = classifier.predict(
    image_path='photo.jpg',
    return_probabilities=True,
    top_k=3
)

print(result)
# Output:
# {
#     'predicted_class': 'dry',
#     'confidence': 0.92,
#     'probabilities': {
#         'normal': 0.05,
#         'dry': 0.92,
#         'oily': 0.02,
#         'combination': 0.01,
#         'sensitive': 0.00
#     },
#     'top_k': [
#         {'class': 'dry', 'confidence': 0.92},
#         {'class': 'normal', 'confidence': 0.05},
#         {'class': 'oily', 'confidence': 0.02}
#     ]
# }
```

### Condition Detection

```python
from ml.inference import ConditionDetector, analyze_detections

# Initialize detector
detector = ConditionDetector(
    model_path='ml/exports/detector/detect/weights/best.pt',
    device='cuda'
)

# Detect on single image
result = detector.detect(
    image_path='photo.jpg',
    conf_thresh=0.3,
    return_summary=True
)

print(result)
# Output:
# {
#     'detections': [
#         {
#             'class_id': 0,
#             'class_name': 'acne',
#             'confidence': 0.85,
#             'bbox_xyxy': [100, 150, 200, 250],  # pixels
#             'bbox_norm': [0.1, 0.15, 0.2, 0.25],  # normalized (0-1)
#             'bbox_xywh': [0.1, 0.15, 0.1, 0.1],  # normalized center format
#             'area': 0.01
#         },
#         {
#             'class_id': 1,
#             'class_name': 'eczema',
#             'confidence': 0.72,
#             'bbox_xyxy': [50, 80, 120, 150],
#             'bbox_norm': [0.05, 0.08, 0.12, 0.15],
#             'bbox_xywh': [0.05, 0.08, 0.07, 0.07],
#             'area': 0.005
#         }
#     ],
#     'summary': {'acne': 1, 'eczema': 1},
#     'model_type': 'yolov8',
#     'total_detections': 2,
#     'image_shape': (1000, 1000)
# }

# Analyze detections
analysis = analyze_detections(result)
print(analysis)
# Output:
# {
#     'total_conditions_detected': 2,
#     'dominant_condition': 'acne',
#     'conditions_breakdown': {'acne': 1, 'eczema': 1},
#     'severity_assessment': {
#         'acne': {'count': 1, 'severity': 'mild'},
#         'eczema': {'count': 1, 'severity': 'mild'}
#     }
# }
```

## API Reference

### SkinTypeClassifier

```python
classifier = SkinTypeClassifier(
    model_path: str,                    # Path to .pth model weights
    class_names: Optional[List[str]],   # Class names (or load from mapping)
    class_mapping_path: Optional[str],  # Path to class_mapping.json
    model_arch: str = 'efficientnet_b0',  # 'efficientnet_b0' or 'resnet50'
    device: str = None,                 # 'cuda' or 'cpu' (auto-detect)
)
```

#### Methods

**`predict(image_path, return_probabilities=True, top_k=None)`**

Classify single image.

Args:

- `image_path`: Path to image
- `return_probabilities`: Return full probability distribution
- `top_k`: Return top-K predictions

Returns:

```python
{
    'predicted_class': str,
    'confidence': float,
    'probabilities': {class_name: confidence, ...},  # if return_probabilities=True
    'top_k': [{class, confidence}, ...],  # if top_k is set
}
```

**`predict_batch(image_paths, return_probabilities=True)`**

Classify multiple images.

Args:

- `image_paths`: List of image paths
- `return_probabilities`: Return probability distributions

Returns:

- List of prediction results

### ConditionDetector

```python
detector = ConditionDetector(
    model_path: Optional[str],          # Path to .pt (YOLOv8) model
    class_names: Optional[List[str]],   # Class names for detection
    device: str = 'cpu',                # 'cpu', 'cuda', or GPU ID
    conf_thresh: float = 0.3,           # Default confidence threshold
)
```

#### Methods

**`detect(image_path, conf_thresh=None, return_summary=True)`**

Detect conditions in single image.

Args:

- `image_path`: Path to image
- `conf_thresh`: Confidence threshold (overrides default)
- `return_summary`: Include per-class counts

Returns:

```python
{
    'detections': [
        {
            'class_id': int,
            'class_name': str,
            'confidence': float,
            'bbox_xyxy': [x1, y1, x2, y2],  # pixel coordinates
            'bbox_norm': [x1, y1, x2, y2],  # normalized (0-1)
            'bbox_xywh': [x, y, w, h],      # normalized center format
            'area': float,                  # relative area
        },
        ...
    ],
    'summary': {class_name: count, ...},  # if return_summary=True
    'model_type': 'yolov8' or 'opencv',
    'total_detections': int,
    'image_shape': (height, width),
}
```

**`detect_batch(image_paths, conf_thresh=None)`**

Detect conditions in multiple images.

Args:

- `image_paths`: List of image paths
- `conf_thresh`: Confidence threshold

Returns:

- List of detection results

**`draw_detections(image_path, output_path, conf_thresh=None, line_thickness=2, text_size=0.6)`**

Draw detection boxes on image and save.

Args:

- `image_path`: Path to input image
- `output_path`: Path to save annotated image
- `conf_thresh`: Confidence threshold
- `line_thickness`: Box line thickness
- `text_size`: Label font size

**`load_model(model_path)`**

Load a new model.

### analyze_detections()

```python
analysis = analyze_detections(
    detections: Dict,                          # Result from detector.detect()
    condition_thresholds: Optional[Dict[str, int]] = None  # Severity thresholds
)
```

Returns:

```python
{
    'total_conditions_detected': int,
    'dominant_condition': str,  # Most frequent condition
    'conditions_breakdown': {class_name: count, ...},
    'severity_assessment': {
        class_name: {
            'count': int,
            'severity': 'none' | 'mild' | 'moderate' | 'severe'
        },
        ...
    }
}
```

## Backend Integration

### Using with FastAPI (ml_infer.py)

```python
from ml.inference import ConditionDetector, SkinTypeClassifier, analyze_detections

class SkinAnalyzer:
    def __init__(self, classifier_path, detector_path):
        self.classifier = SkinTypeClassifier(
            model_path=classifier_path,
            class_mapping_path='ml/exports/class_mapping.json'
        )
        self.detector = ConditionDetector(model_path=detector_path)

    def analyze_image(self, image_path: str) -> dict:
        # Classify skin type
        classification_result = self.classifier.predict(
            image_path,
            return_probabilities=True
        )

        # Detect conditions
        detection_result = self.detector.detect(
            image_path,
            conf_thresh=0.3,
            return_summary=True
        )

        # Analyze detections
        analysis = analyze_detections(detection_result)

        # Combine results
        return {
            'skin_type': classification_result['predicted_class'],
            'skin_type_confidence': classification_result['confidence'],
            'conditions': analysis['conditions_breakdown'],
            'dominant_condition': analysis['dominant_condition'],
            'severity': analysis['severity_assessment'],
            'total_detections': analysis['total_conditions_detected'],
        }
```

## Command Line Usage

### Classifier

```bash
# Predict with default classes
python ml/inference/classifier_infer.py \
  --model ml/exports/skin_classifier.pth \
  --image photo.jpg

# With class mapping
python ml/inference/classifier_infer.py \
  --model ml/exports/skin_classifier.pth \
  --image photo.jpg \
  --class-mapping ml/exports/class_mapping.json

# Output as JSON
python ml/inference/classifier_infer.py \
  --model ml/exports/skin_classifier.pth \
  --image photo.jpg \
  --json

# Using ResNet50
python ml/inference/classifier_infer.py \
  --model ml/exports/skin_classifier.pth \
  --image photo.jpg \
  --arch resnet50
```

### Detector

```bash
# Basic detection
python ml/inference/detector_infer.py \
  --model ml/exports/detector/weights/best.pt \
  --image photo.jpg

# With confidence threshold
python ml/inference/detector_infer.py \
  --model ml/exports/detector/weights/best.pt \
  --image photo.jpg \
  --conf 0.5

# Save annotated image
python ml/inference/detector_infer.py \
  --model ml/exports/detector/weights/best.pt \
  --image photo.jpg \
  --output annotated.jpg

# Output as JSON
python ml/inference/detector_infer.py \
  --model ml/exports/detector/weights/best.pt \
  --image photo.jpg \
  --json
```

## Performance Considerations

### Model Selection

**Classifier**:

- EfficientNet-B0: Fast (80ms), suitable for real-time
- ResNet50: Accurate (120ms), for high-accuracy requirements

**Detector**:

- YOLOv8n: Fast (40ms), real-time
- YOLOv8s: Balanced (60ms)
- YOLOv8m: Accurate (120ms)

### GPU vs CPU

```python
# Use GPU (recommended)
detector = ConditionDetector(model_path='...', device='cuda')
classifier = SkinTypeClassifier(model_path='...', device='cuda')

# Use CPU
detector = ConditionDetector(model_path='...', device='cpu')
classifier = SkinTypeClassifier(model_path='...', device='cpu')
```

### Batch Processing

For multiple images:

```python
# Classifier batch
results = classifier.predict_batch(image_paths)

# Detector batch
results = detector.detect_batch(image_paths)
```

## Troubleshooting

### Model Not Found

```python
# Error: FileNotFoundError: Model not found: path/to/model.pth
# Solution: Check model path exists and is correct
```

### Class Names Mismatch

```python
# Solution 1: Provide class_names directly
classifier = SkinTypeClassifier(
    model_path='model.pth',
    class_names=['normal', 'dry', 'oily', 'combination', 'sensitive']
)

# Solution 2: Use class_mapping.json
classifier = SkinTypeClassifier(
    model_path='model.pth',
    class_mapping_path='ml/exports/class_mapping.json'
)
```

### CUDA Out of Memory

```python
# Solution: Use CPU
detector = ConditionDetector(model_path='...', device='cpu')
```

### Ultralytics Not Available

```python
# Error: ImportError: Ultralytics not available
# Solution: Install ultralytics
pip install ultralytics

# Or use OpenCV models (limited support)
detector = ConditionDetector(model_path='model.onnx')
```

## File Structure

```
ml/inference/
├── __init__.py                 # Module exports
├── classifier_infer.py         # Classification inference
├── detector_infer.py           # Detection inference
└── README.md                   # This file
```

## References

- [PyTorch Models](https://pytorch.org/vision/stable/models.html)
- [Ultralytics YOLOv8](https://docs.ultralytics.com/)
- [Transfer Learning](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

---

**Status**: ✅ Classifier and detector inference modules complete  
**Integration**: Ready for backend/services/ml_infer.py  
**Last Updated**: 2025-10-24
