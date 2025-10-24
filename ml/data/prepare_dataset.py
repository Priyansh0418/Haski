"""
Dataset Preparation Script for Haski ML Training

This script organizes images into classification or detection datasets with validation.

Supports:
- Classification: ImageFolder structure (train/val/test/{class_name}/*.jpg)
- Detection: YOLO format (images/ and labels/ with normalized coordinates)

Usage:
    # Classification dataset
    python prepare_dataset.py \
      --task classification \
      --source /path/to/source/images \
      --output ml/data/skin_hair \
      --config config_classification.yaml

    # Detection dataset
    python prepare_dataset.py \
      --task detection \
      --source /path/to/source/images \
      --labels /path/to/labels \
      --output ml/data/detection \
      --config config_detection.yaml
"""

import os
import json
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple
import yaml
from PIL import Image
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class ClassificationDatasetPreparer:
    """Prepare classification datasets in ImageFolder structure."""

    def __init__(self, output_dir: str, symlink: bool = False):
        """
        Initialize preparer.
        
        Args:
            output_dir: Root output directory for dataset
            symlink: If True, create symlinks instead of copying files
        """
        self.output_dir = Path(output_dir)
        self.symlink = symlink
        self.manifest = {
            "task": "classification",
            "structure": "imagefolder",
            "splits": {},
            "class_counts": {},
            "total_images": 0
        }

    def setup_structure(self, splits: List[str] = None, classes: List[str] = None):
        """
        Create directory structure for classification dataset.
        
        Args:
            splits: List of splits (e.g., ['train', 'val', 'test'])
            classes: List of class names (e.g., ['normal', 'dry', 'oily'])
        """
        if splits is None:
            splits = ['train', 'val', 'test']
        if classes is None:
            classes = []

        self.output_dir.mkdir(parents=True, exist_ok=True)

        for split in splits:
            split_dir = self.output_dir / split
            split_dir.mkdir(exist_ok=True)
            
            for cls in classes:
                cls_dir = split_dir / cls
                cls_dir.mkdir(exist_ok=True)
                logger.info(f"Created: {cls_dir}")

        self.manifest["splits"] = {split: [] for split in splits}
        self.manifest["class_counts"] = {cls: 0 for cls in classes}

    def validate_image(self, image_path: Path) -> Tuple[bool, str]:
        """
        Validate image file.
        
        Args:
            image_path: Path to image file
            
        Returns:
            Tuple of (is_valid, message)
        """
        try:
            if not image_path.exists():
                return False, f"File not found: {image_path}"
            
            with Image.open(image_path) as img:
                img.verify()
            return True, "Valid"
        except Exception as e:
            return False, f"Invalid image: {str(e)}"

    def copy_or_link_image(self, source_path: Path, dest_path: Path):
        """
        Copy or symlink image from source to destination.
        
        Args:
            source_path: Source image path
            dest_path: Destination path
        """
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        
        if self.symlink:
            # Create symlink
            if dest_path.exists() or dest_path.is_symlink():
                dest_path.unlink()
            dest_path.symlink_to(source_path.resolve())
            logger.debug(f"Symlinked: {source_path} -> {dest_path}")
        else:
            # Copy file
            shutil.copy2(source_path, dest_path)
            logger.debug(f"Copied: {source_path} -> {dest_path}")

    def add_images_from_directory(self, source_dir: Path, split: str, class_name: str):
        """
        Add images from source directory to dataset.
        
        Args:
            source_dir: Source directory containing images
            split: Dataset split (train/val/test)
            class_name: Class label
            
        Returns:
            Number of images added
        """
        source_dir = Path(source_dir)
        dest_dir = self.output_dir / split / class_name
        dest_dir.mkdir(parents=True, exist_ok=True)

        images_added = 0
        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

        for image_file in sorted(source_dir.iterdir()):
            if image_file.suffix.lower() not in valid_extensions:
                continue

            # Validate image
            is_valid, msg = self.validate_image(image_file)
            if not is_valid:
                logger.warning(f"Skipping {image_file}: {msg}")
                continue

            # Copy or link
            dest_path = dest_dir / image_file.name
            try:
                self.copy_or_link_image(image_file, dest_path)
                images_added += 1
                self.manifest["class_counts"][class_name] += 1
                self.manifest["total_images"] += 1
            except Exception as e:
                logger.error(f"Failed to process {image_file}: {e}")

        logger.info(f"Added {images_added} images to {split}/{class_name}")
        return images_added

    def get_summary(self) -> str:
        """Get summary of dataset statistics."""
        summary = "Classification Dataset Summary\n"
        summary += "=" * 50 + "\n"
        summary += f"Total images: {self.manifest['total_images']}\n\n"
        
        summary += "Class distribution:\n"
        for cls, count in self.manifest['class_counts'].items():
            pct = (count / self.manifest['total_images'] * 100) if self.manifest['total_images'] > 0 else 0
            summary += f"  {cls:20s}: {count:5d} ({pct:5.1f}%)\n"
        
        return summary

    def save_manifest(self, output_path: str = None):
        """Save dataset manifest to JSON."""
        if output_path is None:
            output_path = self.output_dir.parent / "manifest.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        logger.info(f"Saved manifest to {output_path}")


class DetectionDatasetPreparer:
    """Prepare detection datasets in YOLO format."""

    def __init__(self, output_dir: str, symlink: bool = False):
        """
        Initialize detection dataset preparer.
        
        Args:
            output_dir: Root output directory
            symlink: If True, create symlinks instead of copying
        """
        self.output_dir = Path(output_dir)
        self.symlink = symlink
        self.manifest = {
            "task": "detection",
            "format": "yolo",
            "splits": {},
            "class_names": {},
            "class_counts": {},
            "total_images": 0,
            "images_without_labels": []
        }

    def setup_structure(self, splits: List[str] = None):
        """Create YOLO dataset directory structure."""
        if splits is None:
            splits = ['train', 'val', 'test']

        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        for split in splits:
            images_dir = self.output_dir / "images" / split
            labels_dir = self.output_dir / "labels" / split
            
            images_dir.mkdir(parents=True, exist_ok=True)
            labels_dir.mkdir(parents=True, exist_ok=True)
            
            self.manifest["splits"][split] = {
                "images": str(images_dir),
                "labels": str(labels_dir),
                "count": 0
            }
            
            logger.info(f"Created: {images_dir}")
            logger.info(f"Created: {labels_dir}")

    def validate_image(self, image_path: Path) -> Tuple[bool, str]:
        """Validate image file."""
        try:
            if not image_path.exists():
                return False, f"File not found: {image_path}"
            
            with Image.open(image_path) as img:
                img.verify()
                width, height = img.size
            return True, f"Valid ({width}x{height})"
        except Exception as e:
            return False, f"Invalid: {str(e)}"

    def validate_yolo_label(self, label_path: Path) -> Tuple[bool, List[str]]:
        """
        Validate YOLO format label file.
        
        Args:
            label_path: Path to .txt label file
            
        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []
        
        if not label_path.exists():
            return False, ["Label file not found"]
        
        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()
            
            if not lines:
                errors.append("Empty label file")
                return False, errors
            
            for idx, line in enumerate(lines):
                parts = line.strip().split()
                if len(parts) != 5:
                    errors.append(f"Line {idx+1}: Expected 5 values, got {len(parts)}")
                    continue
                
                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])
                    
                    # Validate ranges (normalized 0-1)
                    for val, name in [(x_center, 'x_center'), (y_center, 'y_center'),
                                      (width, 'width'), (height, 'height')]:
                        if not (0 <= val <= 1):
                            errors.append(f"Line {idx+1}: {name}={val} out of range [0,1]")
                except ValueError as e:
                    errors.append(f"Line {idx+1}: Invalid values - {e}")
            
            return len(errors) == 0, errors
        except Exception as e:
            return False, [f"Error reading file: {str(e)}"]

    def add_detection_images(self, images_dir: Path, labels_dir: Path, split: str, class_names: Dict[int, str]):
        """
        Add detection images and labels to dataset.
        
        Args:
            images_dir: Source images directory
            labels_dir: Source labels directory
            split: Dataset split (train/val/test)
            class_names: Mapping of class_id to class_name
        """
        images_dir = Path(images_dir)
        labels_dir = Path(labels_dir)
        
        dest_images = self.output_dir / "images" / split
        dest_labels = self.output_dir / "labels" / split
        
        dest_images.mkdir(parents=True, exist_ok=True)
        dest_labels.mkdir(parents=True, exist_ok=True)

        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}
        images_added = 0
        images_skipped = 0

        for image_file in sorted(images_dir.iterdir()):
            if image_file.suffix.lower() not in valid_extensions:
                continue

            # Validate image
            is_valid, msg = self.validate_image(image_file)
            if not is_valid:
                logger.warning(f"Skipping {image_file}: {msg}")
                images_skipped += 1
                continue

            # Check for corresponding label
            label_file = labels_dir / (image_file.stem + ".txt")
            is_valid_label, label_errors = self.validate_yolo_label(label_file)
            
            if not is_valid_label:
                logger.warning(f"Skipping {image_file}: {', '.join(label_errors)}")
                self.manifest["images_without_labels"].append(str(image_file))
                images_skipped += 1
                continue

            # Copy/link image and label
            try:
                dest_image = dest_images / image_file.name
                dest_label = dest_labels / label_file.name
                
                if self.symlink:
                    if dest_image.exists() or dest_image.is_symlink():
                        dest_image.unlink()
                    if dest_label.exists() or dest_label.is_symlink():
                        dest_label.unlink()
                    dest_image.symlink_to(image_file.resolve())
                    dest_label.symlink_to(label_file.resolve())
                else:
                    shutil.copy2(image_file, dest_image)
                    shutil.copy2(label_file, dest_label)
                
                # Count classes
                with open(label_file, 'r') as f:
                    for line in f:
                        class_id = int(line.split()[0])
                        if class_id not in self.manifest["class_counts"]:
                            self.manifest["class_counts"][class_id] = 0
                        self.manifest["class_counts"][class_id] += 1
                
                images_added += 1
                self.manifest["total_images"] += 1
                
            except Exception as e:
                logger.error(f"Failed to process {image_file}: {e}")
                images_skipped += 1

        self.manifest["splits"][split]["count"] = images_added
        self.manifest["class_names"] = class_names
        
        logger.info(f"Added {images_added} images to {split}")
        if images_skipped > 0:
            logger.warning(f"Skipped {images_skipped} images")

    def create_yolo_config(self, output_path: str = None):
        """Create YOLO data.yaml configuration file."""
        if output_path is None:
            output_path = self.output_dir / "data.yaml"
        
        output_path = Path(output_path)
        
        config = {
            'path': str(self.output_dir.resolve()),
            'train': 'images/train',
            'val': 'images/val',
            'test': 'images/test',
            'nc': len(self.manifest['class_names']),
            'names': self.manifest['class_names']
        }
        
        with open(output_path, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)
        
        logger.info(f"Created YOLO config: {output_path}")

    def get_summary(self) -> str:
        """Get summary of detection dataset."""
        summary = "Detection Dataset Summary (YOLO Format)\n"
        summary += "=" * 50 + "\n"
        summary += f"Total images: {self.manifest['total_images']}\n\n"
        
        summary += "Images per split:\n"
        for split, info in self.manifest['splits'].items():
            summary += f"  {split:10s}: {info['count']:5d}\n"
        
        summary += "\nClass distribution:\n"
        for class_id, class_name in self.manifest['class_names'].items():
            count = self.manifest['class_counts'].get(class_id, 0)
            summary += f"  {class_id}: {class_name:20s}: {count:5d} annotations\n"
        
        if self.manifest['images_without_labels']:
            summary += f"\nImages without labels: {len(self.manifest['images_without_labels'])}\n"
        
        return summary

    def save_manifest(self, output_path: str = None):
        """Save dataset manifest to JSON."""
        if output_path is None:
            output_path = self.output_dir.parent / "manifest.json"
        
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w') as f:
            json.dump(self.manifest, f, indent=2)
        
        logger.info(f"Saved manifest to {output_path}")


def load_config(config_path: str) -> dict:
    """Load configuration from YAML file."""
    if not config_path:
        return {}
    
    with open(config_path, 'r') as f:
        return yaml.safe_load(f) or {}


def main():
    parser = argparse.ArgumentParser(
        description='Prepare classification or detection datasets for Haski ML'
    )
    
    parser.add_argument(
        '--task',
        type=str,
        choices=['classification', 'detection'],
        required=True,
        help='Dataset task type'
    )
    parser.add_argument(
        '--source',
        type=str,
        required=True,
        help='Source directory containing images'
    )
    parser.add_argument(
        '--labels',
        type=str,
        help='Source directory containing YOLO labels (detection only)'
    )
    parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for prepared dataset'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='YAML configuration file'
    )
    parser.add_argument(
        '--symlink',
        action='store_true',
        help='Create symlinks instead of copying files'
    )
    parser.add_argument(
        '--manifest',
        type=str,
        help='Output path for manifest.json'
    )
    
    args = parser.parse_args()
    
    # Load config
    config = load_config(args.config) if args.config else {}
    logger.info(f"Configuration: {config}")
    
    if args.task == 'classification':
        logger.info("Preparing classification dataset...")
        preparer = ClassificationDatasetPreparer(args.output, symlink=args.symlink)
        
        # Get class names and splits from config or defaults
        classes = config.get('classes', ['normal', 'dry', 'oily', 'combination', 'sensitive'])
        splits = config.get('splits', ['train', 'val', 'test'])
        
        preparer.setup_structure(splits=splits, classes=classes)
        
        # Add images from source directory (assuming class directories exist)
        source_dir = Path(args.source)
        for split in splits:
            split_source = source_dir / split
            if split_source.exists():
                for class_dir in split_source.iterdir():
                    if class_dir.is_dir() and class_dir.name in classes:
                        preparer.add_images_from_directory(
                            class_dir,
                            split=split,
                            class_name=class_dir.name
                        )
        
        # Print summary
        print("\n" + preparer.get_summary())
        
        # Save manifest
        preparer.save_manifest(args.manifest)
    
    else:  # detection
        logger.info("Preparing detection dataset (YOLO format)...")
        preparer = DetectionDatasetPreparer(args.output, symlink=args.symlink)
        
        # Get class names from config
        class_names = config.get('class_names', {
            0: 'acne',
            1: 'eczema',
            2: 'psoriasis',
            3: 'dandruff',
            4: 'rosacea',
            5: 'hair_loss'
        })
        splits = config.get('splits', ['train', 'val', 'test'])
        
        preparer.setup_structure(splits=splits)
        
        # Add images and labels from source directories
        source_dir = Path(args.source)
        labels_dir = Path(args.labels) if args.labels else source_dir.parent / 'labels'
        
        for split in splits:
            split_images = source_dir / split
            split_labels = labels_dir / split
            
            if split_images.exists() and split_labels.exists():
                preparer.add_detection_images(
                    split_images,
                    split_labels,
                    split=split,
                    class_names=class_names
                )
        
        # Create YOLO config
        preparer.create_yolo_config()
        
        # Print summary
        print("\n" + preparer.get_summary())
        
        # Save manifest
        preparer.save_manifest(args.manifest)


if __name__ == '__main__':
    main()
