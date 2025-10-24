#!/usr/bin/env python3
"""
Example: Prepare datasets for Haski ML training

This script demonstrates how to use prepare_dataset.py for both
classification and detection tasks.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a shell command and print output."""
    print(f"\n{'='*60}")
    print(f"Running: {description}")
    print(f"{'='*60}")
    print(f"Command: {' '.join(cmd)}\n")
    
    result = subprocess.run(cmd, cwd=str(Path(__file__).parent))
    
    if result.returncode != 0:
        print(f"Error running {description}")
        return False
    return True


def example_classification():
    """Example: Prepare classification dataset."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Classification Dataset (Skin Type)")
    print("="*60)
    
    # Prepare skin type dataset
    cmd = [
        sys.executable,
        "prepare_dataset.py",
        "--task", "classification",
        "--source", "/path/to/skin_type_images",
        "--output", "../../datasets/skin_type",
        "--config", "config_classification.yaml",
        # "--symlink"  # Uncomment to use symlinks
    ]
    
    print("\nUsage:")
    print(f"  {' '.join(cmd)}")
    print("\nThis will:")
    print("  1. Create train/val/test directories")
    print("  2. Create subdirectories for each class (normal, dry, oily, etc.)")
    print("  3. Copy/link images from source to appropriate directories")
    print("  4. Validate all images")
    print("  5. Generate manifest.json with statistics")
    
    print("\nExpected output structure:")
    print("""
datasets/
└── skin_type/
    ├── train/
    │   ├── normal/
    │   ├── dry/
    │   ├── oily/
    │   ├── combination/
    │   └── sensitive/
    ├── val/
    ├── test/
    └── manifest.json
    """)


def example_detection():
    """Example: Prepare detection dataset."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Detection Dataset (Conditions)")
    print("="*60)
    
    cmd = [
        sys.executable,
        "prepare_dataset.py",
        "--task", "detection",
        "--source", "/path/to/condition_images",
        "--labels", "/path/to/condition_labels",
        "--output", "../../datasets/conditions",
        "--config", "config_detection.yaml"
    ]
    
    print("\nUsage:")
    print(f"  {' '.join(cmd)}")
    print("\nThis will:")
    print("  1. Create images/train, images/val, images/test directories")
    print("  2. Create labels/train, labels/val, labels/test directories")
    print("  3. Copy/link images and YOLO labels")
    print("  4. Validate YOLO label format")
    print("  5. Generate data.yaml for YOLOv5/v8 training")
    print("  6. Generate manifest.json with statistics")
    
    print("\nExpected output structure:")
    print("""
datasets/
└── conditions/
    ├── images/
    │   ├── train/
    │   ├── val/
    │   └── test/
    ├── labels/
    │   ├── train/
    │   ├── val/
    │   └── test/
    ├── data.yaml
    └── manifest.json
    """)
    
    print("\nYOLO Label Format:")
    print("""
  Each image has a corresponding .txt file with:
  class_id center_x center_y width height
  
  Example: img_001.txt
    0 0.5 0.5 0.3 0.4    # acne at center
    2 0.2 0.3 0.1 0.2    # psoriasis top-left
    
  All coordinates are normalized to 0-1 range
    """)


def example_coco_to_yolo():
    """Example: Convert COCO format to YOLO."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Convert COCO JSON to YOLO Format")
    print("="*60)
    
    code = '''
import json
from pathlib import Path

def coco_to_yolo(coco_json_path, images_dir, output_labels_dir):
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
        image_stem = Path(image_info['file_name']).stem
        label_file = Path(output_labels_dir) / f"{image_stem}.txt"
        
        with open(label_file, 'a') as f:
            f.write(f"{class_id} {x_center:.6f} {y_center:.6f} {width:.6f} {height:.6f}\\n")

# Usage:
coco_to_yolo(
    "annotations.json",
    "images/train",
    "labels/train"
)
    '''
    
    print("\nRun this code to convert COCO format to YOLO:")
    print(code)


def example_symlink():
    """Example: Use symlinks for large datasets."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Large Dataset with Symlinks")
    print("="*60)
    
    cmd = [
        sys.executable,
        "prepare_dataset.py",
        "--task", "classification",
        "--source", "/mnt/external_drive/huge_dataset",
        "--output", "../../datasets/skin_type_large",
        "--config", "config_classification.yaml",
        "--symlink"
    ]
    
    print("\nFor large datasets (>100GB), use symlinks to save disk space:")
    print(f"  {' '.join(cmd)}")
    print("\nBenefits of symlinks:")
    print("  - Saves disk space (no file duplication)")
    print("  - Faster preparation (instant linking)")
    print("  - Transparent to training code")
    print("\nNote: Use --symlink flag to enable")


def main():
    print("""
╔═══════════════════════════════════════════════════════════════╗
║       Haski ML Dataset Preparation Examples                   ║
╚═══════════════════════════════════════════════════════════════╝
    """)
    
    example_classification()
    print("\n" + "-"*60)
    
    example_detection()
    print("\n" + "-"*60)
    
    example_coco_to_yolo()
    print("\n" + "-"*60)
    
    example_symlink()
    print("\n" + "-"*60)
    
    print("\n" + "="*60)
    print("QUICK START CHECKLIST")
    print("="*60)
    print("""
1. Install dependencies:
   pip install pillow pyyaml

2. Prepare your source data directory structure

3. Choose your task:
   - Classification: organized by class subdirectories
   - Detection: images in one folder, labels in another

4. Run the prepare script:
   python prepare_dataset.py --task <classification|detection> \\
     --source <source_dir> --output <output_dir> \\
     --config config_*.yaml

5. Check the output:
   - Verify directory structure
   - Review manifest.json for statistics
   - Spot-check a few samples

6. Train your model:
   - Classification: Use pytorch ImageFolder loader
   - Detection: Use YOLO with generated data.yaml

For detailed help:
  python prepare_dataset.py --help

For usage guide:
  cat USAGE.md
    """)


if __name__ == '__main__':
    main()
