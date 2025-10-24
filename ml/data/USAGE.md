# Dataset Preparation Guide

This guide explains how to use `prepare_dataset.py` to organize your image datasets for Haski ML training.

## Overview

The script supports two dataset types:

1. **Classification** - ImageFolder structure for skin/hair type classification
2. **Detection** - YOLO format for condition detection with bounding boxes

## Prerequisites

```bash
pip install pillow pyyaml
```

## Classification Dataset

### Directory Structure

Your source data should be organized as:

```
source_data/
├── train/
│   ├── normal/
│   │   ├── img_001.jpg
│   │   ├── img_002.jpg
│   │   └── ...
│   ├── dry/
│   │   ├── img_101.jpg
│   │   └── ...
│   └── [other classes]
├── val/
│   ├── normal/
│   │   └── ...
│   └── [other classes]
└── test/
    ├── normal/
    │   └── ...
    └── [other classes]
```

### Prepare Classification Dataset

**Basic usage:**

```bash
cd ml/data

python prepare_dataset.py \
  --task classification \
  --source /path/to/source_data \
  --output ../../ml/datasets/skin_type \
  --config config_classification.yaml
```

**With symlinks (faster, saves disk space):**

```bash
python prepare_dataset.py \
  --task classification \
  --source /path/to/source_data \
  --output ../../ml/datasets/skin_type \
  --config config_classification.yaml \
  --symlink
```

**Output structure:**

```
ml/datasets/
└── skin_type/
    ├── train/
    │   ├── normal/
    │   │   ├── img_001.jpg
    │   │   └── ...
    │   ├── dry/
    │   │   └── ...
    │   └── [other classes]
    ├── val/
    ├── test/
    └── manifest.json
```

### Output Manifest (Classification)

**manifest.json:**

```json
{
  "task": "classification",
  "structure": "imagefolder",
  "splits": {
    "train": [],
    "val": [],
    "test": []
  },
  "class_counts": {
    "normal": 1250,
    "dry": 980,
    "oily": 1120,
    "combination": 1050,
    "sensitive": 850
  },
  "total_images": 5250
}
```

## Detection Dataset (YOLO Format)

### Directory Structure

Your source data should be organized as:

```
source_data/
├── images/
│   ├── train/
│   │   ├── img_001.jpg
│   │   ├── img_002.jpg
│   │   └── ...
│   ├── val/
│   │   └── ...
│   └── test/
│       └── ...
└── labels/
    ├── train/
    │   ├── img_001.txt
    │   ├── img_002.txt
    │   └── ...
    ├── val/
    │   └── ...
    └── test/
        └── ...
```

### YOLO Label Format

Each `.txt` file contains one line per bounding box:

```
class_id center_x center_y width height
```

**Important:** All coordinates are **normalized to 0-1 range** (relative to image size)

**Example img_001.txt:**

```
0 0.5 0.5 0.3 0.4
2 0.2 0.3 0.1 0.2
```

This means:

- Box 1: class 0 (acne) at center (50%, 50%) with width 30%, height 40%
- Box 2: class 2 (psoriasis) at center (20%, 30%) with width 10%, height 20%

### Converting from Other Formats

If your labels are in a different format, you need to convert them first:

**From COCO JSON to YOLO:**

```python
import json
from pathlib import Path

def coco_to_yolo(coco_json_path, output_dir):
    """Convert COCO format annotations to YOLO format."""
    with open(coco_json_path) as f:
        coco = json.load(f)

    # Build image lookup
    images = {img['id']: img for img in coco['images']}

    # Process annotations
    for annotation in coco['annotations']:
        image_id = annotation['image_id']
        image_info = images[image_id]

        image_width = image_info['width']
        image_height = image_info['height']

        # COCO bbox: [x, y, width, height]
        bbox = annotation['bbox']
        class_id = annotation['category_id']

        # Convert to YOLO format (normalized)
        x_center = (bbox[0] + bbox[2] / 2) / image_width
        y_center = (bbox[1] + bbox[3] / 2) / image_height
        width = bbox[2] / image_width
        height = bbox[3] / image_height

        # Write to YOLO label file
        label_file = output_dir / f"{Path(image_info['file_name']).stem}.txt"
        with open(label_file, 'a') as f:
            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

# Usage
coco_to_yolo("annotations.json", Path("labels/train"))
```

**From Pascal VOC XML to YOLO:**

```python
import xml.etree.ElementTree as ET
from pathlib import Path

def voc_to_yolo(xml_file, output_file):
    """Convert Pascal VOC XML to YOLO format."""
    tree = ET.parse(xml_file)
    root = tree.getroot()

    # Get image dimensions
    size = root.find('size')
    img_width = int(size.find('width').text)
    img_height = int(size.find('height').text)

    # Process objects
    with open(output_file, 'w') as f:
        for obj in root.findall('object'):
            class_name = obj.find('name').text
            bbox = obj.find('bndbox')

            xmin = float(bbox.find('xmin').text)
            ymin = float(bbox.find('ymin').text)
            xmax = float(bbox.find('xmax').text)
            ymax = float(bbox.find('ymax').text)

            # Convert to YOLO format
            x_center = (xmin + xmax) / 2 / img_width
            y_center = (ymin + ymax) / 2 / img_height
            width = (xmax - xmin) / img_width
            height = (ymax - ymin) / img_height

            class_id = class_mapping[class_name]  # Define class_mapping
            f.write(f"{class_id} {x_center} {y_center} {width} {height}\n")

# Usage
voc_to_yolo("image_001.xml", "labels/train/image_001.txt")
```

### Prepare Detection Dataset

**Basic usage:**

```bash
cd ml/data

python prepare_dataset.py \
  --task detection \
  --source /path/to/images \
  --labels /path/to/labels \
  --output ../../ml/datasets/conditions \
  --config config_detection.yaml
```

**Output structure:**

```
ml/datasets/
└── conditions/
    ├── images/
    │   ├── train/
    │   │   ├── img_001.jpg
    │   │   └── ...
    │   ├── val/
    │   └── test/
    ├── labels/
    │   ├── train/
    │   │   ├── img_001.txt
    │   │   └── ...
    │   ├── val/
    │   └── test/
    ├── data.yaml          # YOLO config
    └── manifest.json
```

### Output Manifest (Detection)

**manifest.json:**

```json
{
  "task": "detection",
  "format": "yolo",
  "splits": {
    "train": {
      "images": "/path/to/images/train",
      "labels": "/path/to/labels/train",
      "count": 800
    },
    "val": {
      "images": "/path/to/images/val",
      "labels": "/path/to/labels/val",
      "count": 200
    },
    "test": {
      "images": "/path/to/images/test",
      "labels": "/path/to/labels/test",
      "count": 200
    }
  },
  "class_names": {
    "0": "acne",
    "1": "eczema",
    "2": "psoriasis",
    "3": "dandruff",
    "4": "rosacea",
    "5": "hair_loss"
  },
  "class_counts": {
    "0": 450,
    "1": 380,
    "2": 320,
    "3": 410,
    "4": 290,
    "5": 350
  },
  "total_images": 1200,
  "images_without_labels": []
}
```

**data.yaml (for YOLO training):**

```yaml
path: /absolute/path/to/conditions
train: images/train
val: images/val
test: images/test
nc: 6
names:
  0: acne
  1: eczema
  2: psoriasis
  3: dandruff
  4: rosacea
  5: hair_loss
```

## Validation Features

The script automatically validates:

1. **Image Files**

   - Checks if files exist
   - Verifies files are readable with Pillow
   - Skips corrupted images with warning

2. **Label Files (Detection)**

   - Checks for corresponding `.txt` file
   - Validates YOLO format (5 values per line)
   - Ensures coordinates are normalized (0-1 range)
   - Reports images without labels

3. **Class Distribution**
   - Counts images per class
   - Displays percentage breakdown
   - Identifies missing classes

## Example Workflows

### Workflow 1: Prepare Skin Type Classification

```bash
# Organize your source data
mkdir -p raw_data/train/{normal,dry,oily,combination,sensitive}
mkdir -p raw_data/val/{normal,dry,oily,combination,sensitive}
mkdir -p raw_data/test/{normal,dry,oily,combination,sensitive}

# Copy/move images to appropriate folders
# Then prepare dataset:

python ml/data/prepare_dataset.py \
  --task classification \
  --source raw_data \
  --output ml/datasets/skin_type \
  --config ml/data/config_classification.yaml \
  --symlink

# Check output
cat ml/datasets/manifest.json
```

### Workflow 2: Prepare Condition Detection

```bash
# Assuming you have images and YOLO labels
# Images in: raw_data/images/{train,val,test}/*.jpg
# Labels in: raw_data/labels/{train,val,test}/*.txt

python ml/data/prepare_dataset.py \
  --task detection \
  --source raw_data/images \
  --labels raw_data/labels \
  --output ml/datasets/conditions \
  --config ml/data/config_detection.yaml

# Check YOLO config
cat ml/datasets/conditions/data.yaml

# Check manifest
cat ml/datasets/conditions/manifest.json
```

### Workflow 3: Handle Large Datasets with Symlinks

For large datasets, use symlinks to save disk space:

```bash
python ml/data/prepare_dataset.py \
  --task classification \
  --source /external/drive/huge_dataset \
  --output ml/datasets/skin_type \
  --config ml/data/config_classification.yaml \
  --symlink \
  --manifest ml/datasets/skin_type_manifest.json
```

## Troubleshooting

### Issue: "Image file not found"

**Solution:** Ensure your source data structure matches the expected layout.

### Issue: "Invalid image" or "Could not open image file"

**Solution:** Check if images are corrupted. The script skips these and logs warnings.

### Issue: "Label file not found" (detection)

**Solution:** Ensure your images and labels are in the same relative directory structure with matching filenames.

### Issue: "Coordinate out of range" (detection)

**Solution:** YOLO format requires normalized coordinates (0-1). Verify your label conversion.

### Issue: "Empty label file"

**Solution:** Remove or fix label files with no annotations.

## Next Steps

1. **Prepare your dataset** using this script
2. **Review manifest.json** to ensure data quality
3. **Train your model** using the organized dataset
4. **Monitor class balance** - consider data augmentation if imbalanced

## Tips

- Start with a small subset to test the pipeline
- Use `--symlink` for faster preparation and lower disk usage
- Monitor the summary output for class distribution
- Check manifest.json for quality assurance
- Validate a few random samples manually

---

**Last Updated:** 2025-10-24  
**Supported Formats:** JPG, PNG, GIF, WebP  
**YOLO Format:** YOLOv5, YOLOv8 compatible
