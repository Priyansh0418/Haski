# YOLOv8 Object Detection Training Guide

Complete guide for training YOLOv8 models for skin condition detection using the Ultralytics framework.

## Overview

This guide covers training YOLOv8 models for detecting skin conditions (acne, eczema, psoriasis, etc.) on facial skin regions. YOLOv8 provides state-of-the-art real-time object detection with minimal configuration.

### Why YOLOv8 for Condition Detection?

- **Real-time performance**: 40+ FPS on standard GPUs
- **High accuracy**: mAP@0.5 >75% on COCO dataset
- **Multiple sizes**: Nano (n), Small (s), Medium (m), Large (l), Extra-Large (xl)
- **Transfer learning**: Pre-trained on COCO with 80 classes
- **Easy fine-tuning**: Minimal code required
- **Export options**: ONNX, TFLite, CoreML, TensorRT

## Installation

### Install Ultralytics YOLOv8

```bash
# Basic installation
pip install ultralytics

# With GPU support (recommended)
pip install ultralytics torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118

# With extra utilities
pip install ultralytics opencv-python pillow numpy matplotlib scikit-learn
```

### Verify Installation

```bash
python -c "import ultralytics; print(ultralytics.__version__)"

# Download pre-trained weights (optional, auto-downloads on first run)
yolo task=detect mode=predict model=yolov8n.pt source=https://example.com/image.jpg
```

## Dataset Structure

### YOLO Format Requirements

YOLOv8 requires datasets in a specific directory structure with normalized bounding box annotations.

#### Directory Layout

```
data/
├── images/
│   ├── train/
│   │   ├── image_001.jpg
│   │   ├── image_002.jpg
│   │   └── ...
│   ├── val/
│   │   ├── image_101.jpg
│   │   └── ...
│   └── test/
│       ├── image_201.jpg
│       └── ...
├── labels/
│   ├── train/
│   │   ├── image_001.txt
│   │   ├── image_002.txt
│   │   └── ...
│   ├── val/
│   │   ├── image_101.txt
│   │   └── ...
│   └── test/
│       ├── image_201.txt
│       └── ...
└── data.yaml
```

### Label Format

Each `.txt` file corresponds to an image and contains one line per detection:

```
<class_id> <x_center> <y_center> <width> <height>
```

**Important**: All coordinates are **normalized** (0-1 range):

- `x_center`: Horizontal center as fraction of image width
- `y_center`: Vertical center as fraction of image height
- `width`: Bounding box width as fraction of image width
- `height`: Bounding box height as fraction of image height

#### Example Label File

```
0 0.5 0.3 0.4 0.3
1 0.2 0.7 0.15 0.2
```

This means:

- Class 0 (acne): center at 50% horizontal, 30% vertical; 40% width, 30% height
- Class 1 (eczema): center at 20% horizontal, 70% vertical; 15% width, 20% height

### Format Conversion

Use the provided label conversion utilities to convert from other formats:

```bash
# Convert from Pascal VOC XML to YOLO
cd ml/data
python label_utils.py convert-voc \
  --xml-dir path/to/voc/annotations \
  --output-dir path/to/yolo/labels \
  --image-dir path/to/images

# Convert from COCO JSON to YOLO
python label_utils.py convert-coco \
  --json path/to/coco.json \
  --output-dir path/to/yolo/labels \
  --image-dir path/to/images
```

## Dataset Configuration

### data.yaml

Create a `data.yaml` file in your dataset root directory:

```yaml
# Dataset paths (relative to yaml location or absolute)
path: /path/to/dataset # Dataset root
train: images/train # Training images
val: images/val # Validation images
test: images/test # Test images (optional)

# Number of classes
nc: 5

# Class names
names:
  0: acne
  1: eczema
  2: psoriasis
  3: dandruff
  4: rosacea
```

### Complete data.yaml Example

```yaml
# Skin Condition Detection Dataset
path: ml/data/detection

# Folder locations
train: images/train
val: images/val
test: images/test

# Number of object classes
nc: 5

# Class names (must match label file class indices)
names: ["acne", "eczema", "psoriasis", "dandruff", "rosacea"]

# Download/preparation commands (optional)
download: |
  # Script to download dataset if available
  echo "Download your dataset and organize according to YOLO format"
```

### Minimal data.yaml

If you only have train/val splits:

```yaml
path: ml/data/detection
train: images/train
val: images/val
nc: 5
names: ["acne", "eczema", "psoriasis", "dandruff", "rosacea"]
```

## Training YOLOv8 Models

### Basic Training

```bash
# Train with default settings
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=ml/data/detection/data.yaml \
  epochs=100
```

### Complete Training Command

```bash
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=ml/data/detection/data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=16 \
  patience=20 \
  project=ml/exports/detector \
  name=skin_conditions_v1 \
  device=0 \
  workers=4 \
  optimizer=SGD \
  lr0=0.01 \
  lrf=0.01 \
  momentum=0.937 \
  weight_decay=0.0005 \
  warmup_epochs=3 \
  warmup_momentum=0.8 \
  warmup_bias_lr=0.1 \
  box=7.5 \
  cls=0.5 \
  dfl=1.5 \
  fl_gamma=0.0 \
  label_smoothing=0.0 \
  nbs=64 \
  hsv_h=0.015 \
  hsv_s=0.7 \
  hsv_v=0.4 \
  degrees=0.0 \
  translate=0.1 \
  scale=0.5 \
  flipud=0.0 \
  fliplr=0.5 \
  mosaic=1.0 \
  mixup=0.0 \
  copy_paste=0.0
```

### Model Size Options

| Model   | Size | mAP50 | Speed   | Parameters |
| ------- | ---- | ----- | ------- | ---------- |
| YOLOv8n | 640  | 37.3  | 80.4ms  | 3.2M       |
| YOLOv8s | 640  | 44.9  | 128.4ms | 11.2M      |
| YOLOv8m | 640  | 50.2  | 234.7ms | 25.9M      |
| YOLOv8l | 640  | 52.9  | 375.2ms | 43.7M      |
| YOLOv8x | 640  | 53.9  | 479.1ms | 68.2M      |

**Recommendations**:

- **Mobile/Real-time**: Use YOLOv8n or YOLOv8s
- **Balanced**: Use YOLOv8m
- **High accuracy**: Use YOLOv8l or YOLOv8x

### Training Parameters Explained

#### Model & Data

- `model`: Pre-trained weights (yolov8n.pt, yolov8s.pt, etc.)
- `data`: Path to data.yaml configuration
- `project`: Output directory for runs
- `name`: Run name/experiment identifier

#### Training Settings

- `epochs`: Number of training epochs (typically 50-300)
- `batch`: Batch size (adjust based on GPU memory)
- `imgsz`: Input image size (640 recommended for balance)
- `patience`: Early stopping patience (stop if no improvement)
- `device`: GPU device ID (0, 1, etc.) or 'cpu'

#### Optimization

- `optimizer`: SGD (default), Adam, AdamW
- `lr0`: Initial learning rate
- `lrf`: Final learning rate factor (lr_final = lr0 \* lrf)
- `momentum`: SGD momentum
- `weight_decay`: L2 regularization

#### Augmentation

- `hsv_h`: HSV hue augmentation (0-1)
- `hsv_s`: HSV saturation augmentation (0-1)
- `hsv_v`: HSV value augmentation (0-1)
- `degrees`: Rotation augmentation (degrees)
- `translate`: Translation augmentation (0-1)
- `scale`: Scale augmentation (0-1)
- `flipud`: Vertical flip probability (0-1)
- `fliplr`: Horizontal flip probability (0-1)
- `mosaic`: Mosaic augmentation probability (0-1)
- `mixup`: Mixup augmentation probability (0-1)
- `copy_paste`: Copy-paste augmentation probability (0-1)

#### Loss Weights

- `box`: Box loss weight (default: 7.5)
- `cls`: Classification loss weight (default: 0.5)
- `dfl`: Distribution focal loss weight (default: 1.5)
- `fl_gamma`: Focal loss gamma (0 = no focal loss)

## Training Scenarios

### Scenario 1: Small Dataset (< 500 images)

```bash
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=data.yaml \
  epochs=300 \
  imgsz=640 \
  batch=8 \
  patience=50 \
  lr0=0.001 \
  hsv_h=0.02 \
  hsv_s=0.7 \
  hsv_v=0.4 \
  degrees=10 \
  translate=0.1 \
  scale=0.5 \
  fliplr=0.5 \
  mosaic=1.0
```

### Scenario 2: Medium Dataset (500-5K images)

```bash
yolo task=detect mode=train \
  model=yolov8s.pt \
  data=data.yaml \
  epochs=150 \
  imgsz=640 \
  batch=16 \
  patience=30 \
  lr0=0.01 \
  project=ml/exports/detector \
  name=skin_detector_v2
```

### Scenario 3: Large Dataset (> 5K images)

```bash
yolo task=detect mode=train \
  model=yolov8m.pt \
  data=data.yaml \
  epochs=100 \
  imgsz=640 \
  batch=32 \
  patience=20 \
  lr0=0.01 \
  project=ml/exports/detector \
  name=skin_detector_large
```

## Augmentation Details

### Built-in Augmentations

YOLOv8 includes sophisticated augmentation strategies:

#### Color Augmentations

- **HSV-HSV**: Hue, Saturation, Value shifts to handle different lighting
- Simulates changes in ambient lighting and camera settings

#### Geometric Augmentations

- **Rotation**: Handles tilted detection scenarios
- **Translation**: Shifts objects around the image
- **Scale**: Handles objects at different distances
- **Shear**: Handles perspective distortions
- **Perspective**: Camera angle variations

#### Mixing Augmentations

- **Mosaic**: Combines 4 images in 1 (strong regularization)
- **Mixup**: Blends two images (soft labels)
- **Copy-Paste**: Copies objects between images

#### Flip Augmentations

- **Horizontal Flip**: Natural variations in image capture
- **Vertical Flip**: Can be disabled if not representative

### Recommended Augmentation Settings for Skin Conditions

For skin condition detection with medical/photo variations:

```yaml
# Conservative (for smaller/cleaner datasets)
hsv_h: 0.01
hsv_s: 0.5
hsv_v: 0.3
degrees: 5
translate: 0.05
scale: 0.3
fliplr: 0.5
mosaic: 0.8
mixup: 0.0

# Moderate (balanced approach - recommended)
hsv_h: 0.02
hsv_s: 0.7
hsv_v: 0.4
degrees: 10
translate: 0.1
scale: 0.5
fliplr: 0.5
mosaic: 1.0
mixup: 0.1

# Aggressive (for larger/noisy datasets)
hsv_h: 0.05
hsv_s: 0.9
hsv_v: 0.6
degrees: 15
translate: 0.2
scale: 0.7
fliplr: 0.5
mosaic: 1.0
mixup: 0.3
copy_paste: 0.1
```

## Transfer Learning

### Pre-trained Weights

All YOLOv8 models come pre-trained on COCO (80 classes, 118K images):

```bash
# Start with pre-trained weights (recommended)
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=data.yaml \
  epochs=100

# OR start from scratch (rarely needed)
yolo task=detect mode=train \
  model=yolov8n.yaml \
  data=data.yaml \
  epochs=300
```

### Transfer Learning Benefits

1. **Faster convergence**: Pre-trained features reduce training time
2. **Better accuracy**: Leverages ImageNet and COCO knowledge
3. **Less data required**: Works with smaller datasets
4. **Reduced overfitting**: Pre-trained backbone is regularized

### Fine-tuning Strategy

1. **Freeze backbone** (optional, for very small datasets):

   ```python
   model = YOLO('yolov8n.pt')
   model.train(data='data.yaml', epochs=50, freeze=10)
   ```

2. **Full fine-tuning** (recommended):
   ```bash
   yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100
   ```

## Training Output

### Directory Structure

Training creates organized outputs in your project directory:

```
ml/exports/detector/
└── skin_conditions_v1/
    ├── weights/
    │   ├── best.pt          # Best model (highest mAP)
    │   └── last.pt          # Last epoch model
    ├── plots/
    │   ├── confusion_matrix.png
    │   ├── precision_curve.png
    │   ├── recall_curve.png
    │   ├── f1_curve.png
    │   ├── results.png      # Training metrics plot
    │   └── ...
    ├── results.csv          # Detailed metrics (CSV)
    └── args.yaml            # Training configuration (for reproducibility)
```

### Key Output Files

| File                   | Description                                         |
| ---------------------- | --------------------------------------------------- |
| `best.pt`              | Model with best validation mAP (use for production) |
| `last.pt`              | Model from last epoch (for resuming training)       |
| `results.csv`          | Epoch-by-epoch metrics                              |
| `confusion_matrix.png` | Class confusion patterns                            |
| `results.png`          | Training curves (loss, accuracy, mAP)               |
| `args.yaml`            | Reproducible training configuration                 |

### Resuming Training

To resume interrupted training:

```bash
# Resume from last checkpoint
yolo task=detect mode=train \
  model=ml/exports/detector/skin_conditions_v1/weights/last.pt \
  data=data.yaml \
  epochs=150

# Will continue from epoch where it stopped
```

## Validation & Testing

### Validate Model

```bash
# Validate with validation split
yolo task=detect mode=val \
  model=ml/exports/detector/skin_conditions_v1/weights/best.pt \
  data=data.yaml

# Custom confidence threshold
yolo task=detect mode=val \
  model=best.pt \
  data=data.yaml \
  conf=0.25 \
  iou=0.6
```

### Predictions

```bash
# Single image
yolo task=detect mode=predict \
  model=ml/exports/detector/skin_conditions_v1/weights/best.pt \
  source=test_image.jpg

# Directory of images
yolo task=detect mode=predict \
  model=best.pt \
  source=ml/data/detection/images/test \
  conf=0.5 \
  save=True

# Video
yolo task=detect mode=predict \
  model=best.pt \
  source=video.mp4 \
  save=True
```

## Python Training API

### Train Programmatically

```python
from ultralytics import YOLO

# Load model
model = YOLO('yolov8n.pt')

# Train
results = model.train(
    data='data.yaml',
    epochs=100,
    imgsz=640,
    batch=16,
    patience=20,
    project='ml/exports/detector',
    name='skin_conditions_v1',
    device=0,
)

# Validate
metrics = model.val()

# Predict
predictions = model.predict(source='test.jpg', conf=0.5)

# Export
model.export(format='onnx')  # ONNX, TFLite, CoreML, etc.
```

### Training Results

```python
# Access training results
print(f"Best mAP: {results.best_results}")
print(f"Results file: {results.save_dir}")

# Plot results
results.plot()
```

## Hyperparameter Tuning

### Automated Hyperparameter Tuning

```bash
# Run hyperparameter evolution (computationally expensive)
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=data.yaml \
  epochs=100 \
  hsv_h=0.02 \
  hsv_s=0.7 \
  hsv_v=0.4 \
  degrees=10 \
  translate=0.1 \
  scale=0.5 \
  flipud=0.0 \
  fliplr=0.5 \
  mosaic=1.0 \
  mixup=0.0 \
  copy_paste=0.0 \
  evolve=300  # 300 generations of hyperparameter evolution
```

### Manual Tuning

Start with defaults and adjust based on results:

1. **If overfitting** (train loss low, val loss high):

   - Increase augmentation (mosaic, mixup)
   - Increase weight_decay
   - Reduce model size
   - Reduce learning rate

2. **If underfitting** (both losses high):

   - Increase model size
   - Increase learning rate
   - Decrease augmentation
   - Train longer

3. **If convergence too slow**:
   - Increase learning rate (0.01 → 0.05)
   - Increase batch size
   - Reduce patience threshold

## Troubleshooting

### GPU Memory Issues

```bash
# Reduce batch size
yolo task=detect mode=train model=yolov8n.pt data=data.yaml batch=8

# Reduce image size
yolo task=detect mode=train model=yolov8n.pt data=data.yaml imgsz=512

# Use smaller model
yolo task=detect mode=train model=yolov8n.pt data=data.yaml  # Already nano

# Enable mixed precision
yolo task=detect mode=train model=yolov8n.pt data=data.yaml amp=True
```

### Training Not Converging

```bash
# Increase epochs and patience
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=data.yaml \
  epochs=300 \
  patience=50

# Reduce learning rate
yolo task=detect mode=train \
  model=yolov8n.pt \
  data=data.yaml \
  lr0=0.001

# Check data.yaml paths are correct
# Verify label format (class_id x_center y_center width height, all normalized)
```

### Poor Validation Performance

1. **Check data quality**:

   - Verify images and labels match
   - Ensure bounding boxes are in valid range (0-1)
   - Check for mislabeled images

2. **Class imbalance**:

   ```bash
   # Increase training time for rare classes
   yolo task=detect mode=train \
     model=yolov8n.pt \
     data=data.yaml \
     epochs=200 \
     cls_weight=[1, 2, 1.5, 1, 1]  # Example weights for 5 classes
   ```

3. **Too small objects**:
   - Increase image size: `imgsz=1280` instead of 640
   - Crop images to focus on region of interest

## Model Export

### Export to ONNX

```bash
yolo task=detect mode=export \
  model=ml/exports/detector/skin_conditions_v1/weights/best.pt \
  format=onnx
```

### Export to TensorFlow Lite (Mobile)

```bash
yolo task=detect mode=export \
  model=ml/exports/detector/skin_conditions_v1/weights/best.pt \
  format=tflite
```

### Export to CoreML (iOS)

```bash
yolo task=detect mode=export \
  model=ml/exports/detector/skin_conditions_v1/weights/best.pt \
  format=coreml
```

### Python Export

```python
from ultralytics import YOLO

model = YOLO('best.pt')

# Export to multiple formats
model.export(format='onnx')    # ONNX
model.export(format='tflite')  # TFLite
model.export(format='coreml')  # CoreML
model.export(format='engine')  # TensorRT
```

## Best Practices

1. **Start Small**: Test with YOLOv8n first, then scale up
2. **Monitor Metrics**: Watch training/val loss curves for convergence issues
3. **Use Augmentation**: Especially with smaller datasets
4. **Validate Regularly**: Check validation metrics during training
5. **Save Best Model**: Use the `best.pt` for production, not `last.pt`
6. **Document Runs**: Note hyperparameters and data version
7. **Version Control**: Save training configs for reproducibility
8. **Test on Real Data**: Validate on out-of-distribution images

## Integration with Haski Backend

### Loading in ml_infer.py

```python
from ultralytics import YOLO

class ConditionDetector:
    def __init__(self, model_path='ml/exports/detector/skin_conditions_v1/weights/best.pt'):
        self.model = YOLO(model_path)

    def detect(self, image_path: str, conf: float = 0.5):
        results = self.model.predict(source=image_path, conf=conf)
        detections = []

        for result in results:
            for box in result.boxes:
                detections.append({
                    'class': result.names[int(box.cls)],
                    'confidence': float(box.conf),
                    'bbox': box.xyxy[0].tolist(),
                })

        return detections
```

## References

- [Ultralytics YOLOv8 Docs](https://docs.ultralytics.com/)
- [YOLOv8 GitHub](https://github.com/ultralytics/ultralytics)
- [YOLO Format Specification](https://docs.ultralytics.com/datasets/detect/)
- [Transfer Learning Guide](https://docs.ultralytics.com/yolo/tutorials/transfer-learning-cat-dog/)

## Quick Reference

```bash
# Train
yolo task=detect mode=train model=yolov8n.pt data=data.yaml epochs=100 imgsz=640 batch=16 project=ml/exports/detector

# Validate
yolo task=detect mode=val model=best.pt data=data.yaml

# Predict
yolo task=detect mode=predict model=best.pt source=image.jpg

# Export
yolo task=detect mode=export model=best.pt format=onnx

# Resume
yolo task=detect mode=train model=last.pt data=data.yaml epochs=150
```

---

**Status**: ✅ YOLOv8 Detection Training Guide Complete  
**Next**: Implement training pipeline, model export utilities  
**Last Updated**: 2025-10-24
