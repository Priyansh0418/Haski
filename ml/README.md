# Part 2: Machine Learning Pipeline - Skin & Hair Analysis

## Overview

This document describes the ML training pipeline for the Haski backend. Part 2 focuses on building and training models for:

- **Skin Type Classification** (normal, dry, oily, combination, sensitive)
- **Hair Type Classification** (straight, wavy, curly, coily)
- **Condition Detection** (acne, eczema, psoriasis, dandruff, hair_loss, etc.)

The trained models are exported to **ONNX** and **TensorFlow Lite** formats for integration with the backend inference service.

---

## Project Goals (Part 2)

1. **Model Development**

   - Build classification models for skin/hair type detection
   - Build object detection model for condition localization (optional)
   - Achieve >80% accuracy on validation set
   - Support real-time inference on mobile devices

2. **Data Pipeline**

   - Organize training data with clear label structure
   - Support YOLO format for detection tasks
   - Support COCO format for evaluation
   - Version datasets and track splits (train/val/test)

3. **Training Infrastructure**

   - Modular training scripts for reproducibility
   - Model versioning and checkpoint management
   - Metrics tracking (precision, recall, F1, mAP)
   - Export to production-ready formats

4. **Integration**
   - Seamless model loading in `backend/services/ml_infer.py`
   - Support for batch inference
   - Graceful fallback to mock predictions

---

## Dataset Structure

```
ml/
├── datasets/
│   ├── raw/                          # Original images
│   │   ├── train/
│   │   │   ├── skin_type/
│   │   │   │   ├── normal/
│   │   │   │   ├── dry/
│   │   │   │   ├── oily/
│   │   │   │   ├── combination/
│   │   │   │   └── sensitive/
│   │   │   ├── hair_type/
│   │   │   │   ├── straight/
│   │   │   │   ├── wavy/
│   │   │   │   ├── curly/
│   │   │   │   └── coily/
│   │   │   └── conditions/
│   │   │       ├── mild_acne/
│   │   │       ├── severe_acne/
│   │   │       ├── eczema/
│   │   │       └── psoriasis/
│   │   ├── val/
│   │   │   └── [same structure as train]
│   │   └── test/
│   │       └── [same structure as train]
│   │
│   ├── yolo/                         # YOLO format (for detection tasks)
│   │   ├── images/
│   │   │   ├── train/
│   │   │   ├── val/
│   │   │   └── test/
│   │   ├── labels/
│   │   │   ├── train/               # .txt files with YOLO format
│   │   │   ├── val/
│   │   │   └── test/
│   │   └── data.yaml                # YOLO dataset config
│   │
│   └── coco/                         # COCO format (for detection evaluation)
│       ├── images/
│       ├── train/
│       ├── val/
│       └── annotations.json          # COCO format annotations
│
├── models/                           # Trained models
│   ├── checkpoints/                 # Training checkpoints
│   │   ├── skin_type_v1/
│   │   ├── hair_type_v1/
│   │   └── conditions_v1/
│   ├── exports/                     # Production models
│   │   ├── skin_type_v1.onnx
│   │   ├── skin_type_v1.tflite
│   │   ├── hair_type_v1.onnx
│   │   ├── hair_type_v1.tflite
│   │   ├── conditions_v1.onnx
│   │   └── conditions_v1.tflite
│   └── metadata/                    # Model info & class mappings
│       ├── skin_type_v1_metadata.json
│       ├── hair_type_v1_metadata.json
│       └── conditions_v1_metadata.json
│
├── training/
│   ├── model.py                     # Model architectures
│   ├── train.py                     # Main training script
│   ├── evaluate.py                  # Evaluation metrics
│   ├── export.py                    # Export to ONNX/TFLite
│   └── config/
│       ├── skin_type_config.yaml
│       ├── hair_type_config.yaml
│       └── conditions_config.yaml
│
└── README.md                        # This file
```

---

## Label Formats

### 1. Classification (Skin Type / Hair Type)

**Directory structure (simplest):**

```
datasets/raw/train/skin_type/
├── normal/
│   ├── img_001.jpg
│   ├── img_002.jpg
│   └── ...
├── dry/
│   ├── img_101.jpg
│   └── ...
└── [other classes]
```

**CSV format (for tracking):**

```csv
image_path,label,split
images/train/001.jpg,normal,train
images/train/002.jpg,dry,train
images/val/101.jpg,oily,val
```

### 2. Object Detection (Conditions)

**YOLO Format:**

```
# labels/train/img_001.txt
0 0.5 0.5 0.3 0.4    # class center_x center_y width height (normalized)
2 0.2 0.3 0.1 0.2    # another condition on same image
```

Class indices (conditions):

```
0: acne
1: eczema
2: psoriasis
3: dandruff
4: rosacea
5: hair_loss
```

**COCO Format:**

```json
{
  "images": [
    { "id": 1, "file_name": "img_001.jpg", "height": 480, "width": 640 }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [320, 240, 192, 256],
      "area": 49152,
      "iscrowd": 0
    }
  ],
  "categories": [
    { "id": 0, "name": "acne" },
    { "id": 1, "name": "eczema" }
  ]
}
```

---

## Model Types

### 1. Skin Type Classification

- **Architecture**: ResNet50, EfficientNetB3, or ViT (Vision Transformer)
- **Input**: 224×224 RGB image
- **Output**: 5-class probabilities (normal, dry, oily, combination, sensitive)
- **Metrics**: Accuracy, F1 per class

### 2. Hair Type Classification

- **Architecture**: ResNet50, MobileNetV3
- **Input**: 224×224 RGB image
- **Output**: 4-class probabilities (straight, wavy, curly, coily)
- **Metrics**: Accuracy, F1 per class

### 3. Condition Detection (Optional)

- **Architecture**: YOLOv8, YOLOv5, or Faster R-CNN
- **Input**: Variable size RGB image (auto-resized)
- **Output**: Bounding boxes + class + confidence
- **Metrics**: mAP@0.5, mAP@0.95, Precision, Recall

---

## Training Flow

### Quick Start - Skin Type Classification

```bash
cd ml

# 1. Install dependencies
pip install -r requirements.txt
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
pip install onnx onnxruntime
pip install tensorflow tensorflow-lite

# 2. Prepare dataset (organize into directories)
# Ensure: datasets/raw/train/skin_type/{normal,dry,oily,combination,sensitive}/
#         datasets/raw/val/skin_type/{normal,dry,oily,combination,sensitive}/

# 3. Train model
python training/train.py \
  --task skin_type \
  --model resnet50 \
  --epochs 50 \
  --batch_size 32 \
  --learning_rate 1e-4 \
  --augment \
  --output models/checkpoints/skin_type_v1

# 4. Evaluate
python training/evaluate.py \
  --model_path models/checkpoints/skin_type_v1/best.pth \
  --data_dir datasets/raw/val/skin_type \
  --task skin_type

# 5. Export to ONNX & TFLite
python training/export.py \
  --model_path models/checkpoints/skin_type_v1/best.pth \
  --task skin_type \
  --export_dir models/exports \
  --formats onnx tflite
```

### Quick Start - Hair Type Classification

```bash
cd ml

python training/train.py \
  --task hair_type \
  --model resnet50 \
  --epochs 50 \
  --batch_size 32 \
  --augment \
  --output models/checkpoints/hair_type_v1

python training/evaluate.py \
  --model_path models/checkpoints/hair_type_v1/best.pth \
  --data_dir datasets/raw/val/hair_type \
  --task hair_type

python training/export.py \
  --model_path models/checkpoints/hair_type_v1/best.pth \
  --task hair_type \
  --export_dir models/exports \
  --formats onnx tflite
```

### Quick Start - Condition Detection (YOLOv8)

```bash
cd ml

# Ensure YOLO dataset is in place: datasets/yolo/
# Should have images/labels in train/val/test subdirectories

python training/train.py \
  --task conditions \
  --model yolov8n \
  --epochs 100 \
  --batch_size 16 \
  --data_yaml datasets/yolo/data.yaml \
  --output models/checkpoints/conditions_v1 \
  --device cuda

python training/export.py \
  --model_path models/checkpoints/conditions_v1/best.pt \
  --task conditions \
  --export_dir models/exports \
  --formats onnx tflite
```

---

## Evaluation Metrics

### Classification Metrics

```
Accuracy:  (TP + TN) / (TP + TN + FP + FN)
Precision: TP / (TP + FP)
Recall:    TP / (TP + FN)
F1 Score:  2 * (Precision * Recall) / (Precision + Recall)
```

**Example Output:**

```
Skin Type Classification Metrics
================================
Overall Accuracy: 0.8742

Per-Class Metrics:
- normal:      Precision=0.88, Recall=0.91, F1=0.895
- dry:         Precision=0.86, Recall=0.84, F1=0.850
- oily:        Precision=0.82, Recall=0.80, F1=0.810
- combination: Precision=0.91, Recall=0.87, F1=0.890
- sensitive:   Precision=0.79, Recall=0.82, F1=0.805
```

### Detection Metrics (COCO)

```
mAP@0.5:   Mean Average Precision at IoU=0.5
mAP@0.75:  Mean Average Precision at IoU=0.75
mAP@0.5:95: Mean Average Precision across IoU thresholds
Precision: TP / (TP + FP)
Recall:    TP / (TP + FN)
```

**Example Output:**

```
Condition Detection Metrics (YOLO)
===================================
mAP@0.5:   0.752
mAP@0.75:  0.614
mAP@0.5:95: 0.458
Precision: 0.798
Recall:    0.741

Per-Class mAP@0.5:
- acne:      0.81
- eczema:    0.72
- psoriasis: 0.65
- dandruff:  0.74
- rosacea:   0.68
- hair_loss: 0.70
```

---

## Export Targets

### 1. ONNX (Open Neural Network Exchange)

**Benefits:**

- Cross-platform (CPU + GPU on any hardware)
- Optimized inference
- Language-agnostic (Python, C++, C#, etc.)
- Best for server-side inference

**Export command:**

```bash
python training/export.py \
  --model_path models/checkpoints/skin_type_v1/best.pth \
  --format onnx \
  --output_path models/exports/skin_type_v1.onnx
```

**Backend usage:**

```python
import onnxruntime as ort
session = ort.InferenceSession("models/skin_type_v1.onnx")
predictions = session.run(None, {"input": image_tensor})
```

### 2. TensorFlow Lite (TFLite)

**Benefits:**

- Ultra-lightweight (~5-20 MB)
- Fast mobile inference
- Low latency (real-time on mobile)
- Support for quantization

**Export command:**

```bash
python training/export.py \
  --model_path models/checkpoints/skin_type_v1/best.pth \
  --format tflite \
  --quantize int8 \
  --output_path models/exports/skin_type_v1.tflite
```

**Mobile usage (iOS/Android):**

```python
import tensorflow as tf

# Load TFLite model
interpreter = tf.lite.Interpreter(model_path="skin_type_v1.tflite")
interpreter.allocate_tensors()

# Run inference
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
interpreter.set_tensor(input_details[0]['index'], input_image)
interpreter.invoke()
predictions = interpreter.get_tensor(output_details[0]['index'])
```

---

## Integration with Backend

### Plugging Models into `backend/services/ml_infer.py`

Current implementation uses mock predictions. To integrate real models:

#### Step 1: Update Model Loading

```python
# backend/services/ml_infer.py

import onnxruntime as ort
import numpy as np
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent.parent / "ml" / "models" / "exports"

# Load models at startup
skin_type_model = ort.InferenceSession(str(MODEL_DIR / "skin_type_v1.onnx"))
hair_type_model = ort.InferenceSession(str(MODEL_DIR / "hair_type_v1.onnx"))
conditions_model = ort.InferenceSession(str(MODEL_DIR / "conditions_v1.onnx"))

# Class mappings
SKIN_TYPES = ["normal", "dry", "oily", "combination", "sensitive"]
HAIR_TYPES = ["straight", "wavy", "curly", "coily"]
CONDITIONS = ["mild_acne", "severe_acne", "eczema", "psoriasis", "dandruff", "rosacea", "hair_loss"]
```

#### Step 2: Preprocess Image

```python
from PIL import Image
import cv2

def preprocess_image(image_bytes: bytes, target_size: tuple = (224, 224)) -> np.ndarray:
    """Convert image bytes to model input tensor."""
    # Read image
    image = Image.open(BytesIO(image_bytes)).convert("RGB")

    # Resize
    image = image.resize(target_size, Image.Resampling.LANCZOS)

    # Normalize
    image_array = np.array(image).astype(np.float32) / 255.0

    # Add batch dimension
    image_tensor = np.expand_dims(image_array, axis=0)

    return image_tensor
```

#### Step 3: Run Inference

```python
def analyze_image_local(image_path: str) -> dict:
    """Run inference on image using real models."""

    # Read image
    with open(image_path, "rb") as f:
        image_bytes = f.read()

    # Preprocess
    image_tensor = preprocess_image(image_bytes)

    # Run skin type inference
    skin_output = skin_type_model.run(None, {"input": image_tensor})
    skin_probs = skin_output[0][0]
    skin_type_idx = np.argmax(skin_probs)
    skin_type = SKIN_TYPES[skin_type_idx]
    skin_confidence = float(skin_probs[skin_type_idx])

    # Run hair type inference
    hair_output = hair_type_model.run(None, {"input": image_tensor})
    hair_probs = hair_output[0][0]
    hair_type_idx = np.argmax(hair_probs)
    hair_type = HAIR_TYPES[hair_type_idx]
    hair_confidence = float(hair_probs[hair_type_idx])

    # Run condition detection
    conditions_output = conditions_model.run(None, {"input": image_tensor})
    condition_scores = conditions_output[0][0]

    # Extract detected conditions (threshold = 0.5)
    detected_conditions = []
    confidence_scores = {}
    for idx, score in enumerate(condition_scores):
        if score > 0.5:
            condition_name = CONDITIONS[idx]
            detected_conditions.append(condition_name)
            confidence_scores[condition_name] = float(score)

    # If no conditions detected, return empty
    if not detected_conditions:
        detected_conditions = ["none"]

    return {
        "skin_type": skin_type,
        "hair_type": hair_type,
        "conditions_detected": detected_conditions,
        "confidence_scores": {
            "skin_type": skin_confidence,
            "hair_type": hair_confidence,
            **confidence_scores
        },
        "model_version": "v1-onnx"
    }
```

#### Step 4: Error Handling & Fallback

```python
def analyze_image_local(image_path: str) -> dict:
    """Run inference with fallback to mock predictions."""
    try:
        # [inference code above]
        result = {
            "skin_type": skin_type,
            "hair_type": hair_type,
            "conditions_detected": detected_conditions,
            "confidence_scores": {...},
            "model_version": "v1-onnx"
        }
        return result
    except Exception as e:
        print(f"Error during inference: {e}")
        # Fallback to mock predictions
        return {
            "skin_type": "combination",
            "hair_type": "wavy",
            "conditions_detected": ["mild_acne"],
            "confidence_scores": {
                "skin_type": 0.84,
                "hair_type": 0.76,
                "mild_acne": 0.67
            },
            "model_version": "v0-mock"
        }
```

---

## Model Versioning & Checkpoint Management

### Directory Structure for Versions

```
models/exports/
├── skin_type_v1.onnx          # Production v1
├── skin_type_v2.onnx          # Production v2 (improved)
├── skin_type_v2_quantized.onnx # Quantized variant
├── hair_type_v1.onnx
├── conditions_v1.onnx
└── metadata/
    ├── skin_type_v1_metadata.json
    ├── skin_type_v2_metadata.json
    └── conditions_v1_metadata.json
```

### Metadata Format

```json
{
  "model_name": "skin_type_v2",
  "task": "classification",
  "model_type": "resnet50",
  "input_size": [224, 224, 3],
  "classes": ["normal", "dry", "oily", "combination", "sensitive"],
  "training_date": "2025-10-24",
  "accuracy": 0.8742,
  "f1_macro": 0.8621,
  "framework": "pytorch",
  "export_format": "onnx",
  "notes": "Trained on 5000 images with data augmentation"
}
```

---

## Performance Considerations

### Model Optimization

1. **Quantization** (reduce size, maintain accuracy)

   ```bash
   python training/export.py \
     --model_path models/checkpoints/skin_type_v1/best.pth \
     --format tflite \
     --quantize int8 \
     --output_path models/exports/skin_type_v1_quantized.tflite
   ```

2. **Pruning** (remove unnecessary weights)

   - Typically 30-50% size reduction
   - <2% accuracy loss

3. **Knowledge Distillation** (compress using student model)
   - Teacher (large) → Student (small)
   - Good for mobile deployment

### Inference Speed Targets

| Model                        | Size   | Latency (CPU) | Latency (GPU) | Target Device |
| ---------------------------- | ------ | ------------- | ------------- | ------------- |
| ResNet50 (skin_type)         | 102 MB | 500ms         | 50ms          | Server        |
| ResNet50 (skin_type, TFLite) | 25 MB  | 200ms         | -             | Mobile        |
| YOLOv8n (conditions)         | 6.3 MB | 1000ms        | 100ms         | Server        |

---

## Troubleshooting

### Common Issues

1. **Model not found during inference**

   - Ensure models are exported to `ml/models/exports/`
   - Check file paths in `ml_infer.py`
   - Verify model formats match framework (ONNX vs TFLite)

2. **Poor accuracy on new images**

   - Check image preprocessing (normalization, resizing)
   - Verify classes match training data
   - Retrain with more diverse data

3. **Slow inference**

   - Use quantized models
   - Consider model size reduction
   - Use GPU acceleration if available

4. **Import errors**
   - Verify `ml/requirements.txt` installed
   - Check ONNX Runtime vs PyTorch versions
   - Ensure TensorFlow/TensorFlow Lite versions match

---

## Next Steps

1. **Data Collection**: Gather 5,000+ high-quality images per class
2. **Dataset Split**: Organize into train (70%) / val (15%) / test (15%)
3. **Model Training**: Run training scripts, track metrics
4. **Evaluation**: Achieve >80% accuracy target
5. **Export & Integration**: Export models and plug into backend
6. **Testing**: End-to-end API testing with real models
7. **Deployment**: Deploy backend with trained models

---

## References

- **PyTorch**: https://pytorch.org/
- **ONNX**: https://onnx.ai/
- **TensorFlow Lite**: https://www.tensorflow.org/lite
- **YOLOv8**: https://docs.ultralytics.com/
- **Hugging Face Models**: https://huggingface.co/models

---

## Contributing

When adding new models or improving existing ones:

1. Update model metadata in `models/metadata/`
2. Document training hyperparameters
3. Track metrics and accuracy improvements
4. Add notes about dataset used
5. Update this README with new model info

---

**Last Updated**: 2025-10-24  
**Current Production Models**: skin_type_v1, hair_type_v1, conditions_v0-mock  
**Next Milestone**: Full condition detection model (conditions_v1)
