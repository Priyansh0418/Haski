"""
Transfer Learning Classifier Training Script for Haski

Implements transfer learning using pre-trained EfficientNet-B0 or ResNet50.
Supports training on custom image datasets with automatic class detection.

Features:
- Transfer learning from ImageNet pre-trained models
- Automatic class detection from dataset structure
- Data augmentation with torchvision transforms
- Training/validation loops with metrics logging
- Early stopping and model checkpointing
- JSON metrics export for analysis
- GPU support with automatic device detection

Usage:
    python train_classifier.py --data-dir /path/to/dataset --epochs 50
    python train_classifier.py --data-dir data/ --model efficientnet_b0 --batch-size 32
    python train_classifier.py --data-dir data/ --lr 0.001 --output models/
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from collections import defaultdict
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset, random_split
from torchvision import datasets, models, transforms
from torchvision.models import EfficientNet_B0_Weights, ResNet50_Weights
from PIL import Image
import tqdm

# Import augmentation utilities
try:
    from augmentations import get_transforms, AugmentationConfig
except ImportError:
    sys.path.insert(0, str(Path(__file__).parent))
    from augmentations import get_transforms, AugmentationConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class TrainingConfig:
    """Training configuration parameters."""
    
    def __init__(
        self,
        data_dir: str,
        model_name: str = 'efficientnet_b0',
        epochs: int = 50,
        batch_size: int = 32,
        learning_rate: float = 0.001,
        weight_decay: float = 1e-4,
        output_dir: str = None,
        device: str = None,
        num_workers: int = 4,
        patience: int = 10,
        val_split: float = 0.2,
    ):
        """
        Initialize training configuration.
        
        Args:
            data_dir: Directory containing train/val or class folders
            model_name: 'efficientnet_b0' or 'resnet50'
            epochs: Number of training epochs
            batch_size: Batch size for training
            learning_rate: Initial learning rate
            weight_decay: L2 regularization weight
            output_dir: Directory to save models and metrics
            device: 'cuda' or 'cpu' (auto-detect if None)
            num_workers: DataLoader workers
            patience: Early stopping patience
            val_split: Validation split ratio if no val folder
        """
        self.data_dir = Path(data_dir)
        self.model_name = model_name.lower()
        self.epochs = epochs
        self.batch_size = batch_size
        self.learning_rate = learning_rate
        self.weight_decay = weight_decay
        self.output_dir = Path(output_dir or 'ml/exports')
        self.num_workers = num_workers
        self.patience = patience
        self.val_split = val_split
        
        # Auto-detect device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        # Validate model name
        if self.model_name not in ['efficientnet_b0', 'resnet50']:
            raise ValueError(
                f"Model must be 'efficientnet_b0' or 'resnet50', "
                f"got '{self.model_name}'"
            )
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
    def __repr__(self) -> str:
        return (
            f"TrainingConfig(\n"
            f"  data_dir={self.data_dir}\n"
            f"  model={self.model_name}\n"
            f"  epochs={self.epochs}\n"
            f"  batch_size={self.batch_size}\n"
            f"  lr={self.learning_rate}\n"
            f"  device={self.device}\n"
            f"  output_dir={self.output_dir}\n"
            f")"
        )


class ClassificationDataset(Dataset):
    """Custom dataset for image classification."""
    
    def __init__(
        self,
        image_paths: List[str],
        labels: List[int],
        transforms_fn = None
    ):
        """
        Initialize dataset.
        
        Args:
            image_paths: List of image file paths
            labels: List of class labels
            transforms_fn: Augmentation transforms
        """
        self.image_paths = image_paths
        self.labels = labels
        self.transforms = transforms_fn
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """Get item by index."""
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        # Load image
        image = Image.open(image_path).convert('RGB')
        
        # Apply transforms
        if self.transforms:
            image = self.transforms(image)
        
        return image, label


def get_dataloaders(
    config: TrainingConfig,
    class_to_idx: Dict[str, int],
    augmentation_config: Optional[AugmentationConfig] = None
) -> Tuple[DataLoader, DataLoader, int]:
    """
    Create training and validation dataloaders.
    
    Args:
        config: Training configuration
        class_to_idx: Mapping of class names to indices
        augmentation_config: Augmentation configuration
        
    Returns:
        Tuple of (train_loader, val_loader, num_classes)
    """
    logger.info("Loading dataset...")
    
    # Collect all images and labels
    image_paths = []
    labels = []
    
    # Check if dataset has train/val split
    train_dir = config.data_dir / 'train'
    val_dir = config.data_dir / 'val'
    
    if train_dir.exists() and val_dir.exists():
        logger.info("Using pre-split train/val directories")
        
        # Load training data
        for class_name, class_idx in class_to_idx.items():
            class_dir = train_dir / class_name
            if class_dir.exists():
                for img_file in class_dir.glob('*.jpg'):
                    image_paths.append(str(img_file))
                    labels.append(class_idx)
                for img_file in class_dir.glob('*.png'):
                    image_paths.append(str(img_file))
                    labels.append(class_idx)
        
        train_image_paths = image_paths
        train_labels = labels
        
        # Load validation data
        val_image_paths = []
        val_labels = []
        for class_name, class_idx in class_to_idx.items():
            class_dir = val_dir / class_name
            if class_dir.exists():
                for img_file in class_dir.glob('*.jpg'):
                    val_image_paths.append(str(img_file))
                    val_labels.append(class_idx)
                for img_file in class_dir.glob('*.png'):
                    val_image_paths.append(str(img_file))
                    val_labels.append(class_idx)
    else:
        logger.info(f"Splitting data with {config.val_split:.0%} validation ratio")
        
        # Load all images and labels
        for class_name, class_idx in class_to_idx.items():
            class_dir = config.data_dir / class_name
            if not class_dir.exists():
                logger.warning(f"Class directory not found: {class_dir}")
                continue
            
            for img_file in class_dir.glob('*.jpg'):
                image_paths.append(str(img_file))
                labels.append(class_idx)
            for img_file in class_dir.glob('*.png'):
                image_paths.append(str(img_file))
                labels.append(class_idx)
            for img_file in class_dir.glob('*.jpeg'):
                image_paths.append(str(img_file))
                labels.append(class_idx)
        
        # Split into train and validation
        total_size = len(image_paths)
        val_size = int(total_size * config.val_split)
        train_size = total_size - val_size
        
        # Create indices and shuffle
        indices = np.random.permutation(total_size)
        train_indices = indices[:train_size]
        val_indices = indices[train_size:]
        
        train_image_paths = [image_paths[i] for i in train_indices]
        train_labels = [labels[i] for i in train_indices]
        
        val_image_paths = [image_paths[i] for i in val_indices]
        val_labels = [labels[i] for i in val_indices]
    
    logger.info(f"Training samples: {len(train_image_paths)}")
    logger.info(f"Validation samples: {len(val_image_paths)}")
    
    # Print class distribution
    logger.info("\nClass distribution:")
    train_counts = defaultdict(int)
    for label in train_labels:
        train_counts[label] += 1
    
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    for class_idx in sorted(train_counts.keys()):
        class_name = idx_to_class[class_idx]
        count = train_counts[class_idx]
        logger.info(f"  {class_name}: {count}")
    
    # Create transforms
    train_transforms = get_transforms(phase='train', config=augmentation_config)
    val_transforms = get_transforms(phase='val', config=augmentation_config)
    
    # Create datasets
    train_dataset = ClassificationDataset(
        train_image_paths,
        train_labels,
        transforms_fn=train_transforms
    )
    val_dataset = ClassificationDataset(
        val_image_paths,
        val_labels,
        transforms_fn=val_transforms
    )
    
    # Create dataloaders
    train_loader = DataLoader(
        train_dataset,
        batch_size=config.batch_size,
        shuffle=True,
        num_workers=config.num_workers,
        pin_memory=True if config.device == 'cuda' else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True if config.device == 'cuda' else False
    )
    
    num_classes = len(class_to_idx)
    
    return train_loader, val_loader, num_classes


def build_model(
    model_name: str,
    num_classes: int,
    device: str
) -> nn.Module:
    """
    Build transfer learning model.
    
    Args:
        model_name: 'efficientnet_b0' or 'resnet50'
        num_classes: Number of output classes
        device: Device to place model on
        
    Returns:
        PyTorch model
    """
    logger.info(f"Building model: {model_name}")
    
    if model_name == 'efficientnet_b0':
        model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        # Get input features of final layer
        in_features = model.classifier[1].in_features
        # Replace final layer
        model.classifier[1] = nn.Linear(in_features, num_classes)
    
    elif model_name == 'resnet50':
        model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        # Get input features of final layer
        in_features = model.fc.in_features
        # Replace final layer
        model.fc = nn.Linear(in_features, num_classes)
    
    model = model.to(device)
    
    # Log model info
    num_params = sum(p.numel() for p in model.parameters())
    trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
    logger.info(f"Total parameters: {num_params:,}")
    logger.info(f"Trainable parameters: {trainable_params:,}")
    
    return model


def train_epoch(
    model: nn.Module,
    train_loader: DataLoader,
    criterion: nn.Module,
    optimizer: optim.Optimizer,
    device: str,
    epoch: int,
    total_epochs: int
) -> Dict[str, float]:
    """
    Train for one epoch.
    
    Args:
        model: PyTorch model
        train_loader: Training dataloader
        criterion: Loss function
        optimizer: Optimizer
        device: Device to run on
        epoch: Current epoch number
        total_epochs: Total number of epochs
        
    Returns:
        Dict with epoch metrics (loss, accuracy)
    """
    model.train()
    
    running_loss = 0.0
    correct_predictions = 0
    total_samples = 0
    
    progress_bar = tqdm.tqdm(
        train_loader,
        desc=f"Epoch {epoch+1}/{total_epochs} [Train]",
        unit='batch'
    )
    
    for batch_idx, (images, labels) in enumerate(progress_bar):
        # Move to device
        images = images.to(device)
        labels = labels.to(device)
        
        # Zero gradients
        optimizer.zero_grad()
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        loss.backward()
        optimizer.step()
        
        # Update metrics
        running_loss += loss.item() * images.size(0)
        
        _, predicted = torch.max(outputs.data, 1)
        correct_predictions += (predicted == labels).sum().item()
        total_samples += labels.size(0)
        
        # Update progress bar
        current_acc = correct_predictions / total_samples
        progress_bar.set_postfix({
            'loss': running_loss / total_samples,
            'acc': current_acc
        })
    
    epoch_loss = running_loss / total_samples
    epoch_accuracy = correct_predictions / total_samples
    
    return {
        'loss': epoch_loss,
        'accuracy': epoch_accuracy
    }


def validate_epoch(
    model: nn.Module,
    val_loader: DataLoader,
    criterion: nn.Module,
    device: str,
    epoch: int,
    total_epochs: int
) -> Dict[str, float]:
    """
    Validate for one epoch.
    
    Args:
        model: PyTorch model
        val_loader: Validation dataloader
        criterion: Loss function
        device: Device to run on
        epoch: Current epoch number
        total_epochs: Total number of epochs
        
    Returns:
        Dict with epoch metrics (loss, accuracy)
    """
    model.eval()
    
    running_loss = 0.0
    correct_predictions = 0
    total_samples = 0
    
    progress_bar = tqdm.tqdm(
        val_loader,
        desc=f"Epoch {epoch+1}/{total_epochs} [Val]",
        unit='batch'
    )
    
    with torch.no_grad():
        for images, labels in progress_bar:
            # Move to device
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Update metrics
            running_loss += loss.item() * images.size(0)
            
            _, predicted = torch.max(outputs.data, 1)
            correct_predictions += (predicted == labels).sum().item()
            total_samples += labels.size(0)
            
            # Update progress bar
            current_acc = correct_predictions / total_samples
            progress_bar.set_postfix({
                'loss': running_loss / total_samples,
                'acc': current_acc
            })
    
    epoch_loss = running_loss / total_samples
    epoch_accuracy = correct_predictions / total_samples
    
    return {
        'loss': epoch_loss,
        'accuracy': epoch_accuracy
    }


class EarlyStopping:
    """Early stopping callback."""
    
    def __init__(self, patience: int = 10, verbose: bool = True):
        """
        Initialize early stopping.
        
        Args:
            patience: Number of epochs with no improvement to wait
            verbose: Whether to print messages
        """
        self.patience = patience
        self.verbose = verbose
        self.counter = 0
        self.best_loss = None
        self.early_stop = False
    
    def __call__(self, val_loss: float) -> bool:
        """
        Check if training should stop.
        
        Args:
            val_loss: Current validation loss
            
        Returns:
            True if training should stop
        """
        if self.best_loss is None:
            self.best_loss = val_loss
        elif val_loss < self.best_loss:
            self.best_loss = val_loss
            self.counter = 0
            if self.verbose:
                logger.info(f"✓ Validation loss improved to {val_loss:.4f}")
        else:
            self.counter += 1
            if self.verbose:
                logger.info(
                    f"✗ Validation loss did not improve. "
                    f"({self.counter}/{self.patience})"
                )
            
            if self.counter >= self.patience:
                self.early_stop = True
        
        return self.early_stop


def train_model(
    config: TrainingConfig,
    class_to_idx: Dict[str, int],
) -> Dict:
    """
    Train classifier model.
    
    Args:
        config: Training configuration
        class_to_idx: Mapping of class names to indices
        
    Returns:
        Dict with training history
    """
    logger.info("\n" + "="*70)
    logger.info("TRAINING CLASSIFIER")
    logger.info("="*70)
    logger.info(f"\n{config}\n")
    
    # Create dataloaders
    augmentation_config = AugmentationConfig()
    train_loader, val_loader, num_classes = get_dataloaders(
        config,
        class_to_idx,
        augmentation_config
    )
    
    # Build model
    model = build_model(config.model_name, num_classes, config.device)
    
    # Setup training
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(
        model.parameters(),
        lr=config.learning_rate,
        weight_decay=config.weight_decay
    )
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(
        optimizer,
        mode='min',
        factor=0.1,
        patience=5,
        verbose=True
    )
    early_stopping = EarlyStopping(patience=config.patience)
    
    # Training history
    history = {
        'train_loss': [],
        'train_accuracy': [],
        'val_loss': [],
        'val_accuracy': [],
        'epochs': 0
    }
    
    best_model_path = config.output_dir / 'skin_classifier_best.pth'
    best_val_accuracy = 0.0
    
    logger.info(f"\nTraining on device: {config.device}")
    logger.info(f"Model: {config.model_name}")
    logger.info(f"Epochs: {config.epochs}")
    logger.info(f"Learning rate: {config.learning_rate}")
    logger.info(f"Batch size: {config.batch_size}\n")
    
    # Training loop
    start_time = datetime.now()
    
    for epoch in range(config.epochs):
        logger.info(f"\n--- Epoch {epoch+1}/{config.epochs} ---")
        
        # Train
        train_metrics = train_epoch(
            model,
            train_loader,
            criterion,
            optimizer,
            config.device,
            epoch,
            config.epochs
        )
        
        # Validate
        val_metrics = validate_epoch(
            model,
            val_loader,
            criterion,
            config.device,
            epoch,
            config.epochs
        )
        
        # Update history
        history['train_loss'].append(train_metrics['loss'])
        history['train_accuracy'].append(train_metrics['accuracy'])
        history['val_loss'].append(val_metrics['loss'])
        history['val_accuracy'].append(val_metrics['accuracy'])
        history['epochs'] = epoch + 1
        
        # Log metrics
        logger.info(
            f"\nMetrics: "
            f"train_loss={train_metrics['loss']:.4f}, "
            f"train_acc={train_metrics['accuracy']:.4f}, "
            f"val_loss={val_metrics['loss']:.4f}, "
            f"val_acc={val_metrics['accuracy']:.4f}"
        )
        
        # Learning rate scheduling
        scheduler.step(val_metrics['loss'])
        
        # Save best model
        if val_metrics['accuracy'] > best_val_accuracy:
            best_val_accuracy = val_metrics['accuracy']
            logger.info(f"✓ Saving best model (acc={best_val_accuracy:.4f})")
            torch.save(model.state_dict(), best_model_path)
        
        # Early stopping
        if early_stopping(val_metrics['loss']):
            logger.info(f"\nEarly stopping triggered at epoch {epoch+1}")
            break
    
    # Training finished
    elapsed_time = datetime.now() - start_time
    logger.info(f"\nTraining finished in {elapsed_time}")
    
    # Save final model
    final_model_path = config.output_dir / 'skin_classifier.pth'
    torch.save(model.state_dict(), final_model_path)
    logger.info(f"✓ Final model saved: {final_model_path}")
    
    # Save class mapping
    class_mapping_path = config.output_dir / 'class_mapping.json'
    with open(class_mapping_path, 'w') as f:
        json.dump(class_to_idx, f, indent=2)
    logger.info(f"✓ Class mapping saved: {class_mapping_path}")
    
    # Prepare metrics for export
    history['config'] = {
        'model': config.model_name,
        'data_dir': str(config.data_dir),
        'epochs': config.epochs,
        'batch_size': config.batch_size,
        'learning_rate': config.learning_rate,
        'device': config.device,
    }
    history['best_val_accuracy'] = float(best_val_accuracy)
    history['best_val_loss'] = float(min(history['val_loss']))
    history['elapsed_time_seconds'] = elapsed_time.total_seconds()
    
    return history


def save_metrics(history: Dict, output_path: Path):
    """
    Save training metrics to JSON.
    
    Args:
        history: Training history dict
        output_path: Path to save metrics
    """
    # Convert numpy arrays to lists for JSON serialization
    metrics = {
        'train_loss': [float(x) for x in history['train_loss']],
        'train_accuracy': [float(x) for x in history['train_accuracy']],
        'val_loss': [float(x) for x in history['val_loss']],
        'val_accuracy': [float(x) for x in history['val_accuracy']],
        'config': history['config'],
        'best_val_accuracy': history['best_val_accuracy'],
        'best_val_loss': history['best_val_loss'],
        'elapsed_time_seconds': history['elapsed_time_seconds'],
        'num_epochs_trained': history['epochs'],
    }
    
    with open(output_path, 'w') as f:
        json.dump(metrics, f, indent=2)
    
    logger.info(f"✓ Metrics saved: {output_path}")


def main():
    """Main training script."""
    parser = argparse.ArgumentParser(
        description='Train skin classifier using transfer learning'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        required=True,
        help='Directory containing dataset (class folders or train/val folders)'
    )
    parser.add_argument(
        '--model',
        type=str,
        default='efficientnet_b0',
        choices=['efficientnet_b0', 'resnet50'],
        help='Model architecture'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of training epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for training'
    )
    parser.add_argument(
        '--lr',
        type=float,
        default=0.001,
        help='Learning rate'
    )
    parser.add_argument(
        '--weight-decay',
        type=float,
        default=1e-4,
        help='Weight decay (L2 regularization)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='ml/exports',
        help='Output directory for models and metrics'
    )
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        help='Device to use (auto-detect if not specified)'
    )
    parser.add_argument(
        '--num-workers',
        type=int,
        default=4,
        help='Number of DataLoader workers'
    )
    parser.add_argument(
        '--patience',
        type=int,
        default=10,
        help='Early stopping patience (epochs)'
    )
    parser.add_argument(
        '--val-split',
        type=float,
        default=0.2,
        help='Validation split ratio if no val folder'
    )
    
    args = parser.parse_args()
    
    # Validate data directory
    data_dir = Path(args.data_dir)
    if not data_dir.exists():
        logger.error(f"Data directory not found: {data_dir}")
        sys.exit(1)
    
    # Detect classes
    train_dir = data_dir / 'train'
    val_dir = data_dir / 'val'
    
    if train_dir.exists():
        class_dirs = sorted([d for d in train_dir.iterdir() if d.is_dir()])
    else:
        class_dirs = sorted([d for d in data_dir.iterdir() if d.is_dir()])
    
    if not class_dirs:
        logger.error(f"No class directories found in {data_dir}")
        sys.exit(1)
    
    # Create class mapping
    class_to_idx = {d.name: idx for idx, d in enumerate(class_dirs)}
    num_classes = len(class_to_idx)
    
    logger.info(f"Found {num_classes} classes: {list(class_to_idx.keys())}")
    
    # Create training config
    config = TrainingConfig(
        data_dir=args.data_dir,
        model_name=args.model,
        epochs=args.epochs,
        batch_size=args.batch_size,
        learning_rate=args.lr,
        weight_decay=args.weight_decay,
        output_dir=args.output,
        device=args.device,
        num_workers=args.num_workers,
        patience=args.patience,
        val_split=args.val_split,
    )
    
    # Train model
    history = train_model(config, class_to_idx)
    
    # Save metrics
    metrics_path = Path(args.output) / 'classifier_metrics.json'
    save_metrics(history, metrics_path)
    
    logger.info("\n" + "="*70)
    logger.info("TRAINING COMPLETE")
    logger.info("="*70)
    logger.info(f"Models saved to: {config.output_dir}")
    logger.info(f"Best model: skin_classifier_best.pth")
    logger.info(f"Final model: skin_classifier.pth")
    logger.info(f"Metrics: classifier_metrics.json")
    logger.info(f"Class mapping: class_mapping.json")
    logger.info("="*70 + "\n")


if __name__ == '__main__':
    main()
