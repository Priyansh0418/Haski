# Dataset Manifest Format & Structure

## Overview

This document specifies the `manifest.json` format used in Haski ML pipeline to track:

- **Dataset statistics** (class distribution, split sizes)
- **Quality metadata** (Fitzpatrick tone, age range, lighting conditions)
- **Version tracking** (dataset version, creation date, changes)
- **Annotation status** (completion percentage, QA approval)
- **File mappings** (image-to-label relationships)

---

## Directory Structure

```
ml/data/
├── manifest.json                    # Master dataset manifest
├── skin_classification/             # Classification dataset
│   ├── train/
│   │   ├── normal/
│   │   │   ├── img_001.jpg
│   │   │   ├── img_002.jpg
│   │   │   └── ...
│   │   ├── dry/
│   │   ├── oily/
│   │   ├── combination/
│   │   └── sensitive/
│   ├── val/
│   │   └── [same structure as train]
│   ├── test/
│   │   └── [same structure as train]
│   └── split_manifest.json          # Split-specific metadata
│
├── yolo/                            # Detection dataset (YOLO format)
│   ├── images/
│   │   ├── train/
│   │   │   ├── img_001.jpg
│   │   │   ├── img_002.jpg
│   │   │   └── ...
│   │   ├── val/
│   │   └── test/
│   ├── labels/
│   │   ├── train/
│   │   │   ├── img_001.txt          # YOLO format: class x_center y_center width height
│   │   │   ├── img_002.txt
│   │   │   └── ...
│   │   ├── val/
│   │   └── test/
│   ├── data.yaml                    # YOLO config
│   └── yolo_manifest.json           # Detection-specific metadata
│
├── metadata/
│   ├── image_metadata.csv           # Per-image metadata
│   ├── consent_log.csv              # Consent tracking
│   └── annotations.csv              # Label details
│
└── versions/
    ├── v1.0_manifest.json           # Version history
    ├── v1.1_manifest.json
    └── CHANGELOG.md                 # Version changes
```

---

## Manifest JSON Format

### 1. Master Manifest (`ml/data/manifest.json`)

```json
{
  "dataset_info": {
    "name": "Haski Skin & Hair Dataset",
    "version": "2.1",
    "description": "Diverse skin/hair dataset with balanced demographics",
    "created_date": "2025-10-24",
    "last_updated": "2025-10-24",
    "total_images": 5000,
    "annotation_complete": true,
    "quality_score": 0.94
  },

  "dataset_statistics": {
    "total_images": 5000,
    "train_images": 3500,
    "val_images": 750,
    "test_images": 750,
    "splits": {
      "train": {
        "count": 3500,
        "percentage": 70.0
      },
      "val": {
        "count": 750,
        "percentage": 15.0
      },
      "test": {
        "count": 750,
        "percentage": 15.0
      }
    }
  },

  "skin_type_distribution": {
    "total_classes": 5,
    "classes": {
      "normal": {
        "count": 1000,
        "percentage": 20.0,
        "train": 700,
        "val": 150,
        "test": 150
      },
      "dry": {
        "count": 1000,
        "percentage": 20.0,
        "train": 700,
        "val": 150,
        "test": 150
      },
      "oily": {
        "count": 1000,
        "percentage": 20.0,
        "train": 700,
        "val": 150,
        "test": 150
      },
      "combination": {
        "count": 1000,
        "percentage": 20.0,
        "train": 700,
        "val": 150,
        "test": 150
      },
      "sensitive": {
        "count": 1000,
        "percentage": 20.0,
        "train": 700,
        "val": 150,
        "test": 150
      }
    }
  },

  "hair_type_distribution": {
    "total_classes": 4,
    "classes": {
      "straight": {
        "count": 1250,
        "percentage": 25.0,
        "train": 875,
        "val": 188,
        "test": 187
      },
      "wavy": {
        "count": 1250,
        "percentage": 25.0,
        "train": 875,
        "val": 188,
        "test": 187
      },
      "curly": {
        "count": 1250,
        "percentage": 25.0,
        "train": 875,
        "val": 188,
        "test": 187
      },
      "coily": {
        "count": 1250,
        "percentage": 25.0,
        "train": 875,
        "val": 188,
        "test": 187
      }
    }
  },

  "condition_distribution": {
    "total_classes": 9,
    "classes": {
      "no_condition": {
        "count": 3000,
        "percentage": 60.0
      },
      "mild_acne": {
        "count": 1000,
        "percentage": 20.0
      },
      "moderate_acne": {
        "count": 600,
        "percentage": 12.0
      },
      "severe_acne": {
        "count": 200,
        "percentage": 4.0
      },
      "rash": {
        "count": 150,
        "percentage": 3.0
      },
      "eczema": {
        "count": 200,
        "percentage": 4.0
      },
      "infection": {
        "count": 100,
        "percentage": 2.0
      },
      "psoriasis": {
        "count": 50,
        "percentage": 1.0
      },
      "other": {
        "count": 100,
        "percentage": 2.0
      }
    }
  },

  "demographic_distribution": {
    "skin_tone_fitzpatrick": {
      "type_1": {
        "count": 750,
        "percentage": 15.0
      },
      "type_2": {
        "count": 750,
        "percentage": 15.0
      },
      "type_3": {
        "count": 1000,
        "percentage": 20.0
      },
      "type_4": {
        "count": 1000,
        "percentage": 20.0
      },
      "type_5": {
        "count": 750,
        "percentage": 15.0
      },
      "type_6": {
        "count": 750,
        "percentage": 15.0
      }
    },

    "age_groups": {
      "13_18": {
        "count": 500,
        "percentage": 10.0
      },
      "19_25": {
        "count": 750,
        "percentage": 15.0
      },
      "26_35": {
        "count": 1250,
        "percentage": 25.0
      },
      "36_45": {
        "count": 1000,
        "percentage": 20.0
      },
      "46_55": {
        "count": 750,
        "percentage": 15.0
      },
      "56_65": {
        "count": 500,
        "percentage": 10.0
      },
      "65_plus": {
        "count": 250,
        "percentage": 5.0
      }
    },

    "gender": {
      "male": {
        "count": 2000,
        "percentage": 40.0
      },
      "female": {
        "count": 2000,
        "percentage": 40.0
      },
      "non_binary": {
        "count": 500,
        "percentage": 10.0
      },
      "not_disclosed": {
        "count": 500,
        "percentage": 10.0
      }
    },

    "lighting": {
      "natural_daylight": {
        "count": 1500,
        "percentage": 30.0
      },
      "window_indirect": {
        "count": 1250,
        "percentage": 25.0
      },
      "warm_indoor": {
        "count": 1000,
        "percentage": 20.0
      },
      "cool_indoor": {
        "count": 750,
        "percentage": 15.0
      },
      "flash": {
        "count": 500,
        "percentage": 10.0
      }
    },

    "device": {
      "flagship_phone": {
        "count": 1500,
        "percentage": 30.0
      },
      "midrange_phone": {
        "count": 1250,
        "percentage": 25.0
      },
      "budget_phone": {
        "count": 1000,
        "percentage": 20.0
      },
      "professional_camera": {
        "count": 750,
        "percentage": 15.0
      },
      "other": {
        "count": 500,
        "percentage": 10.0
      }
    }
  },

  "quality_metrics": {
    "inter_rater_reliability": {
      "cohens_kappa_skin_type": 0.87,
      "cohens_kappa_hair_type": 0.89,
      "cohens_kappa_conditions": 0.84,
      "overall_agreement": 0.87,
      "status": "APPROVED"
    },

    "image_quality": {
      "excellent": {
        "count": 4200,
        "percentage": 84.0
      },
      "good": {
        "count": 700,
        "percentage": 14.0
      },
      "acceptable": {
        "count": 100,
        "percentage": 2.0
      },
      "poor": {
        "count": 0,
        "percentage": 0.0
      }
    },

    "annotation_status": {
      "fully_annotated": 5000,
      "partially_annotated": 0,
      "unannotated": 0,
      "completion_percentage": 100.0,
      "qa_approved": 4990,
      "qa_approval_percentage": 99.8
    }
  },

  "data_locations": {
    "classification": {
      "base_path": "ml/data/skin_classification",
      "splits": {
        "train": "ml/data/skin_classification/train",
        "val": "ml/data/skin_classification/val",
        "test": "ml/data/skin_classification/test"
      },
      "manifest": "ml/data/skin_classification/split_manifest.json"
    },

    "detection": {
      "base_path": "ml/data/yolo",
      "images": {
        "train": "ml/data/yolo/images/train",
        "val": "ml/data/yolo/images/val",
        "test": "ml/data/yolo/images/test"
      },
      "labels": {
        "train": "ml/data/yolo/labels/train",
        "val": "ml/data/yolo/labels/val",
        "test": "ml/data/yolo/labels/test"
      },
      "config": "ml/data/yolo/data.yaml",
      "manifest": "ml/data/yolo/yolo_manifest.json"
    },

    "metadata": {
      "image_metadata": "ml/data/metadata/image_metadata.csv",
      "consent_log": "ml/data/metadata/consent_log.csv",
      "annotations": "ml/data/metadata/annotations.csv"
    }
  },

  "version_history": [
    {
      "version": "2.1",
      "date": "2025-10-24",
      "changes": [
        "Added 1000 new Type I skin tone images",
        "Re-annotated 200 ambiguous images",
        "Improved inter-rater kappa from 0.84 to 0.87",
        "Fixed 50 mislabeled acne severity"
      ],
      "total_images": 5000,
      "quality_score": 0.94
    },
    {
      "version": "2.0",
      "date": "2025-09-15",
      "changes": [
        "Initial balanced dataset with 5000 images",
        "Complete annotation and QA review"
      ],
      "total_images": 4800,
      "quality_score": 0.91
    }
  ],

  "class_mappings": {
    "skin_type": {
      "0": "normal",
      "1": "dry",
      "2": "oily",
      "3": "combination",
      "4": "sensitive"
    },

    "hair_type": {
      "0": "straight",
      "1": "wavy",
      "2": "curly",
      "3": "coily"
    },

    "conditions": {
      "0": "no_condition",
      "1": "mild_acne",
      "2": "moderate_acne",
      "3": "severe_acne",
      "4": "rash",
      "5": "eczema",
      "6": "infection",
      "7": "psoriasis",
      "8": "other"
    }
  },

  "metadata": {
    "collected_by": "Haski Team",
    "data_protection": "GDPR Compliant",
    "consent_obtained": true,
    "irbapproval": "Protocol #12345",
    "published": false,
    "license": "Proprietary - Internal Use Only",
    "contact": "data-team@haski.com"
  }
}
```

---

## Split-Specific Manifest (`split_manifest.json`)

```json
{
  "split": "train",
  "total_images": 3500,
  "base_path": "ml/data/skin_classification/train",

  "skin_type_classes": {
    "normal": {
      "count": 700,
      "percentage": 20.0,
      "images": ["normal/img_001.jpg", "normal/img_002.jpg", "..."]
    },
    "dry": {
      "count": 700,
      "percentage": 20.0,
      "images": ["dry/img_101.jpg", "dry/img_102.jpg", "..."]
    },
    "oily": {
      "count": 700,
      "percentage": 20.0,
      "images": []
    },
    "combination": {
      "count": 700,
      "percentage": 20.0,
      "images": []
    },
    "sensitive": {
      "count": 700,
      "percentage": 20.0,
      "images": []
    }
  },

  "quality_checks": {
    "all_images_exist": true,
    "no_duplicates": true,
    "valid_image_format": true,
    "acceptable_resolution": true,
    "last_verified": "2025-10-24T10:30:00Z"
  }
}
```

---

## YOLO Detection Manifest (`yolo_manifest.json`)

```json
{
  "dataset_name": "Haski Condition Detection",
  "task": "detection",
  "format": "YOLO",
  "version": "1.0",

  "class_mapping": {
    "0": "acne_mild",
    "1": "acne_moderate",
    "2": "acne_severe",
    "3": "rash",
    "4": "eczema",
    "5": "infection_fungal",
    "6": "infection_bacterial",
    "7": "psoriasis",
    "8": "hair_loss"
  },

  "splits": {
    "train": {
      "image_count": 3500,
      "annotation_count": 8750,
      "avg_objects_per_image": 2.5,
      "path": "ml/data/yolo/images/train",
      "labels_path": "ml/data/yolo/labels/train"
    },
    "val": {
      "image_count": 750,
      "annotation_count": 1875,
      "avg_objects_per_image": 2.5,
      "path": "ml/data/yolo/images/val",
      "labels_path": "ml/data/yolo/labels/val"
    },
    "test": {
      "image_count": 750,
      "annotation_count": 1875,
      "avg_objects_per_image": 2.5,
      "path": "ml/data/yolo/images/test",
      "labels_path": "ml/data/yolo/labels/test"
    }
  },

  "condition_statistics": {
    "acne_mild": {
      "count": 2000,
      "percentage": 22.9,
      "avg_confidence": 0.92
    },
    "acne_moderate": {
      "count": 1500,
      "percentage": 17.1,
      "avg_confidence": 0.88
    },
    "acne_severe": {
      "count": 800,
      "percentage": 9.1,
      "avg_confidence": 0.85
    },
    "rash": {
      "count": 1200,
      "percentage": 13.7,
      "avg_confidence": 0.86
    },
    "eczema": {
      "count": 1300,
      "percentage": 14.9,
      "avg_confidence": 0.87
    },
    "infection_fungal": {
      "count": 600,
      "percentage": 6.9,
      "avg_confidence": 0.83
    },
    "infection_bacterial": {
      "count": 400,
      "percentage": 4.6,
      "avg_confidence": 0.8
    },
    "psoriasis": {
      "count": 300,
      "percentage": 3.4,
      "avg_confidence": 0.81
    },
    "hair_loss": {
      "count": 500,
      "percentage": 5.7,
      "avg_confidence": 0.84
    }
  },

  "data_yaml": {
    "path": "ml/data/yolo/data.yaml",
    "nc": 9,
    "names": [
      "acne_mild",
      "acne_moderate",
      "acne_severe",
      "rash",
      "eczema",
      "infection_fungal",
      "infection_bacterial",
      "psoriasis",
      "hair_loss"
    ]
  },

  "quality_metrics": {
    "label_format_valid": true,
    "all_boxes_normalized": true,
    "no_zero_area_boxes": true,
    "bbox_coverage": {
      "min": 0.001,
      "max": 0.95,
      "mean": 0.08,
      "std": 0.12
    },
    "last_validated": "2025-10-24T10:30:00Z"
  }
}
```

---

## Manifest Generation Script

```python
# ml/data/generate_manifest.py

import json
import os
from pathlib import Path
from collections import defaultdict
from datetime import datetime

def generate_classification_manifest(data_dir="ml/data/skin_classification"):
    """Generate manifest for classification dataset."""

    manifest = {
        "dataset_info": {
            "name": "Haski Skin & Hair Dataset",
            "version": "2.1",
            "description": "Diverse skin/hair dataset with balanced demographics",
            "created_date": datetime.now().isoformat(),
            "last_updated": datetime.now().isoformat(),
            "annotation_complete": True,
            "quality_score": 0.94
        },
        "dataset_statistics": {
            "splits": {}
        },
        "skin_type_distribution": {
            "classes": {}
        }
    }

    # Scan splits (train/val/test)
    total_images = 0
    for split in ["train", "val", "test"]:
        split_dir = Path(data_dir) / split
        if not split_dir.exists():
            continue

        split_count = 0
        split_data = {"classes": {}}

        # Scan classes (normal, dry, oily, etc.)
        for class_dir in split_dir.iterdir():
            if class_dir.is_dir():
                class_name = class_dir.name
                image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
                count = len(image_files)
                split_count += count

                split_data["classes"][class_name] = {
                    "count": count,
                    "images": [f.name for f in image_files[:10]]  # First 10 for sample
                }

                # Update overall distribution
                if class_name not in manifest["skin_type_distribution"]["classes"]:
                    manifest["skin_type_distribution"]["classes"][class_name] = {
                        "count": 0,
                        "train": 0,
                        "val": 0,
                        "test": 0
                    }

                manifest["skin_type_distribution"]["classes"][class_name][split] = count
                manifest["skin_type_distribution"]["classes"][class_name]["count"] += count

        split_data["total"] = split_count
        manifest["dataset_statistics"]["splits"][split] = split_data
        total_images += split_count

    manifest["dataset_statistics"]["total_images"] = total_images

    # Calculate percentages
    for class_name, data in manifest["skin_type_distribution"]["classes"].items():
        data["percentage"] = (data["count"] / total_images * 100) if total_images > 0 else 0

    return manifest


def generate_yolo_manifest(yolo_dir="ml/data/yolo"):
    """Generate manifest for YOLO detection dataset."""

    manifest = {
        "dataset_name": "Haski Condition Detection",
        "task": "detection",
        "format": "YOLO",
        "version": "1.0",
        "splits": {}
    }

    # Scan train/val/test splits
    for split in ["train", "val", "test"]:
        images_dir = Path(yolo_dir) / "images" / split
        labels_dir = Path(yolo_dir) / "labels" / split

        if images_dir.exists() and labels_dir.exists():
            image_files = list(images_dir.glob("*.jpg")) + list(images_dir.glob("*.png"))
            label_files = list(labels_dir.glob("*.txt"))

            manifest["splits"][split] = {
                "image_count": len(image_files),
                "label_count": len(label_files),
                "path": str(images_dir),
                "labels_path": str(labels_dir)
            }

    return manifest


def save_manifest(manifest, output_path):
    """Save manifest to JSON file."""
    with open(output_path, 'w') as f:
        json.dump(manifest, f, indent=2)
    print(f"✅ Manifest saved to {output_path}")


if __name__ == "__main__":
    # Generate and save manifests
    class_manifest = generate_classification_manifest()
    save_manifest(class_manifest, "ml/data/manifest.json")

    yolo_manifest = generate_yolo_manifest()
    save_manifest(yolo_manifest, "ml/data/yolo/yolo_manifest.json")

    print("\n📊 Dataset manifests generated successfully!")
```

---

## Loading Manifest in Python

```python
import json
from pathlib import Path

def load_manifest(manifest_path="ml/data/manifest.json"):
    """Load manifest from JSON file."""
    with open(manifest_path, 'r') as f:
        manifest = json.load(f)
    return manifest


def get_class_distribution(manifest):
    """Extract class distribution from manifest."""
    distribution = manifest["skin_type_distribution"]["classes"]
    for class_name, data in distribution.items():
        print(f"{class_name}: {data['count']} images ({data['percentage']:.1f}%)")


def get_split_sizes(manifest):
    """Get train/val/test split sizes."""
    splits = manifest["dataset_statistics"]["splits"]
    total = manifest["dataset_statistics"]["total_images"]

    for split, data in splits.items():
        count = data["total"]
        pct = (count / total * 100)
        print(f"{split}: {count} images ({pct:.1f}%)")


def verify_dataset_integrity(manifest):
    """Verify dataset quality metrics."""
    quality = manifest["quality_metrics"]

    print("Quality Metrics:")
    print(f"  Inter-rater Kappa: {quality['inter_rater_reliability']['cohens_kappa_skin_type']:.3f}")
    print(f"  QA Approval: {quality['annotation_status']['qa_approval_percentage']:.1f}%")
    print(f"  Annotation Complete: {quality['annotation_status']['completion_percentage']:.1f}%")


# Usage
if __name__ == "__main__":
    manifest = load_manifest()

    print("=== Dataset Overview ===")
    print(f"Total images: {manifest['dataset_statistics']['total_images']}")

    print("\n=== Split Distribution ===")
    get_split_sizes(manifest)

    print("\n=== Class Distribution ===")
    get_class_distribution(manifest)

    print("\n=== Quality Checks ===")
    verify_dataset_integrity(manifest)
```

---

## YOLO Label Format

Each image in YOLO format has a corresponding `.txt` file with one line per object:

```
# Example: img_001.txt
0 0.5 0.5 0.3 0.4    # class center_x center_y width height (normalized 0-1)
2 0.2 0.3 0.1 0.2    # another condition on same image
4 0.7 0.8 0.15 0.2   # third condition

# Class mapping:
# 0 = acne_mild
# 1 = acne_moderate
# 2 = acne_severe
# 3 = rash
# 4 = eczema
# 5 = infection_fungal
# 6 = infection_bacterial
# 7 = psoriasis
# 8 = hair_loss
```

---

## Manifest Validation

```python
import json

def validate_manifest(manifest_path):
    """Validate manifest structure and data integrity."""

    with open(manifest_path, 'r') as f:
        manifest = json.load(f)

    errors = []
    warnings = []

    # Check required fields
    required_fields = ["dataset_info", "dataset_statistics", "quality_metrics"]
    for field in required_fields:
        if field not in manifest:
            errors.append(f"Missing required field: {field}")

    # Verify split percentages sum to 100%
    if "splits" in manifest.get("dataset_statistics", {}):
        splits = manifest["dataset_statistics"]["splits"]
        total = manifest["dataset_statistics"].get("total_images", 1)

        split_sum = sum([s.get("total", 0) for s in splits.values()])
        if split_sum != total:
            warnings.append(f"Split totals ({split_sum}) don't match total images ({total})")

    # Check quality metrics
    quality = manifest.get("quality_metrics", {})
    if quality.get("inter_rater_reliability", {}).get("cohens_kappa_skin_type", 0) < 0.70:
        warnings.append("Low inter-rater reliability (kappa < 0.70)")

    # Check annotation completion
    completion = quality.get("annotation_status", {}).get("completion_percentage", 0)
    if completion < 100:
        warnings.append(f"Dataset not fully annotated: {completion:.1f}%")

    # Report results
    print("✅ Validation Results")
    print("=" * 50)

    if errors:
        print(f"\n❌ ERRORS ({len(errors)}):")
        for err in errors:
            print(f"  - {err}")
    else:
        print("\n✅ No errors found")

    if warnings:
        print(f"\n⚠️  WARNINGS ({len(warnings)}):")
        for warn in warnings:
            print(f"  - {warn}")
    else:
        print("\n✅ No warnings")

    return len(errors) == 0


# Usage
if __name__ == "__main__":
    is_valid = validate_manifest("ml/data/manifest.json")
    print(f"\nManifest valid: {is_valid}")
```

---

## Checklist for Dataset Artifacts

✅ **Master Manifest**

```
ml/data/manifest.json - Complete dataset overview
  ✓ Dataset statistics (total, train/val/test counts)
  ✓ Class distributions (skin type, hair type, conditions)
  ✓ Demographic breakdown (Fitzpatrick, age, gender, lighting, device)
  ✓ Quality metrics (inter-rater kappa, approval percentage)
  ✓ Version history and changelog
```

✅ **Classification Dataset**

```
ml/data/skin_classification/
  ✓ train/normal/, train/dry/, ... (ImageFolder format)
  ✓ val/normal/, val/dry/, ... (same structure)
  ✓ test/normal/, test/dry/, ... (same structure)
  ✓ split_manifest.json (per-split metadata)
```

✅ **Detection Dataset (YOLO)**

```
ml/data/yolo/
  ✓ images/train/, images/val/, images/test/
  ✓ labels/train/*.txt, labels/val/*.txt, labels/test/*.txt
  ✓ data.yaml (class mapping and paths)
  ✓ yolo_manifest.json (detection-specific metadata)
```

✅ **Metadata**

```
ml/data/metadata/
  ✓ image_metadata.csv (per-image demographics)
  ✓ consent_log.csv (consent tracking)
  ✓ annotations.csv (label details and confidence)
```

✅ **Version Control**

```
ml/data/versions/
  ✓ v1.0_manifest.json, v1.1_manifest.json, ...
  ✓ CHANGELOG.md (version history and changes)
```

---

## Summary

The manifest system provides:

- **Transparency**: Complete dataset statistics and composition
- **Traceability**: Version history and change tracking
- **Quality assurance**: Inter-rater reliability and annotation metrics
- **Reproducibility**: Exact class distributions and split definitions
- **Integration**: Easy loading into training pipelines

Use `generate_manifest.py` to auto-create manifests from your dataset directory!
