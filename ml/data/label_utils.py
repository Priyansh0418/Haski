"""
Label Format Conversion Utilities for Haski ML

Supports conversion between annotation formats:
- Pascal VOC XML format
- COCO JSON format
- YOLO TXT format

Usage:
    # Convert Pascal VOC to YOLO
    python label_utils.py convert-voc --input annotations/ --output labels/ --images images/

    # Convert COCO to YOLO
    python label_utils.py convert-coco --input annotations.json --output labels/ --images images/

    # Validate YOLO labels
    python label_utils.py validate --images images/ --labels labels/

    # Validate COCO format
    python label_utils.py validate-coco --annotations annotations.json --images images/
"""

import json
import os
import sys
import shutil
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import xml.etree.ElementTree as ET
import logging

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class VOCtoYOLOConverter:
    """Convert Pascal VOC XML annotations to YOLO format."""

    @staticmethod
    def parse_xml(xml_path: str) -> Tuple[int, int, List[Dict]]:
        """
        Parse Pascal VOC XML file.

        Args:
            xml_path: Path to XML annotation file

        Returns:
            Tuple of (width, height, objects)
            where objects is list of dicts with 'name', 'xmin', 'ymin', 'xmax', 'ymax'
        """
        try:
            tree = ET.parse(xml_path)
            root = tree.getroot()

            # Get image dimensions
            size = root.find('size')
            if size is None:
                raise ValueError("Size element not found in XML")

            width = int(size.find('width').text)
            height = int(size.find('height').text)

            # Parse objects
            objects = []
            for obj in root.findall('object'):
                name = obj.find('name').text
                bndbox = obj.find('bndbox')

                xmin = float(bndbox.find('xmin').text)
                ymin = float(bndbox.find('ymin').text)
                xmax = float(bndbox.find('xmax').text)
                ymax = float(bndbox.find('ymax').text)

                objects.append({
                    'name': name,
                    'xmin': xmin,
                    'ymin': ymin,
                    'xmax': xmax,
                    'ymax': ymax
                })

            return width, height, objects

        except Exception as e:
            logger.error(f"Error parsing {xml_path}: {e}")
            raise

    @staticmethod
    def convert_pascal_voc_to_yolo(
        xml_path: str,
        img_width: int,
        img_height: int,
        class_mapping: Optional[Dict[str, int]] = None
    ) -> str:
        """
        Convert Pascal VOC XML annotation to YOLO format.

        Args:
            xml_path: Path to Pascal VOC XML file
            img_width: Image width (pixels)
            img_height: Image height (pixels)
            class_mapping: Optional dict mapping class names to IDs

        Returns:
            YOLO format string (multiple lines, one per object)

        Raises:
            ValueError: If required elements are missing
        """
        width, height, objects = VOCtoYOLOConverter.parse_xml(xml_path)

        if width != img_width or height != img_height:
            logger.warning(
                f"Size mismatch in {xml_path}: "
                f"XML says {width}x{height}, "
                f"provided {img_width}x{img_height}"
            )

        yolo_lines = []

        for obj in objects:
            class_name = obj['name']
            xmin = obj['xmin']
            ymin = obj['ymin']
            xmax = obj['xmax']
            ymax = obj['ymax']

            # Convert to YOLO format
            x_center = (xmin + xmax) / 2 / img_width
            y_center = (ymin + ymax) / 2 / img_height
            width_norm = (xmax - xmin) / img_width
            height_norm = (ymax - ymin) / img_height

            # Validate normalized coordinates
            for val, name in [(x_center, 'x_center'), (y_center, 'y_center'),
                              (width_norm, 'width'), (height_norm, 'height')]:
                if not (0 <= val <= 1):
                    logger.warning(
                        f"Out of range: {name}={val} in {xml_path}"
                    )

            # Get class ID
            if class_mapping is None:
                class_id = 0
            else:
                if class_name not in class_mapping:
                    logger.warning(
                        f"Unknown class '{class_name}' in {xml_path}, "
                        f"mapping to 0"
                    )
                    class_id = 0
                else:
                    class_id = class_mapping[class_name]

            yolo_line = f"{class_id} {x_center:.6f} {y_center:.6f} {width_norm:.6f} {height_norm:.6f}"
            yolo_lines.append(yolo_line)

        return '\n'.join(yolo_lines)

    @staticmethod
    def batch_convert(
        xml_dir: str,
        output_dir: str,
        images_dir: Optional[str] = None,
        class_mapping: Optional[Dict[str, int]] = None,
        copy_images: bool = False
    ) -> Tuple[int, int]:
        """
        Batch convert Pascal VOC XML files to YOLO format.

        Args:
            xml_dir: Directory containing XML files
            output_dir: Output directory for YOLO txt files
            images_dir: Optional directory containing images
            class_mapping: Optional dict mapping class names to IDs
            copy_images: If True, copy images to output directory

        Returns:
            Tuple of (successful, failed) conversion counts
        """
        xml_dir = Path(xml_dir)
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        successful = 0
        failed = 0

        for xml_file in sorted(xml_dir.glob('*.xml')):
            try:
                # Parse XML
                width, height, objects = VOCtoYOLOConverter.parse_xml(str(xml_file))

                # Convert to YOLO
                yolo_text = VOCtoYOLOConverter.convert_pascal_voc_to_yolo(
                    str(xml_file),
                    width,
                    height,
                    class_mapping
                )

                # Write YOLO file
                output_file = output_dir / (xml_file.stem + '.txt')
                with open(output_file, 'w') as f:
                    f.write(yolo_text)

                # Copy image if requested
                if copy_images and images_dir:
                    images_dir = Path(images_dir)
                    for ext in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
                        img_src = images_dir / (xml_file.stem + ext)
                        if img_src.exists():
                            img_dst = output_dir / img_src.name
                            shutil.copy2(img_src, img_dst)
                            break

                logger.info(f"✓ Converted: {xml_file.name}")
                successful += 1

            except Exception as e:
                logger.error(f"✗ Failed: {xml_file.name} - {e}")
                failed += 1

        return successful, failed


class COCOtoYOLOConverter:
    """Convert COCO JSON annotations to YOLO format."""

    @staticmethod
    def convert_coco_to_yolo(
        coco_json_path: str,
        output_dir: str,
        images_dir: Optional[str] = None,
        copy_images: bool = False,
        class_mapping: Optional[Dict[int, int]] = None
    ) -> Tuple[int, int, int]:
        """
        Convert COCO JSON annotations to YOLO format.

        Args:
            coco_json_path: Path to COCO JSON file
            output_dir: Output directory for YOLO txt files
            images_dir: Optional directory containing images
            copy_images: If True, copy images to output directory
            class_mapping: Optional dict mapping COCO category_id to YOLO class_id

        Returns:
            Tuple of (images_processed, annotations_created, errors)
        """
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        try:
            with open(coco_json_path, 'r') as f:
                coco = json.load(f)
        except Exception as e:
            logger.error(f"Error loading COCO JSON: {e}")
            raise

        # Build lookup tables
        images = {img['id']: img for img in coco.get('images', [])}
        categories = {cat['id']: cat['name'] for cat in coco.get('categories', [])}

        # Group annotations by image
        image_annotations = {}
        for ann in coco.get('annotations', []):
            img_id = ann['image_id']
            if img_id not in image_annotations:
                image_annotations[img_id] = []
            image_annotations[img_id].append(ann)

        images_processed = 0
        annotations_created = 0
        errors = 0

        # Process each image
        for img_id, img_info in images.items():
            try:
                img_width = img_info['width']
                img_height = img_info['height']
                img_filename = img_info['file_name']

                yolo_lines = []

                # Convert annotations for this image
                if img_id in image_annotations:
                    for ann in image_annotations[img_id]:
                        try:
                            # COCO bbox: [x, y, width, height]
                            bbox = ann['bbox']
                            category_id = ann['category_id']

                            x = bbox[0]
                            y = bbox[1]
                            w = bbox[2]
                            h = bbox[3]

                            # Convert to YOLO format (normalized)
                            x_center = (x + w / 2) / img_width
                            y_center = (y + h / 2) / img_height
                            width_norm = w / img_width
                            height_norm = h / img_height

                            # Validate ranges
                            for val, name in [(x_center, 'x_center'), (y_center, 'y_center'),
                                              (width_norm, 'width'), (height_norm, 'height')]:
                                if not (0 <= val <= 1):
                                    logger.warning(
                                        f"Out of range: {name}={val} in image {img_filename}"
                                    )

                            # Map category ID if mapping provided
                            if class_mapping:
                                yolo_class_id = class_mapping.get(category_id, category_id)
                            else:
                                yolo_class_id = category_id

                            yolo_line = (
                                f"{yolo_class_id} "
                                f"{x_center:.6f} {y_center:.6f} "
                                f"{width_norm:.6f} {height_norm:.6f}"
                            )
                            yolo_lines.append(yolo_line)
                            annotations_created += 1

                        except Exception as e:
                            logger.warning(
                                f"Error processing annotation in {img_filename}: {e}"
                            )
                            errors += 1

                # Write YOLO file
                output_txt = output_dir / (Path(img_filename).stem + '.txt')
                with open(output_txt, 'w') as f:
                    f.write('\n'.join(yolo_lines))

                # Copy image if requested
                if copy_images and images_dir:
                    images_dir = Path(images_dir)
                    img_src = images_dir / img_filename
                    if img_src.exists():
                        img_dst = output_dir / img_src.name
                        shutil.copy2(img_src, img_dst)
                    else:
                        logger.warning(f"Image not found: {img_src}")
                        errors += 1

                images_processed += 1
                logger.info(f"✓ Processed: {img_filename}")

            except Exception as e:
                logger.error(f"Error processing image {img_id}: {e}")
                errors += 1

        return images_processed, annotations_created, errors


class YOLOValidator:
    """Validate YOLO format labels and images."""

    @staticmethod
    def validate_yolo_label(
        label_path: str,
        max_class_id: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        """
        Validate YOLO format label file.

        Args:
            label_path: Path to .txt label file
            max_class_id: Maximum allowed class ID (optional)

        Returns:
            Tuple of (is_valid, errors)
        """
        errors = []

        try:
            with open(label_path, 'r') as f:
                lines = f.readlines()

            if not lines:
                return True, []  # Empty labels are OK (image with no objects)

            for idx, line in enumerate(lines, 1):
                parts = line.strip().split()

                if len(parts) != 5:
                    errors.append(
                        f"Line {idx}: Expected 5 values, got {len(parts)}"
                    )
                    continue

                try:
                    class_id = int(parts[0])
                    x_center = float(parts[1])
                    y_center = float(parts[2])
                    width = float(parts[3])
                    height = float(parts[4])

                    # Validate class ID
                    if class_id < 0:
                        errors.append(
                            f"Line {idx}: class_id={class_id} must be >= 0"
                        )
                    if max_class_id is not None and class_id > max_class_id:
                        errors.append(
                            f"Line {idx}: class_id={class_id} exceeds max {max_class_id}"
                        )

                    # Validate coordinates (normalized 0-1)
                    for val, name in [(x_center, 'x_center'), (y_center, 'y_center'),
                                      (width, 'width'), (height, 'height')]:
                        if not (0 <= val <= 1):
                            errors.append(
                                f"Line {idx}: {name}={val} not in range [0,1]"
                            )

                except ValueError as e:
                    errors.append(f"Line {idx}: Invalid numeric values - {e}")

            return len(errors) == 0, errors

        except Exception as e:
            return False, [f"Error reading file: {e}"]

    @staticmethod
    def validate_yolo_labels(
        images_dir: str,
        labels_dir: str,
        max_class_id: Optional[int] = None
    ) -> Dict:
        """
        Validate YOLO format labels for a dataset.

        Args:
            images_dir: Directory containing images
            labels_dir: Directory containing YOLO labels
            max_class_id: Maximum allowed class ID

        Returns:
            Dict with validation results
        """
        images_dir = Path(images_dir)
        labels_dir = Path(labels_dir)

        results = {
            'total_images': 0,
            'valid_images': 0,
            'images_without_labels': [],
            'invalid_labels': [],
            'warnings': [],
            'errors': []
        }

        valid_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp'}

        for img_file in sorted(images_dir.iterdir()):
            if img_file.suffix.lower() not in valid_extensions:
                continue

            results['total_images'] += 1
            label_file = labels_dir / (img_file.stem + '.txt')

            if not label_file.exists():
                results['images_without_labels'].append(str(img_file))
                logger.warning(f"Missing label: {img_file.name}")
                continue

            # Validate label file
            is_valid, errors = YOLOValidator.validate_yolo_label(
                str(label_file),
                max_class_id
            )

            if is_valid:
                results['valid_images'] += 1
                logger.info(f"✓ Valid: {img_file.name}")
            else:
                results['invalid_labels'].append({
                    'image': str(img_file),
                    'errors': errors
                })
                logger.error(f"✗ Invalid label: {label_file.name}")
                results['errors'].extend(errors)

        # Summary
        results['summary'] = {
            'total': results['total_images'],
            'valid': results['valid_images'],
            'without_labels': len(results['images_without_labels']),
            'invalid': len(results['invalid_labels']),
            'pass_rate': (
                results['valid_images'] / results['total_images'] * 100
                if results['total_images'] > 0 else 0
            )
        }

        return results

    @staticmethod
    def validate_coco_format(coco_json_path: str, images_dir: Optional[str] = None) -> Dict:
        """
        Validate COCO format JSON file.

        Args:
            coco_json_path: Path to COCO JSON file
            images_dir: Optional directory to verify image existence

        Returns:
            Dict with validation results
        """
        results = {
            'valid': False,
            'errors': [],
            'warnings': [],
            'summary': {}
        }

        try:
            with open(coco_json_path, 'r') as f:
                coco = json.load(f)

            # Check required fields
            required_fields = ['images', 'annotations', 'categories']
            for field in required_fields:
                if field not in coco:
                    results['errors'].append(f"Missing required field: {field}")

            images = {img['id']: img for img in coco.get('images', [])}
            annotations = coco.get('annotations', [])
            categories = coco.get('categories', [])

            # Validate images
            for img in images.values():
                if 'id' not in img or 'file_name' not in img:
                    results['errors'].append("Image missing 'id' or 'file_name'")

                if images_dir:
                    img_path = Path(images_dir) / img['file_name']
                    if not img_path.exists():
                        results['warnings'].append(
                            f"Image not found: {img['file_name']}"
                        )

            # Validate annotations
            for ann in annotations:
                required_ann_fields = ['id', 'image_id', 'category_id', 'bbox']
                for field in required_ann_fields:
                    if field not in ann:
                        results['errors'].append(
                            f"Annotation missing field: {field}"
                        )

                if ann.get('image_id') not in images:
                    results['errors'].append(
                        f"Annotation references unknown image_id: {ann.get('image_id')}"
                    )

                if ann.get('category_id') not in [c['id'] for c in categories]:
                    results['errors'].append(
                        f"Annotation references unknown category_id: {ann.get('category_id')}"
                    )

                bbox = ann.get('bbox', [])
                if len(bbox) != 4:
                    results['errors'].append(
                        f"Annotation bbox has {len(bbox)} values, expected 4"
                    )

            # Summary
            results['summary'] = {
                'images': len(images),
                'annotations': len(annotations),
                'categories': len(categories)
            }

            results['valid'] = len(results['errors']) == 0

            logger.info(f"COCO validation: {results['summary']}")
            if results['errors']:
                logger.error(f"Errors found: {len(results['errors'])}")
            if results['warnings']:
                logger.warning(f"Warnings found: {len(results['warnings'])}")

        except Exception as e:
            results['errors'].append(f"Error reading JSON: {e}")

        return results


def main():
    parser = argparse.ArgumentParser(
        description='Label format conversion and validation utilities'
    )

    subparsers = parser.add_subparsers(dest='command', help='Command to run')

    # Convert VOC to YOLO
    voc_parser = subparsers.add_parser(
        'convert-voc',
        help='Convert Pascal VOC XML to YOLO format'
    )
    voc_parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input directory containing XML files'
    )
    voc_parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for YOLO txt files'
    )
    voc_parser.add_argument(
        '--images',
        type=str,
        help='Input directory containing images'
    )
    voc_parser.add_argument(
        '--copy-images',
        action='store_true',
        help='Copy images to output directory'
    )
    voc_parser.add_argument(
        '--class-mapping',
        type=str,
        help='JSON file mapping class names to IDs'
    )

    # Convert COCO to YOLO
    coco_parser = subparsers.add_parser(
        'convert-coco',
        help='Convert COCO JSON to YOLO format'
    )
    coco_parser.add_argument(
        '--input',
        type=str,
        required=True,
        help='Input COCO JSON file'
    )
    coco_parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory for YOLO txt files'
    )
    coco_parser.add_argument(
        '--images',
        type=str,
        help='Input directory containing images'
    )
    coco_parser.add_argument(
        '--copy-images',
        action='store_true',
        help='Copy images to output directory'
    )
    coco_parser.add_argument(
        '--class-mapping',
        type=str,
        help='JSON file mapping category_id to YOLO class_id'
    )

    # Validate YOLO
    yolo_parser = subparsers.add_parser(
        'validate',
        help='Validate YOLO format labels'
    )
    yolo_parser.add_argument(
        '--images',
        type=str,
        required=True,
        help='Directory containing images'
    )
    yolo_parser.add_argument(
        '--labels',
        type=str,
        required=True,
        help='Directory containing YOLO labels'
    )
    yolo_parser.add_argument(
        '--max-class-id',
        type=int,
        help='Maximum allowed class ID'
    )

    # Validate COCO
    coco_val_parser = subparsers.add_parser(
        'validate-coco',
        help='Validate COCO format JSON'
    )
    coco_val_parser.add_argument(
        '--annotations',
        type=str,
        required=True,
        help='COCO JSON file'
    )
    coco_val_parser.add_argument(
        '--images',
        type=str,
        help='Directory containing images to verify paths'
    )

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    try:
        if args.command == 'convert-voc':
            logger.info(f"Converting Pascal VOC to YOLO...")
            logger.info(f"Input: {args.input}")
            logger.info(f"Output: {args.output}")

            # Load class mapping if provided
            class_mapping = None
            if args.class_mapping:
                with open(args.class_mapping, 'r') as f:
                    class_mapping = json.load(f)

            successful, failed = VOCtoYOLOConverter.batch_convert(
                args.input,
                args.output,
                images_dir=args.images,
                class_mapping=class_mapping,
                copy_images=args.copy_images
            )

            print(f"\n{'='*60}")
            print(f"Conversion Summary")
            print(f"{'='*60}")
            print(f"Successful: {successful}")
            print(f"Failed:     {failed}")
            print(f"Total:      {successful + failed}")

        elif args.command == 'convert-coco':
            logger.info(f"Converting COCO to YOLO...")
            logger.info(f"Input: {args.input}")
            logger.info(f"Output: {args.output}")

            # Load class mapping if provided
            class_mapping = None
            if args.class_mapping:
                with open(args.class_mapping, 'r') as f:
                    class_mapping = json.load(f)

            images_processed, annotations_created, errors = COCOtoYOLOConverter.convert_coco_to_yolo(
                args.input,
                args.output,
                images_dir=args.images,
                copy_images=args.copy_images,
                class_mapping=class_mapping
            )

            print(f"\n{'='*60}")
            print(f"Conversion Summary")
            print(f"{'='*60}")
            print(f"Images processed:    {images_processed}")
            print(f"Annotations created: {annotations_created}")
            print(f"Errors:              {errors}")

        elif args.command == 'validate':
            logger.info(f"Validating YOLO labels...")
            logger.info(f"Images: {args.images}")
            logger.info(f"Labels: {args.labels}")

            results = YOLOValidator.validate_yolo_labels(
                args.images,
                args.labels,
                max_class_id=args.max_class_id
            )

            print(f"\n{'='*60}")
            print(f"YOLO Validation Summary")
            print(f"{'='*60}")
            print(f"Total images:         {results['summary']['total']}")
            print(f"Valid images:         {results['summary']['valid']}")
            print(f"Without labels:       {results['summary']['without_labels']}")
            print(f"Invalid labels:       {results['summary']['invalid']}")
            print(f"Pass rate:            {results['summary']['pass_rate']:.1f}%")

            if results['images_without_labels']:
                print(f"\nImages without labels:")
                for img in results['images_without_labels'][:5]:
                    print(f"  - {img}")
                if len(results['images_without_labels']) > 5:
                    print(f"  ... and {len(results['images_without_labels']) - 5} more")

            if results['invalid_labels']:
                print(f"\nInvalid labels:")
                for item in results['invalid_labels'][:3]:
                    print(f"  {Path(item['image']).name}:")
                    for err in item['errors'][:2]:
                        print(f"    - {err}")
                    if len(item['errors']) > 2:
                        print(f"    ... and {len(item['errors']) - 2} more errors")

        elif args.command == 'validate-coco':
            logger.info(f"Validating COCO format...")
            logger.info(f"Annotations: {args.annotations}")

            results = YOLOValidator.validate_coco_format(
                args.annotations,
                images_dir=args.images
            )

            print(f"\n{'='*60}")
            print(f"COCO Validation Summary")
            print(f"{'='*60}")
            print(f"Valid:        {'Yes' if results['valid'] else 'No'}")
            print(f"Images:       {results['summary'].get('images', 0)}")
            print(f"Annotations:  {results['summary'].get('annotations', 0)}")
            print(f"Categories:   {results['summary'].get('categories', 0)}")

            if results['errors']:
                print(f"\nErrors ({len(results['errors'])}):")
                for err in results['errors'][:5]:
                    print(f"  - {err}")
                if len(results['errors']) > 5:
                    print(f"  ... and {len(results['errors']) - 5} more")

            if results['warnings']:
                print(f"\nWarnings ({len(results['warnings'])}):")
                for warn in results['warnings'][:5]:
                    print(f"  - {warn}")
                if len(results['warnings']) > 5:
                    print(f"  ... and {len(results['warnings']) - 5} more")

    except Exception as e:
        logger.error(f"Error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
