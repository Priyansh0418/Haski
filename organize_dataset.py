#!/usr/bin/env python3
"""
Organize Raw Dataset and Prepare for Training

Converts unstructured raw data into train/val/test splits
ready for the Haski ML training pipeline.
"""

import os
import shutil
from pathlib import Path
from collections import defaultdict
import json
import random
from PIL import Image

# Set seed for reproducibility
random.seed(42)


def organize_dataset():
    """Organize raw dataset into train/val/test structure."""
    
    raw_dir = Path("ml/data/raw")
    training_dir = Path("ml/data/training")
    
    print("=" * 70)
    print("DATASET ORGANIZATION SCRIPT")
    print("=" * 70)
    print()
    
    # Create output directories
    training_dir.mkdir(parents=True, exist_ok=True)
    
    # Scan raw directory
    print("📊 Scanning raw dataset...")
    print()
    
    image_stats = defaultdict(lambda: {"total": 0, "valid": 0, "invalid": 0})
    class_mapping = {
        "skin": {},
        "hairtype": {},
        "hairfall": {}
    }
    
    # Process each category
    categories = ["skin", "hairtype", "hairfall"]
    
    for category in categories:
        category_path = raw_dir / category
        if not category_path.exists():
            continue
            
        print(f"Processing {category.upper()}...")
        
        # Get all classes in this category
        class_dirs = [d for d in category_path.rglob("*") if d.is_dir()]
        
        for class_dir in class_dirs:
            # Skip intermediate 'data' directories
            if class_dir.name == "data":
                continue
                
            class_name = class_dir.name
            image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
            
            if image_files:
                image_stats[class_name]["total"] = len(image_files)
                print(f"  ✓ {class_name}: {len(image_files)} images")
                
                # Try to validate images
                valid_count = 0
                for img_path in image_files:
                    try:
                        img = Image.open(img_path)
                        img.verify()
                        valid_count += 1
                    except:
                        pass
                
                image_stats[class_name]["valid"] = valid_count
                image_stats[class_name]["invalid"] = len(image_files) - valid_count
                
                if category not in class_mapping:
                    class_mapping[category] = {}
                class_mapping[category][class_name] = len(image_files)
    
    print()
    print("=" * 70)
    print("DATASET SUMMARY")
    print("=" * 70)
    print()
    
    total_images = sum(stats["total"] for stats in image_stats.values())
    total_valid = sum(stats["valid"] for stats in image_stats.values())
    
    print(f"Total Images Found: {total_images}")
    print(f"Valid Images: {total_valid}")
    print(f"Invalid/Corrupt: {total_images - total_valid}")
    print()
    
    print("Classes Found:")
    for category, classes in class_mapping.items():
        if classes:
            print(f"\n  {category.upper()}:")
            for class_name, count in sorted(classes.items(), key=lambda x: x[1], reverse=True):
                print(f"    • {class_name}: {count} images")
    
    print()
    print("=" * 70)
    print("CREATING TRAIN/VAL/TEST SPLITS")
    print("=" * 70)
    print()
    
    # Create train/val/test split
    for category in categories:
        category_path = raw_dir / category
        if not category_path.exists():
            continue
        
        # Get all leaf directories containing images
        image_classes = {}
        for class_dir in category_path.rglob("*"):
            if class_dir.is_dir():
                image_files = list(class_dir.glob("*.jpg")) + list(class_dir.glob("*.png"))
                if image_files:
                    image_classes[class_dir.name] = (class_dir, image_files)
        
        # Create train/val/test directories
        for split in ["train", "val", "test"]:
            split_dir = training_dir / split
            split_dir.mkdir(parents=True, exist_ok=True)
        
        # Organize images
        for class_name, (class_dir, image_files) in image_classes.items():
            print(f"Processing {category}/{class_name}...")
            
            # Shuffle images
            shuffled_images = image_files.copy()
            random.shuffle(shuffled_images)
            
            # Calculate split indices (70% train, 15% val, 15% test)
            train_idx = int(len(shuffled_images) * 0.7)
            val_idx = int(len(shuffled_images) * 0.85)
            
            train_images = shuffled_images[:train_idx]
            val_images = shuffled_images[train_idx:val_idx]
            test_images = shuffled_images[val_idx:]
            
            # Copy images to train/val/test directories
            for img_path in train_images:
                dest_dir = training_dir / "train" / class_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(img_path, dest_dir / img_path.name)
                except:
                    pass
            
            for img_path in val_images:
                dest_dir = training_dir / "val" / class_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(img_path, dest_dir / img_path.name)
                except:
                    pass
            
            for img_path in test_images:
                dest_dir = training_dir / "test" / class_name
                dest_dir.mkdir(parents=True, exist_ok=True)
                try:
                    shutil.copy2(img_path, dest_dir / img_path.name)
                except:
                    pass
            
            print(f"  ✓ {class_name}: {len(train_images)} train, {len(val_images)} val, {len(test_images)} test")
    
    print()
    print("=" * 70)
    print("VERIFICATION")
    print("=" * 70)
    print()
    
    # Verify splits
    for split in ["train", "val", "test"]:
        split_dir = training_dir / split
        if split_dir.exists():
            total_in_split = sum(1 for _ in split_dir.rglob("*.jpg")) + sum(1 for _ in split_dir.rglob("*.png"))
            classes_in_split = len([d for d in split_dir.iterdir() if d.is_dir()])
            print(f"{split.upper():6} split: {total_in_split:4} images across {classes_in_split} classes")
    
    print()
    print("=" * 70)
    print("✅ DATASET ORGANIZATION COMPLETE!")
    print("=" * 70)
    print()
    print(f"Organized data location: {training_dir}")
    print()
    print("Next steps:")
    print("  1. python ml/data/generate_manifest.py --data-dir ml/data/training")
    print("  2. make train-classifier EPOCHS=50")
    print()


if __name__ == "__main__":
    organize_dataset()
