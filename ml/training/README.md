"""Training README - Skin Classification & Condition Detection Pipeline"""

# ML Training Pipeline

Complete transfer learning and model training utilities for Haski skin analysis.

## Overview

This module provides production-ready training scripts for:

- **Skin Type Classification** (ResNet50 / EfficientNet-B0)
- **Condition Detection** (YOLOv8)
- **Data Augmentation** (comprehensive transforms)
- **Label Format Conversion** (VOC XML, COCO JSON → YOLO)

## Files

```
ml/training/
├── augmentations.py          # Data augmentation transforms
├── train_classifier.py       # Skin type classification training
├── eval_classifier.py        # Model evaluation & metrics
├── train_detector.py         # (Coming soon) Object detection training
└── export.py                 # (Coming soon) Model export (ONNX, TFLite)
```

## Setup

### Install Dependencies

```bash
# Core dependencies
pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# Additional utilities
pip install tqdm numpy pillow

# Optional: GPU support
pip install torch-cuda  # For CUDA support
```

### Dataset Preparation

Prepare your dataset in one of these formats:

**Option 1: Class Folders (Auto-splits train/val)**

```
data/
├── normal/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── dry/
│   ├── image1.jpg
│   └── ...
├── oily/
└── ...
```

**Option 2: Pre-split Train/Val**

```
data/
├── train/
│   ├── normal/
│   ├── dry/
│   └── ...
└── val/
    ├── normal/
    ├── dry/
    └── ...
```

Use `ml/data/prepare_dataset.py` to organize raw data:

```bash
cd ml/data
python prepare_dataset.py classify \
  --input-dir /path/to/raw/images \
  --output-dir ../training/data \
  --config config_classification.yaml
```

## Training Skin Type Classifier

### Basic Training

```bash
cd ml/training

# Train with EfficientNet-B0 (default)
python train_classifier.py --data-dir ./data --epochs 50

# Train with ResNet50
python train_classifier.py --data-dir ./data --model resnet50 --epochs 50
```

### Advanced Options

```bash
# Full configuration
python train_classifier.py \
  --data-dir ./data \
  --model efficientnet_b0 \
  --epochs 100 \
  --batch-size 32 \
  --lr 0.001 \
  --weight-decay 1e-4 \
  --output ../exports \
  --patience 15 \
  --val-split 0.2 \
  --device cuda

# Using a different device
python train_classifier.py --data-dir ./data --device cpu  # Force CPU

# Early stopping with high patience
python train_classifier.py --data-dir ./data --patience 20
```

### CLI Arguments

| Argument         | Default           | Description                       |
| ---------------- | ----------------- | --------------------------------- |
| `--data-dir`     | **required**      | Dataset directory                 |
| `--model`        | `efficientnet_b0` | `efficientnet_b0` or `resnet50`   |
| `--epochs`       | `50`              | Number of training epochs         |
| `--batch-size`   | `32`              | Batch size                        |
| `--lr`           | `0.001`           | Learning rate                     |
| `--weight-decay` | `1e-4`            | L2 regularization                 |
| `--output`       | `ml/exports`      | Output directory                  |
| `--device`       | `auto`            | `cuda` or `cpu`                   |
| `--num-workers`  | `4`               | DataLoader workers                |
| `--patience`     | `10`              | Early stopping patience           |
| `--val-split`    | `0.2`             | Validation split if no val folder |

## Output Files

After training, find these files in `ml/exports/`:

```
ml/exports/
├── skin_classifier.pth                    # Final trained model
├── skin_classifier_best.pth               # Best model (highest val accuracy)
├── classifier_metrics.json                # Training history & metrics
├── class_mapping.json                     # Class name → index mapping
└── augmentation_samples/                  # (Optional) Preview images
    ├── train_aug_00.jpg
    ├── train_aug_01.jpg
    └── ...
```

### Metrics File Format

`classifier_metrics.json`:

```json
{
  "train_loss": [2.45, 1.98, 1.23, ...],
  "train_accuracy": [0.25, 0.42, 0.68, ...],
  "val_loss": [2.31, 1.89, 1.15, ...],
  "val_accuracy": [0.30, 0.45, 0.72, ...],
  "config": {
    "model": "efficientnet_b0",
    "epochs": 50,
    "batch_size": 32,
    "learning_rate": 0.001,
    "device": "cuda"
  },
  "best_val_accuracy": 0.92,
  "best_val_loss": 0.28,
  "elapsed_time_seconds": 3600,
  "num_epochs_trained": 50
}
```

## Evaluating Trained Models

### Basic Evaluation

```bash
cd ml/training

# Evaluate with test split
python eval_classifier.py \
  --model ../exports/skin_classifier.pth \
  --data-dir ./data

# Evaluate with best model
python eval_classifier.py \
  --model ../exports/skin_classifier_best.pth \
  --data-dir ./data/test
```

### Advanced Options

```bash
# Specify output directory
python eval_classifier.py \
  --model ../exports/skin_classifier.pth \
  --data-dir ./data \
  --output ../exports

# Use CPU for evaluation
python eval_classifier.py \
  --model ../exports/skin_classifier.pth \
  --data-dir ./data \
  --device cpu

# Custom batch size
python eval_classifier.py \
  --model ../exports/skin_classifier.pth \
  --data-dir ./data \
  --batch-size 64
```

### CLI Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `--model` | **required** | Path to model weights (.pth) |
| `--data-dir` | **required** | Test data directory |
| `--class-mapping` | auto-detect | Path to class_mapping.json |
| `--output` | `ml/exports` | Output directory for results |
| `--device` | `auto` | `cuda` or `cpu` |
| `--batch-size` | `32` | Batch size |
| `--num-workers` | `4` | DataLoader workers |

### Output Files

After evaluation, find these files in `ml/exports/`:

```
ml/exports/
├── classifier_eval.json               # Detailed metrics (JSON)
├── confusion_matrix.png               # Confusion matrix heatmap
├── f1_scores.png                      # Per-class F1 scores
├── metrics_comparison.png             # Precision/Recall/F1 comparison
└── classifier_eval_report.txt         # Human-readable report
```

### Metrics File Format

`classifier_eval.json`:
```json
{
  "accuracy": 0.92,
  "precision_macro": 0.90,
  "recall_macro": 0.88,
  "f1_macro": 0.89,
  "precision_weighted": 0.91,
  "recall_weighted": 0.92,
  "f1_weighted": 0.91,
  "per_class_metrics": {
    "normal": {
      "precision": 0.95,
      "recall": 0.93,
      "f1": 0.94,
      "support": 150
    },
    "dry": {
      "precision": 0.88,
      "recall": 0.85,
      "f1": 0.86,
      "support": 120
    }
  },
  "confusion_matrix": [[140, 8, 2], ...],
  "total_samples": 500,
  "correct_predictions": 460,
  "classification_report": {...}
}
```

### Understanding Metrics

**Accuracy**: Overall correctness (TP+TN) / Total

**Precision**: Of predicted positives, how many are correct? TP / (TP+FP)
- High precision = fewer false positives
- Important when false positives are costly

**Recall**: Of actual positives, how many did we catch? TP / (TP+FN)
- High recall = fewer false negatives
- Important when false negatives are costly

**F1 Score**: Harmonic mean of precision and recall
- Balanced metric when both are important
- F1 = 2 × (Precision × Recall) / (Precision + Recall)

**Macro Average**: Simple average of per-class metrics
- Treats all classes equally regardless of sample count
- Good for imbalanced datasets

**Weighted Average**: Weighted by support (number of samples)
- Accounts for class imbalance
- Better for real-world scenarios

**Confusion Matrix**: Shows which classes are confused
- Diagonal = correct predictions
- Off-diagonal = misclassifications
- Helps identify problematic class pairs

## Data Augmentation

### Preview Augmentations

Generate augmented image samples:

```bash
cd ml/training

# Preview augmentations for an image
python augmentations.py preview \
  --image /path/to/image.jpg \
  --output ./augmentation_samples \
  --num-examples 9

# View augmentation config
python augmentations.py info
```

### Augmentation Details

**Training Transforms** (aggressive):

- RandomResizedCrop(224) - crop with 0.8-1.0 scale
- ColorJitter - brightness/contrast/saturation/hue
- RandomHorizontalFlip (50%)
- RandomRotation (±15°)
- RandomAffine - rotation/translation/scale/shear
- RandomPerspective - camera angle simulation
- GaussianBlur - regularization
- Normalize (ImageNet mean/std)

**Validation Transforms** (minimal):

- Resize(256)
- CenterCrop(224)
- Normalize (ImageNet mean/std)

### Custom Augmentation Config

Edit `AugmentationConfig` in `augmentations.py`:

```python
class AugmentationConfig:
    INPUT_SIZE = 224
    RESIZE_SIZE = 256

    # Color augmentation
    COLOR_JITTER_BRIGHTNESS = 0.2
    COLOR_JITTER_CONTRAST = 0.2
    COLOR_JITTER_SATURATION = 0.2
    COLOR_JITTER_HUE = 0.1

    # Geometric augmentation
    RANDOM_ROTATION_DEGREES = 15
    RANDOM_AFFINE_DEGREES = 10
    RANDOM_AFFINE_TRANSLATE = (0.1, 0.1)
    RANDOM_AFFINE_SCALE = (0.8, 1.2)

    # Blur
    GAUSSIAN_BLUR_KERNEL_SIZE = 5
    GAUSSIAN_BLUR_SIGMA = (0.1, 2.0)
```

## Model Architecture

### EfficientNet-B0 (Default)

- **Parameters**: ~5.3M
- **ImageNet Accuracy**: 77.7%
- **Speed**: Fast (suitable for mobile)
- **Best for**: Real-time inference, limited resources

```
Layer          Input Shape       Output Shape
─────────────────────────────────────────
Conv2d         (3, 224, 224)    (32, 112, 112)
MobileInverted (32, 112, 112)   (16, 112, 112)
...
Linear         (1280,)          (num_classes,)
```

### ResNet50

- **Parameters**: ~25.5M
- **ImageNet Accuracy**: 76.1%
- **Speed**: Medium
- **Best for**: High accuracy, production models

```
Layer          Input Shape       Output Shape
─────────────────────────────────────────
Conv2d         (3, 224, 224)    (64, 112, 112)
ResidualBlock  (64, 112, 112)   (256, 56, 56)
...
Linear         (2048,)          (num_classes,)
```

## Training Tips

### Hyperparameter Tuning

```bash
# For small datasets (< 5K images)
python train_classifier.py \
  --data-dir ./data \
  --lr 0.0005 \
  --batch-size 16 \
  --epochs 200 \
  --patience 20

# For medium datasets (5K-50K images)
python train_classifier.py \
  --data-dir ./data \
  --lr 0.001 \
  --batch-size 32 \
  --epochs 100 \
  --patience 15

# For large datasets (> 50K images)
python train_classifier.py \
  --data-dir ./data \
  --lr 0.01 \
  --batch-size 64 \
  --epochs 50 \
  --patience 10
```

### Convergence Monitoring

Training logs show:

- Loss: Should steadily decrease
- Accuracy: Should steadily increase
- Validation should track training (overfitting check)

Example good training:

```
Epoch 1/50 [Train] | loss: 2.31, acc: 0.25
Epoch 1/50 [Val]   | loss: 2.15, acc: 0.35
✓ Validation loss improved to 2.15

Epoch 10/50 [Train] | loss: 0.89, acc: 0.78
Epoch 10/50 [Val]   | loss: 0.92, acc: 0.76

Epoch 50/50 [Train] | loss: 0.15, acc: 0.96
Epoch 50/50 [Val]   | loss: 0.28, acc: 0.92
```

### Dealing with Overfitting

If validation accuracy plateaus while training improves:

```bash
# Increase regularization
python train_classifier.py \
  --data-dir ./data \
  --weight-decay 1e-3 \
  --patience 5

# Reduce learning rate
python train_classifier.py \
  --data-dir ./data \
  --lr 0.0001

# Add more augmentation (edit augmentations.py)
```

### Dealing with Underfitting

If both train and val accuracy are low:

```bash
# Increase epochs
python train_classifier.py \
  --data-dir ./data \
  --epochs 200 \
  --patience 20

# Increase batch size
python train_classifier.py \
  --data-dir ./data \
  --batch-size 64

# Increase learning rate
python train_classifier.py \
  --data-dir ./data \
  --lr 0.01
```

## Using Trained Models

### Load and Predict

```python
import torch
from torchvision import models
import json

# Load model
model = models.efficientnet_b0()
model.classifier[1] = torch.nn.Linear(1280, 5)  # 5 classes
model.load_state_dict(torch.load('ml/exports/skin_classifier.pth'))
model.eval()

# Load class mapping
with open('ml/exports/class_mapping.json') as f:
    class_to_idx = json.load(f)
idx_to_class = {v: k for k, v in class_to_idx.items()}

# Predict
from augmentations import get_transforms
transforms = get_transforms(phase='val')
image = transforms(Image.open('image.jpg'))
image = image.unsqueeze(0)  # Add batch dimension

with torch.no_grad():
    output = model(image)
    predicted_idx = output.argmax(1).item()
    predicted_class = idx_to_class[predicted_idx]

print(f"Predicted: {predicted_class}")
```

### Integration with Backend

The trained model integrates with `backend/services/ml_infer.py`:

```python
from services.ml_infer import SkinAnalyzer

analyzer = SkinAnalyzer(model_path='ml/exports/skin_classifier.pth')
result = analyzer.analyze(image_path='photo.jpg')
# Returns: {'skin_type': 'normal', 'confidence': 0.92}
```

## Troubleshooting

### CUDA Out of Memory

```bash
# Reduce batch size
python train_classifier.py --data-dir ./data --batch-size 16

# Use CPU
python train_classifier.py --data-dir ./data --device cpu
```

### No Classes Found

```bash
# Verify directory structure
ls data/
# Should show: normal dry oily combination sensitive

# OR verify train/val structure
ls data/train/
# Should show class folders
```

### Training Too Slow

```bash
# Increase num_workers
python train_classifier.py --data-dir ./data --num-workers 8

# Use GPU
python train_classifier.py --data-dir ./data --device cuda

# Reduce input size (edit augmentations.py)
```

### Model Not Improving

1. **Check data quality**

   ```bash
   python ml/data/prepare_dataset.py validate --input-dir ./data
   ```

2. **Check augmentation**

   ```bash
   python augmentations.py preview --image sample.jpg --output preview/
   ```

3. **Increase patience**
   ```bash
   python train_classifier.py --data-dir ./data --patience 30
   ```

## Performance Benchmarks

On NVIDIA V100 GPU (typical hardware):

| Model           | Input Size | Batch 32 | Epoch Time | Throughput |
| --------------- | ---------- | -------- | ---------- | ---------- |
| EfficientNet-B0 | 224×224    | 32       | ~45s       | 712 img/s  |
| ResNet50        | 224×224    | 32       | ~60s       | 533 img/s  |

## Next Steps

1. **Prepare your dataset** - Use `ml/data/prepare_dataset.py`
2. **Train classifier** - Run `train_classifier.py`
3. **Evaluate model** - Check `classifier_metrics.json`
4. **Export model** - Deploy to backend (coming soon)
5. **Deploy to production** - Integrate with `ml_infer.py`

## References

- [PyTorch Transfer Learning](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)
- [EfficientNet Paper](https://arxiv.org/abs/1905.11946)
- [ResNet Paper](https://arxiv.org/abs/1512.03385)
- [ImageNet Normalization](https://github.com/pytorch/vision/issues/39)

---

**Status**: ✅ Classifier training implemented  
**Next**: Detector training, model evaluation, export utilities  
**Last Updated**: 2025-10-24
