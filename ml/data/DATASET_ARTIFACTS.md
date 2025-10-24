# 📊 Haski ML Dataset Structure & Artifacts

## Quick Links

- 📋 **Manifest Documentation**: [MANIFEST_FORMAT.md](MANIFEST_FORMAT.md)
- 📝 **Data Collection Guide**: [../DATA_COLLECTION.md](../DATA_COLLECTION.md)
- 🔄 **Manifest Generator**: [generate_manifest.py](generate_manifest.py)

---

## Overview

The Haski ML pipeline uses two dataset formats:

1. **Classification** - ImageFolder format for skin/hair type classification
2. **Detection** - YOLO format for condition lesion detection

Both formats have corresponding `manifest.json` files tracking statistics, quality metrics, and version history.

---

## Expected Artifacts

### ✅ Master Manifest

**File**: `ml/data/manifest.json`

Contains:

- Dataset overview (name, version, creation date)
- Overall statistics (total images, split sizes)
- Class distributions (counts and percentages)
- Demographic breakdown (skin tone, age, gender, lighting, device)
- Quality metrics (inter-rater kappa, approval %)
- Version history with changelog
- Class mappings for training
- Expected performance benchmarks

**Size**: ~50-100 KB  
**Update frequency**: After each dataset version  
**Auto-generated**: Yes, use `python generate_manifest.py`

### ✅ Classification Dataset

**Location**: `ml/data/skin_classification/`

```
skin_classification/
├── train/
│   ├── normal/
│   │   ├── img_001.jpg
│   │   ├── img_002.jpg
│   │   └── ... (700 images)
│   ├── dry/
│   │   └── ... (700 images)
│   ├── oily/
│   │   └── ... (700 images)
│   ├── combination/
│   │   └── ... (700 images)
│   └── sensitive/
│       └── ... (700 images)
│
├── val/
│   ├── normal/ (150 images)
│   ├── dry/ (150 images)
│   ├── oily/ (150 images)
│   ├── combination/ (150 images)
│   └── sensitive/ (150 images)
│
├── test/
│   └── [Same structure as val]
│
└── split_manifest.json
```

**Stats**:

- Train: 3,500 images (70%)
- Val: 750 images (15%)
- Test: 750 images (15%)
- Classes: 5 (normal, dry, oily, combination, sensitive)
- Format: JPG/PNG, variable resolution (480p-4K)

**Usage**:

```python
from torchvision import datasets, transforms

# Load training set
train_data = datasets.ImageFolder(
    'ml/data/skin_classification/train',
    transform=transforms.ToTensor()
)

# Get classes
classes = train_data.classes  # ['combination', 'dry', 'normal', 'oily', 'sensitive']
```

### ✅ Detection Dataset (YOLO Format)

**Location**: `ml/data/yolo/`

```
yolo/
├── images/
│   ├── train/ (3500 JPG/PNG files)
│   ├── val/ (750 JPG/PNG files)
│   └── test/ (750 JPG/PNG files)
│
├── labels/
│   ├── train/ (3500 .txt label files)
│   │   ├── img_001.txt    # class cx cy w h (normalized)
│   │   ├── img_002.txt    # One line per object
│   │   └── ...
│   ├── val/ (750 .txt label files)
│   └── test/ (750 .txt label files)
│
├── data.yaml              # YOLO config file
└── yolo_manifest.json     # Detection-specific metadata
```

**Label Format** (img_001.txt):

```
0 0.50 0.45 0.30 0.40    # class cx cy width height (normalized 0-1)
2 0.20 0.30 0.10 0.15    # Another object on same image
4 0.75 0.80 0.15 0.25    # Third object
```

**Classes**:

```
0: acne_mild
1: acne_moderate
2: acne_severe
3: rash
4: eczema
5: infection_fungal
6: infection_bacterial
7: psoriasis
8: hair_loss
```

**Stats**:

- Total images: 5,000
- Total objects: ~12,500 (2.5 per image)
- Train: 3,500 images with 8,750 objects
- Val: 750 images with 1,875 objects
- Test: 750 images with 1,875 objects
- Classes: 9 conditions

### ✅ Split Manifest

**File**: `ml/data/skin_classification/split_manifest.json`

Per-split metadata showing:

- Image counts per class
- Sample image filenames
- Quality checks
- Last verification date

**Usage**: Verify dataset integrity before training

### ✅ YOLO Manifest

**File**: `ml/data/yolo/yolo_manifest.json`

Contains:

- Class mapping
- Split statistics (image count, annotation count, avg objects/image)
- Per-class statistics and confidence scores
- Bounding box coverage statistics
- Quality validation results
- Performance benchmarks by model
- YOLO training/validation/inference commands

### ✅ Metadata Files

**Location**: `ml/data/metadata/`

```
metadata/
├── image_metadata.csv           # Per-image demographics
│   └── Columns: image_id, filename, skin_tone, age_range, gender,
│              lighting, device, image_quality, etc.
│
├── consent_log.csv              # Consent tracking
│   └── Columns: user_id, image_ids, consent_date, consent_type, etc.
│
└── annotations.csv              # Label details
    └── Columns: image_id, skin_type, hair_type, conditions,
               confidence, annotator, qa_status, etc.
```

### ✅ YOLO Configuration

**File**: `ml/data/yolo/data.yaml`

Defines:

- Dataset paths (train, val, test)
- Number of classes
- Class names mapping
- Example training commands
- Tips and best practices

---

## Generating Manifests

### Auto-Generate from Directory

```bash
# Generate both classification and detection manifests
cd ml/data
python generate_manifest.py

# Classification only
python generate_manifest.py --type classification

# Detection only
python generate_manifest.py --type detection

# Custom data directory
python generate_manifest.py --data-dir /path/to/data --output-dir /path/to/output
```

### Using Makefile

```bash
# From ml/ directory
make generate-manifests           # If target exists in Makefile
```

---

## Manifest Contents

### Dataset Info Section

```json
{
  "dataset_info": {
    "name": "Haski Skin & Hair Dataset",
    "version": "2.1",
    "created_date": "2025-10-24",
    "total_images": 5000,
    "annotation_complete": true,
    "quality_score": 0.94
  }
}
```

### Statistics Section

```json
{
  "dataset_statistics": {
    "total_images": 5000,
    "train_images": 3500,
    "val_images": 750,
    "test_images": 750,
    "splits": {
      "train": { "count": 3500, "percentage": 70.0 },
      "val": { "count": 750, "percentage": 15.0 },
      "test": { "count": 750, "percentage": 15.0 }
    }
  }
}
```

### Class Distribution

```json
{
  "skin_type_distribution": {
    "total_classes": 5,
    "classes": {
      "normal": {
        "count": 1000,
        "percentage": 20.0,
        "train": 700,
        "val": 150,
        "test": 150
      }
    }
  }
}
```

### Quality Metrics

```json
{
  "quality_metrics": {
    "inter_rater_reliability": {
      "cohens_kappa_skin_type": 0.87,
      "cohens_kappa_hair_type": 0.89,
      "status": "APPROVED"
    },
    "annotation_status": {
      "completion_percentage": 100.0,
      "qa_approval_percentage": 99.8
    }
  }
}
```

---

## Loading in Python

### Load Classification Manifest

```python
import json

with open('ml/data/manifest.json', 'r') as f:
    manifest = json.load(f)

# Get statistics
total = manifest['dataset_statistics']['total_images']
train_count = manifest['dataset_statistics']['train_images']
print(f"Total: {total}, Train: {train_count}")

# Get class distribution
classes = manifest['skin_type_distribution']['classes']
for class_name, data in classes.items():
    print(f"{class_name}: {data['count']} ({data['percentage']:.1f}%)")

# Check quality
kappa = manifest['quality_metrics']['inter_rater_reliability']['cohens_kappa_skin_type']
print(f"Quality (Cohen's Kappa): {kappa:.3f}")
```

### Load YOLO Manifest

```python
import json
import yaml

# Load YOLO manifest
with open('ml/data/yolo/yolo_manifest.json', 'r') as f:
    yolo_manifest = json.load(f)

# Load data.yaml
with open('ml/data/yolo/data.yaml', 'r') as f:
    data_yaml = yaml.safe_load(f)

print(f"Classes: {data_yaml['names']}")
print(f"Total images: {yolo_manifest['total_images']}")
print(f"Total annotations: {yolo_manifest['total_annotations']}")
```

### Load with PyTorch

```python
from torchvision import datasets, transforms
import json

# Load manifest
with open('ml/data/manifest.json') as f:
    manifest = json.load(f)

# Create dataset
train_data = datasets.ImageFolder(
    'ml/data/skin_classification/train',
    transform=transforms.ToTensor()
)

# Map class indices to names
class_mapping = manifest['class_mappings']['skin_type']
print(f"Classes: {list(class_mapping.values())}")
```

---

## Validating Manifests

```python
import json

def validate_manifest(manifest_path):
    """Validate manifest structure and contents."""

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    errors = []
    warnings = []

    # Check required sections
    required = ['dataset_info', 'dataset_statistics', 'quality_metrics']
    for section in required:
        if section not in manifest:
            errors.append(f"Missing section: {section}")

    # Check image counts sum correctly
    stats = manifest.get('dataset_statistics', {})
    total = stats.get('total_images', 0)
    splits_sum = sum([s['count'] for s in stats.get('splits', {}).values()])
    if splits_sum != total:
        warnings.append(f"Split mismatch: {splits_sum} vs {total}")

    # Check quality metrics
    quality = manifest.get('quality_metrics', {})
    kappa = quality.get('inter_rater_reliability', {}).get('cohens_kappa_skin_type', 0)
    if kappa < 0.70:
        warnings.append(f"Low IRR (kappa={kappa:.2f})")

    # Check annotation completion
    completion = quality.get('annotation_status', {}).get('completion_percentage', 0)
    if completion < 100:
        warnings.append(f"Incomplete: {completion:.0f}%")

    return {
        'valid': len(errors) == 0,
        'errors': errors,
        'warnings': warnings
    }

# Validate
result = validate_manifest('ml/data/manifest.json')
if result['valid']:
    print("✅ Manifest is valid")
else:
    print("❌ Errors found:")
    for err in result['errors']:
        print(f"  - {err}")
```

---

## Version Control

### Version History in Manifest

```json
{
  "version_history": [
    {
      "version": "2.1",
      "date": "2025-10-24",
      "total_images": 5000,
      "quality_score": 0.94,
      "changes": [
        "Added 1000 Type I skin tone images",
        "Re-annotated 200 ambiguous images",
        "Improved kappa from 0.84 to 0.87"
      ]
    },
    {
      "version": "2.0",
      "date": "2025-09-15",
      "total_images": 4800,
      "quality_score": 0.91
    }
  ]
}
```

### Archiving Versions

```bash
# Save versioned manifests
cp ml/data/manifest.json ml/data/versions/v2.1_manifest.json
cp ml/data/yolo/yolo_manifest.json ml/data/versions/v2.1_yolo_manifest.json
```

---

## Checklist for Dataset Artifacts

Use this checklist when preparing datasets:

### Classification Dataset ✅

- [ ] `ml/data/skin_classification/train/` with 5 class folders
- [ ] `ml/data/skin_classification/val/` with same classes
- [ ] `ml/data/skin_classification/test/` with same classes
- [ ] All images are valid JPG/PNG
- [ ] No corrupted or missing files
- [ ] `split_manifest.json` exists and is valid
- [ ] Train/val/test split is 70/15/15

### Detection Dataset ✅

- [ ] `ml/data/yolo/images/train|val|test/` with images
- [ ] `ml/data/yolo/labels/train|val|test/` with .txt files
- [ ] One .txt file per image with matching name
- [ ] Labels in YOLO format (normalized 0-1)
- [ ] No missing labels
- [ ] `data.yaml` with class mapping
- [ ] `yolo_manifest.json` exists and is valid

### Metadata Files ✅

- [ ] `ml/data/metadata/image_metadata.csv` exists
- [ ] `ml/data/metadata/consent_log.csv` exists
- [ ] All required columns present
- [ ] No null values in critical fields

### Manifests ✅

- [ ] `ml/data/manifest.json` generated and validated
- [ ] `ml/data/skin_classification/split_manifest.json` valid
- [ ] `ml/data/yolo/yolo_manifest.json` valid
- [ ] All statistics match actual data
- [ ] Quality scores ≥ 0.90
- [ ] Inter-rater kappa ≥ 0.80

### Documentation ✅

- [ ] `MANIFEST_FORMAT.md` describes structure
- [ ] `data.yaml` has example commands
- [ ] Version history is current
- [ ] Change log is updated

---

## Quick Troubleshooting

**Problem**: Manifest generation fails
**Solution**:

1. Check directory paths match expected structure
2. Verify image files have correct extensions (.jpg, .png)
3. Ensure label files exist for all detection images

**Problem**: Class counts don't match
**Solution**:

1. Re-run `generate_manifest.py`
2. Check for missing subdirectories
3. Verify no files were deleted

**Problem**: Quality metrics look wrong
**Solution**:

1. Manually validate inter-rater reliability
2. Check QA approval status
3. Review flagged images

---

## Summary

The manifest system provides:

- ✅ **Transparency**: Complete dataset statistics
- ✅ **Traceability**: Version history and changelog
- ✅ **Quality assurance**: Comprehensive metrics
- ✅ **Reproducibility**: Exact class distributions
- ✅ **Automation**: Auto-generation from directories

Generate manifests regularly as your dataset evolves!

---

**Last Updated**: 2025-10-24  
**Version**: 2.1  
**Status**: Production Ready
