"""
Image Augmentation Utilities for Haski ML Training

Provides data augmentation transforms for training and validation phases.
Supports PyTorch with torchvision transforms.

Usage:
    from augmentations import get_transforms
    
    # Get transforms for training phase
    train_transforms = get_transforms(phase='train')
    
    # Get transforms for validation phase
    val_transforms = get_transforms(phase='val')
    
    # Apply to image
    augmented_image = train_transforms(image)
"""

import os
import math
import random
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

import torch
import torchvision.transforms as transforms
from torchvision.transforms import (
    RandomResizedCrop,
    ColorJitter,
    RandomHorizontalFlip,
    RandomRotation,
    GaussianBlur,
    Resize,
    CenterCrop,
    ToTensor,
    Normalize,
    Compose,
    RandomAffine,
    RandomPerspective,
)

try:
    from PIL import Image
except ImportError:
    Image = None

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]


class AugmentationConfig:
    """Configuration for augmentation parameters."""
    
    # Input/output sizes
    INPUT_SIZE = 224
    RESIZE_SIZE = 256
    
    # Color augmentation
    COLOR_JITTER_BRIGHTNESS = 0.2
    COLOR_JITTER_CONTRAST = 0.2
    COLOR_JITTER_SATURATION = 0.2
    COLOR_JITTER_HUE = 0.1
    
    # Geometric augmentation
    RANDOM_ROTATION_DEGREES = 15
    RANDOM_AFFINE_DEGREES = 10
    RANDOM_AFFINE_TRANSLATE = (0.1, 0.1)
    RANDOM_AFFINE_SCALE = (0.8, 1.2)
    
    # Blur
    GAUSSIAN_BLUR_KERNEL_SIZE = 5
    GAUSSIAN_BLUR_SIGMA = (0.1, 2.0)
    
    # Normalization
    MEAN = IMAGENET_MEAN
    STD = IMAGENET_STD


def get_transforms(
    phase: str = 'train',
    input_size: int = 224,
    config: Optional[AugmentationConfig] = None
) -> Compose:
    """
    Get augmentation transforms for training or validation.
    
    Args:
        phase: 'train' or 'val'
        input_size: Target image size (default 224 for ImageNet)
        config: Optional AugmentationConfig instance
        
    Returns:
        torchvision.transforms.Compose object
        
    Raises:
        ValueError: If phase is not 'train' or 'val'
    """
    if phase not in ['train', 'val']:
        raise ValueError(f"Phase must be 'train' or 'val', got '{phase}'")
    
    if config is None:
        config = AugmentationConfig()
    
    if phase == 'train':
        return _get_train_transforms(input_size, config)
    else:
        return _get_val_transforms(input_size, config)


def _get_train_transforms(
    input_size: int,
    config: AugmentationConfig
) -> Compose:
    """
    Get augmented transforms for training phase.
    
    Includes:
    - RandomResizedCrop: Random crop with aspect ratio distortion
    - ColorJitter: Brightness, contrast, saturation, hue variations
    - RandomHorizontalFlip: 50% chance horizontal flip
    - RandomRotation: Random rotation up to 15 degrees
    - GaussianBlur: Random Gaussian blur for regularization
    - RandomAffine: Additional affine transformations
    - ToTensor: Convert to tensor
    - Normalize: ImageNet normalization
    
    Args:
        input_size: Target image size
        config: Augmentation configuration
        
    Returns:
        Compose transform pipeline
    """
    transform_list = [
        # Geometric augmentation - RandomResizedCrop
        RandomResizedCrop(
            size=input_size,
            scale=(0.8, 1.0),  # 80-100% of original
            ratio=(0.75, 1.33)  # 3:4 to 4:3 aspect ratio
        ),
        
        # Color augmentation
        ColorJitter(
            brightness=config.COLOR_JITTER_BRIGHTNESS,
            contrast=config.COLOR_JITTER_CONTRAST,
            saturation=config.COLOR_JITTER_SATURATION,
            hue=config.COLOR_JITTER_HUE
        ),
        
        # Spatial augmentation - Horizontal flip
        RandomHorizontalFlip(p=0.5),
        
        # Rotation
        RandomRotation(
            degrees=config.RANDOM_ROTATION_DEGREES,
            fill=0
        ),
        
        # Affine transformation (rotation, translation, scale, shear)
        RandomAffine(
            degrees=config.RANDOM_AFFINE_DEGREES,
            translate=config.RANDOM_AFFINE_TRANSLATE,
            scale=config.RANDOM_AFFINE_SCALE,
            shear=10,
            fill=0
        ),
        
        # Perspective transformation for slight distortion
        RandomPerspective(
            distortion_scale=0.2,
            p=0.5,
            fill=0
        ),
        
        # Blur augmentation for regularization
        GaussianBlur(
            kernel_size=config.GAUSSIAN_BLUR_KERNEL_SIZE,
            sigma=config.GAUSSIAN_BLUR_SIGMA
        ),
        
        # Convert to tensor
        ToTensor(),
        
        # Normalize with ImageNet statistics
        Normalize(
            mean=config.MEAN,
            std=config.STD
        ),
    ]
    
    return Compose(transform_list)


def _get_val_transforms(
    input_size: int,
    config: AugmentationConfig
) -> Compose:
    """
    Get transforms for validation phase (minimal augmentation).
    
    Includes:
    - Resize: Resize to slightly larger than target
    - CenterCrop: Center crop to target size
    - ToTensor: Convert to tensor
    - Normalize: ImageNet normalization
    
    Args:
        input_size: Target image size
        config: Augmentation configuration
        
    Returns:
        Compose transform pipeline
    """
    # Calculate resize size to maintain aspect ratio
    resize_size = int(input_size * config.RESIZE_SIZE / config.INPUT_SIZE)
    
    transform_list = [
        # Resize to slightly larger than input_size
        Resize(size=resize_size),
        
        # Center crop to input_size
        CenterCrop(size=input_size),
        
        # Convert to tensor
        ToTensor(),
        
        # Normalize with ImageNet statistics
        Normalize(
            mean=config.MEAN,
            std=config.STD
        ),
    ]
    
    return Compose(transform_list)


def get_augmentation_stats() -> Dict:
    """
    Get augmentation configuration statistics.
    
    Returns:
        Dict with augmentation settings
    """
    config = AugmentationConfig()
    
    stats = {
        'input_size': config.INPUT_SIZE,
        'resize_size': config.RESIZE_SIZE,
        'color_jitter': {
            'brightness': config.COLOR_JITTER_BRIGHTNESS,
            'contrast': config.COLOR_JITTER_CONTRAST,
            'saturation': config.COLOR_JITTER_SATURATION,
            'hue': config.COLOR_JITTER_HUE,
        },
        'rotation': {
            'degrees': config.RANDOM_ROTATION_DEGREES,
        },
        'affine': {
            'degrees': config.RANDOM_AFFINE_DEGREES,
            'translate': config.RANDOM_AFFINE_TRANSLATE,
            'scale': config.RANDOM_AFFINE_SCALE,
        },
        'blur': {
            'kernel_size': config.GAUSSIAN_BLUR_KERNEL_SIZE,
            'sigma': config.GAUSSIAN_BLUR_SIGMA,
        },
        'normalization': {
            'mean': config.MEAN,
            'std': config.STD,
        },
        'train_transforms': [
            'RandomResizedCrop(224, scale=(0.8, 1.0))',
            'ColorJitter(0.2, 0.2, 0.2, 0.1)',
            'RandomHorizontalFlip(p=0.5)',
            'RandomRotation(±15°)',
            'RandomAffine(±10°, translate, scale, shear)',
            'RandomPerspective(distortion=0.2)',
            'GaussianBlur(kernel=5)',
            'Normalize(ImageNet)',
        ],
        'val_transforms': [
            'Resize(256)',
            'CenterCrop(224)',
            'Normalize(ImageNet)',
        ],
    }
    
    return stats


def denormalize_image(
    tensor: torch.Tensor,
    mean: List[float] = None,
    std: List[float] = None
) -> torch.Tensor:
    """
    Denormalize an image tensor.
    
    Args:
        tensor: Normalized image tensor (C, H, W)
        mean: Normalization mean (default: ImageNet)
        std: Normalization std (default: ImageNet)
        
    Returns:
        Denormalized tensor
    """
    if mean is None:
        mean = IMAGENET_MEAN
    if std is None:
        std = IMAGENET_STD
    
    # Create normalization tensors
    mean_tensor = torch.tensor(mean).view(-1, 1, 1)
    std_tensor = torch.tensor(std).view(-1, 1, 1)
    
    # Denormalize: x_original = (x_normalized * std) + mean
    denormalized = tensor * std_tensor + mean_tensor
    
    return torch.clamp(denormalized, 0, 1)


def tensor_to_image(tensor: torch.Tensor) -> 'Image':
    """
    Convert a PyTorch tensor to PIL Image.
    
    Args:
        tensor: Tensor of shape (C, H, W) with values in [0, 1]
        
    Returns:
        PIL Image
    """
    if Image is None:
        raise ImportError("PIL/Pillow is required for this function")
    
    # Handle batch dimension if present
    if len(tensor.shape) == 4:
        tensor = tensor[0]
    
    # Ensure tensor is on CPU and detached
    if isinstance(tensor, torch.Tensor):
        tensor = tensor.detach().cpu()
    
    # Convert to numpy and transpose to (H, W, C)
    array = tensor.numpy()
    if array.shape[0] == 3:  # Channels first
        array = array.transpose(1, 2, 0)
    
    # Convert to uint8
    array = (array * 255).astype('uint8')
    
    return Image.fromarray(array)


def preview_augmentations(
    image_path: str,
    output_dir: str,
    num_examples: int = 9,
    config: Optional[AugmentationConfig] = None
):
    """
    Generate preview of augmented images and save to disk.
    
    Args:
        image_path: Path to source image
        output_dir: Directory to save preview images
        num_examples: Number of augmented examples to generate
        config: Optional AugmentationConfig
        
    Raises:
        FileNotFoundError: If image doesn't exist
        ImportError: If PIL/Pillow not available
    """
    if Image is None:
        raise ImportError("PIL/Pillow is required for this function")
    
    image_path = Path(image_path)
    if not image_path.exists():
        raise FileNotFoundError(f"Image not found: {image_path}")
    
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if config is None:
        config = AugmentationConfig()
    
    # Load image
    image = Image.open(image_path).convert('RGB')
    logger.info(f"Loaded image: {image_path} ({image.size})")
    
    # Get training transforms
    train_transforms = get_transforms(phase='train', config=config)
    val_transforms = get_transforms(phase='val', config=config)
    
    # Generate training augmentations
    logger.info(f"Generating {num_examples} training augmentations...")
    for i in range(num_examples):
        augmented_tensor = train_transforms(image)
        denormalized = denormalize_image(augmented_tensor)
        augmented_image = tensor_to_image(denormalized)
        
        output_path = output_dir / f"train_aug_{i:02d}.jpg"
        augmented_image.save(output_path)
        logger.info(f"  Saved: {output_path}")
    
    # Generate validation augmentations
    logger.info(f"Generating {num_examples} validation augmentations...")
    for i in range(num_examples):
        augmented_tensor = val_transforms(image)
        denormalized = denormalize_image(augmented_tensor)
        augmented_image = tensor_to_image(denormalized)
        
        output_path = output_dir / f"val_aug_{i:02d}.jpg"
        augmented_image.save(output_path)
        logger.info(f"  Saved: {output_path}")
    
    # Save original image
    image.save(output_dir / "original.jpg")
    logger.info(f"Saved original image")
    
    logger.info(f"\nPreview images saved to: {output_dir}")
    logger.info(f"Total files: {2 * num_examples + 1}")


def print_augmentation_info(config: Optional[AugmentationConfig] = None):
    """
    Print detailed augmentation information.
    
    Args:
        config: Optional AugmentationConfig
    """
    if config is None:
        config = AugmentationConfig()
    
    print("\n" + "="*70)
    print("IMAGE AUGMENTATION CONFIGURATION")
    print("="*70)
    
    print("\n[INPUT/OUTPUT SIZES]")
    print(f"  Input size:     {config.INPUT_SIZE}×{config.INPUT_SIZE}")
    print(f"  Resize size:    {config.RESIZE_SIZE}×{config.RESIZE_SIZE}")
    
    print("\n[TRAINING TRANSFORMS]")
    print("  1. RandomResizedCrop (224×224)")
    print("     • Scale range: 80-100% of original")
    print("     • Aspect ratio: 3:4 to 4:3")
    print(f"  2. ColorJitter")
    print(f"     • Brightness:  ±{config.COLOR_JITTER_BRIGHTNESS}")
    print(f"     • Contrast:    ±{config.COLOR_JITTER_CONTRAST}")
    print(f"     • Saturation:  ±{config.COLOR_JITTER_SATURATION}")
    print(f"     • Hue:         ±{config.COLOR_JITTER_HUE}")
    print(f"  3. RandomHorizontalFlip (p=0.5)")
    print(f"  4. RandomRotation (±{config.RANDOM_ROTATION_DEGREES}°)")
    print(f"  5. RandomAffine")
    print(f"     • Rotation:    ±{config.RANDOM_AFFINE_DEGREES}°")
    print(f"     • Translation: {config.RANDOM_AFFINE_TRANSLATE}")
    print(f"     • Scale:       {config.RANDOM_AFFINE_SCALE}")
    print(f"     • Shear:       ±10°")
    print(f"  6. RandomPerspective (distortion=0.2, p=0.5)")
    print(f"  7. GaussianBlur (kernel={config.GAUSSIAN_BLUR_KERNEL_SIZE})")
    print(f"     • Sigma range: {config.GAUSSIAN_BLUR_SIGMA}")
    print(f"  8. ToTensor()")
    print(f"  9. Normalize (ImageNet)")
    
    print("\n[VALIDATION TRANSFORMS]")
    print(f"  1. Resize ({config.RESIZE_SIZE}×{config.RESIZE_SIZE})")
    print(f"  2. CenterCrop ({config.INPUT_SIZE}×{config.INPUT_SIZE})")
    print(f"  3. ToTensor()")
    print(f"  4. Normalize (ImageNet)")
    
    print("\n[NORMALIZATION STATISTICS]")
    print(f"  Mean (ImageNet):  {config.MEAN}")
    print(f"  Std (ImageNet):   {config.STD}")
    
    print("\n[RATIONALE]")
    print("  Training transforms:")
    print("    • RandomResizedCrop: Simulates different object sizes/positions")
    print("    • ColorJitter: Handles different lighting conditions")
    print("    • Flips/Rotations: Spatial invariance")
    print("    • Affine/Perspective: Handles camera angles and viewpoints")
    print("    • GaussianBlur: Regularization and robustness")
    print("\n  Validation transforms:")
    print("    • Minimal augmentation for fair model evaluation")
    print("    • Consistent center crop for reproducibility")
    print("\n" + "="*70 + "\n")


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Image augmentation utilities'
    )
    
    subparsers = parser.add_subparsers(dest='command')
    
    # Preview command
    preview_parser = subparsers.add_parser(
        'preview',
        help='Preview augmented images'
    )
    preview_parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='Path to source image'
    )
    preview_parser.add_argument(
        '--output',
        type=str,
        required=True,
        help='Output directory'
    )
    preview_parser.add_argument(
        '--num-examples',
        type=int,
        default=9,
        help='Number of augmented examples per phase'
    )
    
    # Info command
    info_parser = subparsers.add_parser(
        'info',
        help='Show augmentation configuration'
    )
    
    args = parser.parse_args()
    
    if args.command == 'preview':
        preview_augmentations(
            args.image,
            args.output,
            num_examples=args.num_examples
        )
    elif args.command == 'info':
        print_augmentation_info()
    else:
        parser.print_help()
