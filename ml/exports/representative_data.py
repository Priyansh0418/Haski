"""
Representative data generator for TFLite int8 quantization.

Generates batches of preprocessed images from validation subsets for
post-training quantization. Supports both classification and detection datasets.

Usage:
    # From command line
    python representative_data.py --data-dir ml/data --dataset-type classification \
        --num-samples 100 --batch-size 1 --output representative_data.py

    # In Python
    from representative_data import RepresentativeDataGenerator
    
    generator = RepresentativeDataGenerator(
        data_dir='ml/data',
        dataset_type='classification',
        num_samples=100,
        batch_size=1,
        input_size=(224, 224)
    )
    
    # Use with TFLite converter
    def representative_dataset():
        for batch in generator.generate_batches():
            yield [batch]

"""

import argparse
import json
import logging
from pathlib import Path
from typing import Generator, Tuple, Optional, List
import random

import numpy as np
from PIL import Image

logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# ImageNet normalization statistics
IMAGENET_MEAN = np.array([0.485, 0.456, 0.406], dtype=np.float32)
IMAGENET_STD = np.array([0.229, 0.224, 0.225], dtype=np.float32)


class RepresentativeDataGenerator:
    """
    Generate representative dataset batches for TFLite int8 quantization.
    
    Loads images from validation/test splits and preprocesses them for
    calibration during quantization.
    """
    
    def __init__(
        self,
        data_dir: str,
        dataset_type: str = 'classification',
        num_samples: int = 100,
        batch_size: int = 1,
        input_size: Tuple[int, int] = (224, 224),
        seed: int = 42
    ):
        """
        Initialize data generator.
        
        Args:
            data_dir: Path to prepared dataset directory
            dataset_type: Type of dataset ('classification' or 'detection')
            num_samples: Maximum number of samples to use
            batch_size: Batch size for generated batches
            input_size: Target image size (H, W)
            seed: Random seed for reproducibility
        """
        self.data_dir = Path(data_dir)
        self.dataset_type = dataset_type
        self.num_samples = num_samples
        self.batch_size = batch_size
        self.input_size = input_size
        self.seed = seed
        
        # Set random seed
        random.seed(seed)
        np.random.seed(seed)
        
        self.image_files: List[Path] = []
        self._load_image_paths()
    
    def _load_image_paths(self) -> None:
        """Load image paths from dataset directory."""
        logger.info(f"Loading images from {self.data_dir}")
        
        if self.dataset_type == 'classification':
            self._load_classification_images()
        elif self.dataset_type == 'detection':
            self._load_detection_images()
        else:
            raise ValueError(
                f"Unknown dataset type: {self.dataset_type}. "
                "Supported: 'classification', 'detection'"
            )
        
        # Limit to num_samples
        if len(self.image_files) > self.num_samples:
            self.image_files = random.sample(self.image_files, self.num_samples)
            logger.info(f"Sampled {len(self.image_files)} random images")
        else:
            logger.info(f"Loaded {len(self.image_files)} images")
        
        if not self.image_files:
            logger.warning("No images found. Quantization may fail.")
    
    def _load_classification_images(self) -> None:
        """Load images from classification dataset structure."""
        # Look for val/test splits
        for split_dir in ['val', 'test']:
            split_path = self.data_dir / split_dir
            if split_path.exists():
                logger.info(f"Found {split_dir} split")
                
                # Iterate through class directories
                for class_dir in split_path.iterdir():
                    if class_dir.is_dir():
                        class_images = list(class_dir.glob('*.jpg')) + \
                                      list(class_dir.glob('*.png')) + \
                                      list(class_dir.glob('*.jpeg'))
                        self.image_files.extend(class_images)
                        logger.info(f"  {class_dir.name}: {len(class_images)} images")
        
        # If no val/test split, look in root
        if not self.image_files:
            logger.info("No val/test splits found, looking in root directory")
            for ext in ['*.jpg', '*.png', '*.jpeg']:
                self.image_files.extend(self.data_dir.glob(ext))
            
            # If still empty, look recursively
            if not self.image_files:
                logger.info("Looking recursively for images")
                for ext in ['**/*.jpg', '**/*.png', '**/*.jpeg']:
                    self.image_files.extend(self.data_dir.glob(ext))
    
    def _load_detection_images(self) -> None:
        """Load images from detection dataset structure (YOLO format)."""
        # Look for images/val or images/test
        images_dir = self.data_dir / 'images'
        
        if images_dir.exists():
            for split_dir in ['val', 'test']:
                split_path = images_dir / split_dir
                if split_path.exists():
                    logger.info(f"Found {split_dir} split")
                    images = list(split_path.glob('*.jpg')) + \
                            list(split_path.glob('*.png')) + \
                            list(split_path.glob('*.jpeg'))
                    self.image_files.extend(images)
                    logger.info(f"  {split_dir}: {len(images)} images")
        
        # If no splits, look in images root
        if not self.image_files and (self.data_dir / 'images').exists():
            logger.info("No val/test splits in images/, using all")
            self.image_files = list((self.data_dir / 'images').glob('**/*.jpg')) + \
                             list((self.data_dir / 'images').glob('**/*.png')) + \
                             list((self.data_dir / 'images').glob('**/*.jpeg'))
    
    def _preprocess_image(self, image_path: Path) -> np.ndarray:
        """
        Preprocess single image for inference.
        
        Args:
            image_path: Path to image file
        
        Returns:
            Preprocessed image array (3, H, W) in float32 range [-2, 2]
        
        Raises:
            IOError: If image cannot be loaded
        """
        try:
            # Load image
            image = Image.open(image_path).convert('RGB')
        except Exception as e:
            raise IOError(f"Failed to load image {image_path}: {e}")
        
        # Resize
        image = image.resize(self.input_size, Image.Resampling.BILINEAR)
        
        # Convert to array
        image_array = np.array(image, dtype=np.float32) / 255.0
        
        # Normalize with ImageNet statistics
        image_array = (image_array - IMAGENET_MEAN) / IMAGENET_STD
        
        # Transpose to (C, H, W) format for TFLite
        image_array = np.transpose(image_array, (2, 0, 1))
        
        return image_array
    
    def generate_batches(self) -> Generator[np.ndarray, None, None]:
        """
        Generate batches of preprocessed images.
        
        Yields:
            Batch of preprocessed images (batch_size, 3, H, W) as float32
        """
        if not self.image_files:
            logger.warning("No images available")
            return
        
        batch = []
        failed_count = 0
        
        for image_path in self.image_files:
            try:
                image_array = self._preprocess_image(image_path)
                batch.append(image_array)
                
                # Yield when batch is full
                if len(batch) == self.batch_size:
                    batch_array = np.stack(batch, axis=0)
                    yield batch_array
                    batch = []
            
            except IOError as e:
                logger.warning(f"Skipping {image_path}: {e}")
                failed_count += 1
                continue
        
        # Yield remaining images
        if batch:
            # Pad with last image if needed
            while len(batch) < self.batch_size:
                batch.append(batch[-1])
            batch_array = np.stack(batch, axis=0)
            yield batch_array
        
        if failed_count > 0:
            logger.warning(f"Failed to load {failed_count} images")
    
    def generate_tflite_batches(self) -> Generator[list, None, None]:
        """
        Generate batches compatible with TFLite quantization.
        
        Converts float32 images to uint8 format for quantized models.
        
        Yields:
            List containing single uint8 tensor [tf.constant(batch)]
        """
        try:
            import tensorflow as tf
        except ImportError:
            raise ImportError(
                "TensorFlow required for TFLite batch generation. "
                "Install with: pip install tensorflow"
            )
        
        for batch in self.generate_batches():
            # Convert float32 [-2, 2] to uint8 [0, 255]
            # Assuming range from standardized ImageNet: ~[-3, 3] maps to [0, 255]
            batch_uint8 = ((batch + 2.0) * 63.75).astype(np.uint8)
            
            yield [tf.constant(batch_uint8)]
    
    def get_statistics(self) -> dict:
        """
        Get statistics about loaded images.
        
        Returns:
            Dictionary with dataset statistics
        """
        return {
            'total_images': len(self.image_files),
            'batch_size': self.batch_size,
            'num_batches': (len(self.image_files) + self.batch_size - 1) // self.batch_size,
            'input_size': self.input_size,
            'dataset_type': self.dataset_type,
            'data_dir': str(self.data_dir)
        }
    
    def print_summary(self) -> None:
        """Print summary of loaded dataset."""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("Representative Dataset Summary")
        print("="*60)
        print(f"Dataset Type:     {stats['dataset_type']}")
        print(f"Data Directory:   {stats['data_dir']}")
        print(f"Total Images:     {stats['total_images']}")
        print(f"Batch Size:       {stats['batch_size']}")
        print(f"Num Batches:      {stats['num_batches']}")
        print(f"Input Size:       {stats['input_size']}")
        print("="*60 + "\n")


def create_representative_dataset_module(
    output_path: str,
    data_dir: str,
    dataset_type: str = 'classification',
    num_samples: int = 100,
    batch_size: int = 1
) -> str:
    """
    Generate a ready-to-use representative dataset module.
    
    Creates a Python file that can be directly imported and used with
    TFLite converter.
    
    Args:
        output_path: Path to save generated module
        data_dir: Path to dataset directory
        dataset_type: Type of dataset
        num_samples: Number of samples
        batch_size: Batch size
    
    Returns:
        Path to generated module
    """
    template = '''"""
Auto-generated representative dataset for TFLite quantization.
Generated from: {data_dir}
"""

import numpy as np

{import_code}

def representative_data_gen():
    """Generate representative data for TFLite quantization.
    
    Yields:
        List with single tf.constant tensor for TFLite converter
    
    Usage:
        converter.optimizations = [tf.lite.Optimize.DEFAULT]
        converter.representative_dataset = representative_data_gen
    """
    from representative_data import RepresentativeDataGenerator
    
    gen = RepresentativeDataGenerator(
        data_dir='{data_dir}',
        dataset_type='{dataset_type}',
        num_samples={num_samples},
        batch_size={batch_size},
        input_size=(224, 224)
    )
    
    for batch in gen.generate_tflite_batches():
        yield batch


if __name__ == '__main__':
    from representative_data import RepresentativeDataGenerator
    
    gen = RepresentativeDataGenerator(
        data_dir='{data_dir}',
        dataset_type='{dataset_type}',
        num_samples={num_samples},
        batch_size={batch_size}
    )
    
    print("Testing representative dataset generator...")
    gen.print_summary()
    
    print("Generating sample batches...")
    for i, batch in enumerate(gen.generate_batches()):
        print(f"Batch {{i}}: shape={{batch.shape}}, dtype={{batch.dtype}}, "
              f"min={{batch.min():.3f}}, max={{batch.max():.3f}}")
        if i >= 2:
            break
    
    print("Dataset generation successful!")
'''
    
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    
    # Determine imports
    import_code = "import tensorflow as tf" if 'tflite' in output_path.name else ""
    
    generated_code = template.format(
        data_dir=data_dir,
        dataset_type=dataset_type,
        num_samples=num_samples,
        batch_size=batch_size,
        import_code=import_code
    )
    
    with open(output_path, 'w') as f:
        f.write(generated_code)
    
    logger.info(f"Generated representative dataset module: {output_path}")
    return str(output_path)


def main():
    """Command-line interface for representative dataset generation."""
    parser = argparse.ArgumentParser(
        description='Generate representative data for TFLite int8 quantization',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate from classification dataset
  %(prog)s --data-dir ml/data --dataset-type classification \\
    --num-samples 100 --batch-size 1

  # Generate from detection (YOLO) dataset
  %(prog)s --data-dir ml/data/output --dataset-type detection \\
    --num-samples 50 --batch-size 4

  # Create ready-to-use module
  %(prog)s --data-dir ml/data --output gen_representative_data.py \\
    --create-module
        '''
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='ml/data',
        help='Path to prepared dataset directory (default: ml/data)'
    )
    
    parser.add_argument(
        '--dataset-type',
        type=str,
        choices=['classification', 'detection'],
        default='classification',
        help='Type of dataset (default: classification)'
    )
    
    parser.add_argument(
        '--num-samples',
        type=int,
        default=100,
        help='Maximum number of samples to use (default: 100)'
    )
    
    parser.add_argument(
        '--batch-size',
        type=int,
        default=1,
        help='Batch size for generated batches (default: 1)'
    )
    
    parser.add_argument(
        '--input-size',
        type=int,
        nargs=2,
        default=[224, 224],
        metavar=('HEIGHT', 'WIDTH'),
        help='Input image size (default: 224 224)'
    )
    
    parser.add_argument(
        '--seed',
        type=int,
        default=42,
        help='Random seed for reproducibility (default: 42)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Path to save generated module (optional)'
    )
    
    parser.add_argument(
        '--create-module',
        action='store_true',
        help='Generate ready-to-use Python module'
    )
    
    parser.add_argument(
        '--test-batches',
        type=int,
        default=3,
        help='Number of batches to generate for testing (default: 3)'
    )
    
    args = parser.parse_args()
    
    # Validate paths
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Dataset directory not found: {data_dir}")
        return 1
    
    try:
        # Create generator
        generator = RepresentativeDataGenerator(
            data_dir=str(data_dir),
            dataset_type=args.dataset_type,
            num_samples=args.num_samples,
            batch_size=args.batch_size,
            input_size=tuple(args.input_size),
            seed=args.seed
        )
        
        # Print summary
        generator.print_summary()
        
        # Generate or test batches
        if args.create_module and args.output:
            create_representative_dataset_module(
                output_path=args.output,
                data_dir=str(data_dir),
                dataset_type=args.dataset_type,
                num_samples=args.num_samples,
                batch_size=args.batch_size
            )
            logger.info(f"Module created: {args.output}")
        else:
            # Test batch generation
            logger.info(f"Generating {args.test_batches} test batches...")
            for i, batch in enumerate(generator.generate_batches()):
                print(f"\nBatch {i}:")
                print(f"  Shape:     {batch.shape}")
                print(f"  Data type: {batch.dtype}")
                print(f"  Min value: {batch.min():.4f}")
                print(f"  Max value: {batch.max():.4f}")
                print(f"  Mean:      {batch.mean():.4f}")
                print(f"  Std:       {batch.std():.4f}")
                
                if i >= args.test_batches - 1:
                    break
        
        logger.info("Representative dataset generation completed successfully!")
        return 0
    
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    import sys
    sys.exit(main())
