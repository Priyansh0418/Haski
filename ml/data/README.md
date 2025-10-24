# Dataset Preparation - Quick Reference

## Files in This Directory

- **prepare_dataset.py** - Main script for dataset organization and validation
- **config_classification.yaml** - Configuration for classification datasets
- **config_detection.yaml** - Configuration for detection datasets (YOLO)
- **USAGE.md** - Comprehensive usage guide with examples
- **examples.py** - Example workflows and common patterns
- **README.md** - This file

## One-Liner Quickstart

### Classification (Skin Type)

```bash
python prepare_dataset.py --task classification \
  --source /path/to/images --output datasets/skin_type \
  --config config_classification.yaml
```

### Detection (Conditions - YOLO)

```bash
python prepare_dataset.py --task detection \
  --source /path/to/images --labels /path/to/labels \
  --output datasets/conditions --config config_detection.yaml
```

## Features

### ✅ Automatic Validation

- **Image files**: Checks readability with Pillow
- **YOLO labels**: Validates format and coordinate ranges
- **Class coverage**: Reports missing labels
- **File integrity**: Skips corrupted files with warnings

### ✅ Flexible Input

- **Copy mode**: Duplicates files (safer)
- **Symlink mode**: Links files (faster, saves space with `--symlink`)
- **Config files**: YAML-based configuration for reproducibility

### ✅ Rich Output

- **Manifest JSON**: Dataset statistics and split information
- **YOLO config**: data.yaml for YOLOv5/v8 training
- **Console summary**: Class distribution and validation results

## Output Files

### Classification Dataset

```
output_dir/
├── train/{class_name}/*.jpg
├── val/{class_name}/*.jpg
├── test/{class_name}/*.jpg
└── manifest.json
```

### Detection Dataset

```
output_dir/
├── images/{train,val,test}/*.jpg
├── labels/{train,val,test}/*.txt
├── data.yaml
└── manifest.json
```

## Common Issues & Solutions

| Issue                | Solution                                |
| -------------------- | --------------------------------------- |
| "File not found"     | Verify source directory structure       |
| "Invalid image"      | Check image format (JPG/PNG/GIF/WebP)   |
| "Skipped N images"   | Corrupted files - safe to ignore        |
| "Label not found"    | Ensure .txt files match image filenames |
| "Coord out of range" | Normalize YOLO labels to 0-1            |
| "Empty label file"   | Remove empty label files                |

## Dataset Statistics

### Classification Example

```
Skin Type Classification Summary
==================================================
Total images: 5250

Class distribution:
  normal              : 1250 (23.8%)
  dry                 :  980 (18.7%)
  oily                : 1120 (21.3%)
  combination         : 1050 (20.0%)
  sensitive           :  850 (16.2%)
```

### Detection Example

```
Condition Detection Metrics (YOLO)
===================================
Total images: 1200

Images per split:
  train     :  800
  val       :  200
  test      :  200

Class distribution:
  0: acne           : 450 annotations
  1: eczema         : 380 annotations
  2: psoriasis      : 320 annotations
  3: dandruff       : 410 annotations
  4: rosacea        : 290 annotations
  5: hair_loss      : 350 annotations
```

## Advanced Options

### Use Symlinks (Large Datasets)

```bash
python prepare_dataset.py --task classification \
  --source /external/drive/data --output datasets/skin_type \
  --config config_classification.yaml --symlink
```

### Custom Manifest Path

```bash
python prepare_dataset.py --task classification \
  --source /data --output datasets/skin_type \
  --config config_classification.yaml \
  --manifest /reports/my_dataset_manifest.json
```

## Integration with Training

### Classification Training (PyTorch)

```python
from torchvision import datasets, transforms

transform = transforms.Compose([
    transforms.Resize(224),
    transforms.ToTensor(),
    transforms.Normalize(mean=[0.485, 0.456, 0.406],
                         std=[0.229, 0.224, 0.225])
])

dataset = datasets.ImageFolder('datasets/skin_type/train', transform=transform)
```

### Detection Training (YOLOv8)

```bash
# Use generated data.yaml
yolo detect train model=yolov8n.pt data=datasets/conditions/data.yaml \
  epochs=100 imgsz=640
```

## Performance Tips

1. **Use `--symlink`** for large datasets (>50GB)
2. **Pre-validate** a small subset first
3. **Check manifest.json** before training
4. **Monitor class balance** - consider augmentation if imbalanced
5. **Store source data** separately from processed datasets

## Data Format Reference

### Classification Directory Structure

```
train/
├── normal/
│   ├── image1.jpg
│   └── image2.jpg
├── dry/
│   ├── image101.jpg
│   └── image102.jpg
└── [other classes]
```

### YOLO Label Format

```
class_id center_x center_y width height

Example:
0 0.5 0.5 0.3 0.4
1 0.2 0.3 0.1 0.15
```

**Ranges**: All values are normalized (0 to 1)

- `center_x`, `center_y`: Relative to image center
- `width`, `height`: Relative to image size

## Command Reference

```bash
# Show help
python prepare_dataset.py --help

# Classification dataset
python prepare_dataset.py \
  --task classification \
  --source <source_dir> \
  --output <output_dir> \
  --config config_classification.yaml \
  [--symlink] \
  [--manifest <path>]

# Detection dataset
python prepare_dataset.py \
  --task detection \
  --source <images_dir> \
  --labels <labels_dir> \
  --output <output_dir> \
  --config config_detection.yaml \
  [--symlink] \
  [--manifest <path>]
```

## Next Steps

1. **Prepare dataset** → Run prepare_dataset.py
2. **Validate** → Check manifest.json
3. **Review** → Inspect a sample of images
4. **Train** → Use generated dataset structure
5. **Iterate** → Adjust config and re-prepare as needed

## Support

For detailed instructions, see **USAGE.md**

For example workflows, run:

```bash
python examples.py
```

---

**Last Updated:** 2025-10-24  
**Supported Formats:** JPG, PNG, GIF, WebP  
**YOLO Version:** v5, v8 compatible
