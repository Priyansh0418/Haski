# Label Format Conversion and Validation Guide

## Overview

`label_utils.py` provides utilities for converting between different annotation formats commonly used in computer vision:

- **Pascal VOC XML** - Traditional format used by PASCAL VOC datasets
- **COCO JSON** - Modern format used by Microsoft COCO dataset
- **YOLO TXT** - Detection format used by YOLOv5/v8 training

## Installation

```bash
# No additional dependencies beyond standard library
pip install pillow  # Optional, only for image operations
```

## Quick Reference

### Convert Pascal VOC to YOLO

```bash
python label_utils.py convert-voc \
  --input /path/to/xml/annotations \
  --output /path/to/yolo/labels \
  --images /path/to/images \
  --copy-images
```

### Convert COCO to YOLO

```bash
python label_utils.py convert-coco \
  --input /path/to/coco.json \
  --output /path/to/yolo/labels \
  --images /path/to/images \
  --copy-images
```

### Validate YOLO Labels

```bash
python label_utils.py validate \
  --images /path/to/images \
  --labels /path/to/labels \
  --max-class-id 5
```

### Validate COCO Format

```bash
python label_utils.py validate-coco \
  --annotations /path/to/coco.json \
  --images /path/to/images
```

## Format Specifications

### Pascal VOC XML Format

**File structure:**

```
annotations/
├── image_001.xml
├── image_002.xml
└── ...
```

**Example image_001.xml:**

```xml
<?xml version="1.0"?>
<annotation>
  <filename>image_001.jpg</filename>
  <size>
    <width>640</width>
    <height>480</height>
    <depth>3</depth>
  </size>
  <object>
    <name>acne</name>
    <bndbox>
      <xmin>100</xmin>
      <ymin>120</ymin>
      <xmax>250</xmax>
      <ymax>280</ymax>
    </bndbox>
  </object>
  <object>
    <name>eczema</name>
    <bndbox>
      <xmin>300</xmin>
      <ymin>150</ymin>
      <xmax>400</xmax>
      <ymax>300</ymax>
    </bndbox>
  </object>
</annotation>
```

**Coordinate system:** Absolute pixel coordinates (top-left, bottom-right)

### COCO JSON Format

**File structure:**

```
annotations.json
```

**Example annotations.json:**

```json
{
  "images": [
    {
      "id": 1,
      "file_name": "image_001.jpg",
      "width": 640,
      "height": 480
    },
    {
      "id": 2,
      "file_name": "image_002.jpg",
      "width": 640,
      "height": 480
    }
  ],
  "annotations": [
    {
      "id": 1,
      "image_id": 1,
      "category_id": 0,
      "bbox": [100, 120, 150, 160],
      "area": 24000,
      "iscrowd": 0
    },
    {
      "id": 2,
      "image_id": 1,
      "category_id": 1,
      "bbox": [300, 150, 100, 150],
      "area": 15000,
      "iscrowd": 0
    }
  ],
  "categories": [
    { "id": 0, "name": "acne" },
    { "id": 1, "name": "eczema" },
    { "id": 2, "name": "psoriasis" }
  ]
}
```

**Coordinate system:** COCO bbox format is [x, y, width, height] in absolute pixels (top-left corner)

### YOLO TXT Format

**File structure:**

```
images/
├── train/
│   ├── image_001.jpg
│   ├── image_002.jpg
│   └── ...
└── labels/
    ├── train/
    │   ├── image_001.txt
    │   ├── image_002.txt
    │   └── ...
```

**Example image_001.txt:**

```
0 0.25 0.30 0.23 0.33
1 0.55 0.40 0.15 0.35
```

**Coordinate system:** Normalized coordinates (0 to 1)

- `class_id`: Integer class identifier (0-based)
- `center_x`: Horizontal center (relative to image width)
- `center_y`: Vertical center (relative to image height)
- `width`: Bounding box width (relative to image width)
- `height`: Bounding box height (relative to image height)

## Usage Examples

### Example 1: Convert Pascal VOC to YOLO

```bash
# Directory structure:
# raw_data/
# ├── annotations/*.xml
# ├── images/*.jpg

python label_utils.py convert-voc \
  --input raw_data/annotations \
  --output ml/datasets/detection/labels/train \
  --images raw_data/images \
  --copy-images \
  --class-mapping class_mapping.json
```

**class_mapping.json:**

```json
{
  "acne": 0,
  "eczema": 1,
  "psoriasis": 2,
  "dandruff": 3,
  "rosacea": 4,
  "hair_loss": 5
}
```

### Example 2: Convert COCO to YOLO

```bash
# Directory structure:
# raw_data/
# ├── annotations.json
# ├── images/
#     └── *.jpg

python label_utils.py convert-coco \
  --input raw_data/annotations.json \
  --output ml/datasets/detection/labels/train \
  --images raw_data/images \
  --copy-images
```

### Example 3: Validate YOLO Labels

```bash
python label_utils.py validate \
  --images ml/datasets/detection/images/train \
  --labels ml/datasets/detection/labels/train \
  --max-class-id 5
```

**Expected output:**

```
YOLO Validation Summary
============================================================
Total images:         800
Valid images:         795
Without labels:       3
Invalid labels:       2
Pass rate:            99.4%

Images without labels:
  - img_042.jpg
  - img_128.jpg
  - img_305.jpg

Invalid labels:
  img_015.jpg:
    - Line 1: x_center=1.05 not in range [0,1]
    - Line 2: class_id=7 exceeds max 5
  img_293.jpg:
    - Line 1: Expected 5 values, got 4
```

### Example 4: Validate COCO Format

```bash
python label_utils.py validate-coco \
  --annotations raw_data/annotations.json \
  --images raw_data/images
```

**Expected output:**

```
COCO Validation Summary
============================================================
Valid:        Yes
Images:       1200
Annotations:  5430
Categories:   6

Warnings (2):
  - Image not found: missing_image.jpg
  - Image not found: corrupted.jpg
```

## Python API Usage

### Convert Pascal VOC to YOLO (Programmatic)

```python
from label_utils import VOCtoYOLOConverter
import json

# Load class mapping
with open('class_mapping.json', 'r') as f:
    class_mapping = json.load(f)

# Convert single file
xml_path = 'annotations/image_001.xml'
yolo_string = VOCtoYOLOConverter.convert_pascal_voc_to_yolo(
    xml_path,
    img_width=640,
    img_height=480,
    class_mapping=class_mapping
)
print(yolo_string)

# Batch convert
successful, failed = VOCtoYOLOConverter.batch_convert(
    xml_dir='raw_data/annotations',
    output_dir='ml/datasets/labels/train',
    images_dir='raw_data/images',
    class_mapping=class_mapping,
    copy_images=True
)
print(f"Converted: {successful}, Failed: {failed}")
```

### Convert COCO to YOLO (Programmatic)

```python
from label_utils import COCOtoYOLOConverter

# Convert COCO to YOLO
images_processed, annotations_created, errors = COCOtoYOLOConverter.convert_coco_to_yolo(
    coco_json_path='raw_data/annotations.json',
    output_dir='ml/datasets/labels/train',
    images_dir='raw_data/images',
    copy_images=True
)
print(f"Images: {images_processed}, Annotations: {annotations_created}, Errors: {errors}")
```

### Validate YOLO Labels (Programmatic)

```python
from label_utils import YOLOValidator

# Validate labels
results = YOLOValidator.validate_yolo_labels(
    images_dir='ml/datasets/images/train',
    labels_dir='ml/datasets/labels/train',
    max_class_id=5
)

print(f"Valid: {results['valid_images']}/{results['total_images']}")
print(f"Pass rate: {results['summary']['pass_rate']:.1f}%")

if results['invalid_labels']:
    for item in results['invalid_labels']:
        print(f"\nInvalid: {item['image']}")
        for error in item['errors']:
            print(f"  - {error}")
```

### Validate Single YOLO Label

```python
from label_utils import YOLOValidator

# Validate single label file
is_valid, errors = YOLOValidator.validate_yolo_label(
    label_path='ml/datasets/labels/train/image_001.txt',
    max_class_id=5
)

if is_valid:
    print("Label is valid!")
else:
    for error in errors:
        print(f"Error: {error}")
```

### Validate COCO Format (Programmatic)

```python
from label_utils import YOLOValidator

# Validate COCO JSON
results = YOLOValidator.validate_coco_format(
    coco_json_path='raw_data/annotations.json',
    images_dir='raw_data/images'
)

print(f"Valid: {results['valid']}")
print(f"Summary: {results['summary']}")

if results['errors']:
    print("Errors:")
    for error in results['errors']:
        print(f"  - {error}")
```

## Coordinate Conversion Reference

### VOC to YOLO

**Pascal VOC (pixel coordinates):**

```
xmin=100, ymin=120, xmax=250, ymax=280
Image size: 640x480
```

**YOLO (normalized):**

```
x_center = (100 + 250) / 2 / 640 = 0.273
y_center = (120 + 280) / 2 / 480 = 0.417
width = (250 - 100) / 640 = 0.234
height = (280 - 120) / 480 = 0.333
```

**Result:** `class_id 0.273 0.417 0.234 0.333`

### COCO to YOLO

**COCO format:**

```
bbox = [100, 120, 150, 160]  # [x, y, width, height]
Image size: 640x480
```

**YOLO (normalized):**

```
x_center = (100 + 150/2) / 640 = 0.195
y_center = (120 + 160/2) / 480 = 0.417
width = 150 / 640 = 0.234
height = 160 / 480 = 0.333
```

**Result:** `class_id 0.195 0.417 0.234 0.333`

## Common Issues and Solutions

### Issue: "Class mapping not found"

**Solution:** Provide a valid JSON file with `--class-mapping`:

```json
{
  "acne": 0,
  "eczema": 1,
  "psoriasis": 2
}
```

### Issue: "Coordinate out of range"

**Solution:** Ensure coordinates are normalized to [0, 1]. For conversion issues:

1. Check image dimensions in source format
2. Verify bbox coordinates are reasonable
3. Re-run conversion with proper image sizes

### Issue: "Image not found"

**Solution:** Ensure image paths in JSON match actual files. Check:

1. Case sensitivity (file_name vs filename)
2. Path separators (/ vs \)
3. Image extensions

### Issue: "Missing label file"

**Solution:** Convert annotations first or create placeholder txt files:

```bash
# Create empty label files for images without annotations
for img in images/*.jpg; do
    touch "labels/$(basename "$img" .jpg).txt"
done
```

## Troubleshooting

### Check Output

After conversion, verify the output:

```bash
# Check directory structure
ls -la labels/train/ | head -10

# Sample a label file
cat labels/train/image_001.txt

# Count annotations
wc -l labels/train/*.txt
```

### Debug Conversion

Enable verbose logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# Then run conversion...
```

### Validate After Conversion

Always validate after converting:

```bash
python label_utils.py validate \
  --images images/train \
  --labels labels/train
```

## Performance Notes

- **Pascal VOC conversion:** ~1000 files/minute on modern hardware
- **COCO conversion:** ~500 images/minute (depends on annotations per image)
- **Validation:** ~2000 labels/minute
- Use `--copy-images` only if disk space allows; consider symlinks for large datasets

## File Format Reference

### Class Mapping JSON

```json
{
  "class_name_1": 0,
  "class_name_2": 1,
  "class_name_3": 2
}
```

### Supported Image Formats

- JPEG (.jpg, .jpeg)
- PNG (.png)
- GIF (.gif)
- WebP (.webp)

## Next Steps

1. **Prepare data** - Organize your dataset
2. **Convert labels** - Use appropriate converter
3. **Validate** - Run validation to ensure quality
4. **Train** - Use prepared dataset with training scripts

---

**Last Updated:** 2025-10-24  
**Supported Formats:** Pascal VOC XML, COCO JSON, YOLO TXT  
**License:** Same as parent project
