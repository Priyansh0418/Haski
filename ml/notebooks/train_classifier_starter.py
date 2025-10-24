#!/usr/bin/env python3
"""
╔════════════════════════════════════════════════════════════════════════════╗
║                                                                            ║
║          HASKI SKIN CLASSIFIER - TRAINING STARTER NOTEBOOK               ║
║                                                                            ║
║  A beginner-friendly guide to training a skin classifier using PyTorch   ║
║  with transfer learning, data loading, visualization, and checkpointing.  ║
║                                                                            ║
╚════════════════════════════════════════════════════════════════════════════╝

NOTEBOOK STYLE: This script is organized like a Jupyter notebook with
                 commented sections that you can run step-by-step.

COLAB SETUP:
    # Uncomment and run these cells first in Google Colab:
    # !pip install torch torchvision pillow numpy matplotlib
    # from google.colab import drive
    # drive.mount('/content/drive')
    # %cd /content/drive/MyDrive/Haski  # Change path to your Haski directory

TABLE OF CONTENTS:
    1. Setup & Imports
    2. Configuration
    3. Dataset Loading (ImageFolder)
    4. Data Visualization
    5. Model Creation (Pretrained Transfer Learning)
    6. Training Loop (Single Epoch)
    7. Checkpoint Saving
    8. Inference & Evaluation
    9. Next Steps

═══════════════════════════════════════════════════════════════════════════
CELL 1: SETUP & IMPORTS
═══════════════════════════════════════════════════════════════════════════
"""

print("╔════════════════════════════════════════════════════════════════════════════╗")
print("║                     CELL 1: SETUP & IMPORTS                                ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# Standard library imports
import os
import sys
import json
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
from collections import defaultdict

# Third-party imports
import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
from torchvision.models import EfficientNet_B0_Weights
from PIL import Image
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Configure device
DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print(f"✓ Device: {DEVICE}")
print(f"✓ PyTorch Version: {torch.__version__}")
print(f"✓ CUDA Available: {torch.cuda.is_available()}")
if torch.cuda.is_available():
    print(f"  GPU: {torch.cuda.get_device_name(0)}")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 2: CONFIGURATION
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                     CELL 2: CONFIGURATION                                  ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Configuration Class
# ============================================================================

class TrainConfig:
    """Training configuration - adjust these parameters."""
    
    # Dataset
    DATASET_PATH = Path("ml/data/skin_classification")  # ImageFolder structure
    BATCH_SIZE = 32
    NUM_WORKERS = 4
    VAL_SPLIT = 0.2  # 80% train, 20% val
    RANDOM_SEED = 42
    
    # Model
    MODEL_NAME = "efficientnet_b0"  # or "resnet50"
    NUM_CLASSES = 5  # normal, dry, oily, combination, sensitive
    PRETRAINED = True
    
    # Training
    EPOCHS = 1  # Start with 1 for smoke test
    LEARNING_RATE = 0.001
    WEIGHT_DECAY = 1e-4
    WARMUP_EPOCHS = 1
    
    # Paths
    OUTPUT_DIR = Path("ml/exports/checkpoints")
    CHECKPOINT_NAME = f"skin_classifier_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    # Paths for Colab
    IS_COLAB = 'google.colab' in sys.modules
    if IS_COLAB:
        DATASET_PATH = Path("/content/drive/MyDrive/Haski/ml/data/skin_classification")
        OUTPUT_DIR = Path("/content/drive/MyDrive/Haski/ml/exports/checkpoints")
    
    @classmethod
    def to_dict(cls):
        return {k: str(v) if isinstance(v, Path) else v 
                for k, v in vars(cls).items() if not k.startswith('_')}


# Create output directory
TrainConfig.OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

print("✓ Configuration Loaded:")
for key, value in TrainConfig.to_dict().items():
    if not key.startswith("IS_"):
        print(f"  {key}: {value}")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 3: DATA TRANSFORMS
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                     CELL 3: DATA TRANSFORMS                                ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Image Transforms for Training & Validation
# ============================================================================

# ImageNet normalization statistics
IMAGENET_MEAN = [0.485, 0.456, 0.406]
IMAGENET_STD = [0.229, 0.224, 0.225]

# Training transforms (with augmentation)
train_transforms = transforms.Compose([
    transforms.RandomResizedCrop(224, scale=(0.8, 1.0)),  # Random crop & resize
    transforms.RandomHorizontalFlip(p=0.5),               # Random horizontal flip
    transforms.RandomRotation(15),                         # Random rotation ±15°
    transforms.ColorJitter(
        brightness=0.2,
        contrast=0.2,
        saturation=0.2,
        hue=0.1
    ),                                                     # Color jittering
    transforms.ToTensor(),                                 # Convert to tensor [0,1]
    transforms.Normalize(
        mean=IMAGENET_MEAN,
        std=IMAGENET_STD
    )                                                      # Normalize
])

# Validation transforms (no augmentation)
val_transforms = transforms.Compose([
    transforms.Resize(256),                                # Resize to 256
    transforms.CenterCrop(224),                            # Center crop to 224
    transforms.ToTensor(),                                 # Convert to tensor
    transforms.Normalize(
        mean=IMAGENET_MEAN,
        std=IMAGENET_STD
    )                                                      # Normalize
])

print("✓ Training Transforms:")
print("  - RandomResizedCrop(224)")
print("  - RandomHorizontalFlip(0.5)")
print("  - RandomRotation(15°)")
print("  - ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1)")
print("  - Normalize (ImageNet statistics)")
print("\n✓ Validation Transforms:")
print("  - Resize(256) → CenterCrop(224)")
print("  - Normalize (ImageNet statistics)")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 4: DATASET LOADING (ImageFolder)
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                  CELL 4: DATASET LOADING (ImageFolder)                      ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Load Dataset with ImageFolder
# ============================================================================

try:
    # Load entire dataset
    dataset = datasets.ImageFolder(
        root=str(TrainConfig.DATASET_PATH),
        transform=val_transforms  # Will be updated per split
    )
    
    print(f"✓ Dataset loaded from: {TrainConfig.DATASET_PATH}")
    print(f"  Total samples: {len(dataset)}")
    print(f"  Classes: {dataset.classes}")
    print(f"  Class to index: {dataset.class_to_idx}")
    
    # Create class labels mapping
    CLASS_NAMES = dataset.classes
    NUM_CLASSES = len(CLASS_NAMES)
    
except Exception as e:
    print(f"✗ Error loading dataset: {e}")
    print("\n📌 Expected dataset structure:")
    print("   dataset_path/")
    print("   ├── class1/")
    print("   │   ├── image1.jpg")
    print("   │   ├── image2.jpg")
    print("   │   └── ...")
    print("   ├── class2/")
    print("   │   ├── image1.jpg")
    print("   │   └── ...")
    print("   └── ...")
    print("\n   Using mock dataset for demonstration...")
    
    # Create a mock dataset for demonstration
    CLASS_NAMES = ['normal', 'dry', 'oily', 'combination', 'sensitive']
    NUM_CLASSES = len(CLASS_NAMES)
    dataset = None


# Split dataset if it was loaded
if dataset is not None:
    train_size = int(len(dataset) * (1 - TrainConfig.VAL_SPLIT))
    val_size = len(dataset) - train_size
    train_dataset, val_dataset = torch.utils.data.random_split(
        dataset,
        [train_size, val_size]
    )
    
    # Update transforms for splits
    train_dataset.dataset.transform = train_transforms
    val_dataset.dataset.transform = val_transforms
    
    print(f"\n✓ Dataset split:")
    print(f"  Training samples: {train_size}")
    print(f"  Validation samples: {val_size}")
else:
    print(f"\n✓ Classes: {CLASS_NAMES}")
    train_dataset = None
    val_dataset = None


"""
═══════════════════════════════════════════════════════════════════════════
CELL 5: DATA VISUALIZATION
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                  CELL 5: DATA VISUALIZATION                                 ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Visualize Training Images
# ============================================================================

def plot_image_grid(images_list: List[Tuple[torch.Tensor, int]], 
                   class_names: List[str],
                   title: str = "Sample Training Images",
                   denorm: bool = True):
    """
    Plot a grid of images with their class labels.
    
    Args:
        images_list: List of (image_tensor, class_idx) tuples
        class_names: List of class names
        title: Plot title
        denorm: Whether to denormalize images
    """
    fig, axes = plt.subplots(2, 3, figsize=(15, 10))
    fig.suptitle(title, fontsize=16, fontweight='bold')
    axes = axes.flatten()
    
    for idx, (ax, (img, label)) in enumerate(zip(axes, images_list)):
        # Denormalize if needed
        if denorm and img.shape[0] == 3:
            img = img.clone()
            for i, (mean, std) in enumerate(zip(IMAGENET_MEAN, IMAGENET_STD)):
                img[i] = img[i] * std + mean
        
        # Convert to numpy and transpose
        if isinstance(img, torch.Tensor):
            img_np = img.numpy().transpose(1, 2, 0)
            img_np = np.clip(img_np, 0, 1)
        else:
            img_np = img
        
        # Plot
        ax.imshow(img_np)
        class_name = class_names[label] if label < len(class_names) else f"Class {label}"
        ax.set_title(class_name, fontsize=12, fontweight='bold')
        ax.axis('off')
    
    # Hide unused subplots
    for idx in range(len(images_list), len(axes)):
        axes[idx].axis('off')
    
    plt.tight_layout()
    return fig


# Visualize if dataset is available
if train_dataset is not None and len(train_dataset) > 0:
    print("✓ Visualizing training samples...")
    sample_images = []
    try:
        # Get diverse samples (one per class if possible)
        class_counts = defaultdict(int)
        for i in range(min(100, len(train_dataset))):
            img, label = train_dataset[i]
            if class_counts[label] < 1:
                sample_images.append((img, label))
                class_counts[label] += 1
            if len(sample_images) == 6:
                break
        
        if sample_images:
            fig = plot_image_grid(sample_images, CLASS_NAMES, "Sample Training Images")
            plt.savefig(TrainConfig.OUTPUT_DIR / "sample_images.png", dpi=100, bbox_inches='tight')
            print(f"  Saved to: {TrainConfig.OUTPUT_DIR / 'sample_images.png'}")
            plt.close()
    except Exception as e:
        print(f"  Warning: Could not visualize images: {e}")
else:
    print("⚠ No training dataset available for visualization")


# Plot augmentation examples
print("\n✓ Example transforms applied to images:")
print("  - Original → Augmented versions (training)")
print("  - Random crop, flip, rotation, color jitter")
print("  - Validation uses center crop (no augmentation)")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 6: CREATE PRETRAINED MODEL (Transfer Learning)
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║            CELL 6: CREATE PRETRAINED MODEL (Transfer Learning)             ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Create Model
# ============================================================================

def create_model(model_name: str = "efficientnet_b0",
                num_classes: int = 5,
                pretrained: bool = True) -> nn.Module:
    """
    Create a pretrained model for transfer learning.
    
    Args:
        model_name: Model name ('efficientnet_b0' or 'resnet50')
        num_classes: Number of output classes
        pretrained: Use pretrained weights
    
    Returns:
        Model with modified classification head
    """
    print(f"✓ Creating {model_name} model (pretrained={pretrained})...")
    
    if model_name.lower() == "efficientnet_b0":
        # Create EfficientNet-B0
        if pretrained:
            model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        else:
            model = models.efficientnet_b0(weights=None)
        
        # Get input features of the classification head
        num_features = model.classifier[1].in_features
        
        # Replace classification head
        model.classifier[1] = nn.Linear(num_features, num_classes)
        
        print(f"  - Model: EfficientNet-B0")
        print(f"  - Input: (B, 3, 224, 224)")
        print(f"  - Output: (B, {num_classes})")
        print(f"  - Pretrained backbone: {pretrained}")
        
    elif model_name.lower() == "resnet50":
        # Create ResNet50
        from torchvision.models import ResNet50_Weights
        if pretrained:
            model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        else:
            model = models.resnet50(weights=None)
        
        # Get number of input features
        num_features = model.fc.in_features
        
        # Replace final linear layer
        model.fc = nn.Linear(num_features, num_classes)
        
        print(f"  - Model: ResNet50")
        print(f"  - Input: (B, 3, 224, 224)")
        print(f"  - Output: (B, {num_classes})")
        print(f"  - Pretrained backbone: {pretrained}")
    
    else:
        raise ValueError(f"Unknown model: {model_name}")
    
    return model


# Create model
model = create_model(
    model_name=TrainConfig.MODEL_NAME,
    num_classes=NUM_CLASSES,
    pretrained=TrainConfig.PRETRAINED
)

# Move to device
model = model.to(DEVICE)

# Print model architecture (summary)
print(f"\n✓ Model moved to device: {DEVICE}")

# Count parameters
total_params = sum(p.numel() for p in model.parameters())
trainable_params = sum(p.numel() for p in model.parameters() if p.requires_grad)
print(f"  Total parameters: {total_params:,}")
print(f"  Trainable parameters: {trainable_params:,}")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 7: SETUP TRAINING
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                     CELL 7: SETUP TRAINING                                 ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Setup Loss, Optimizer, and Learning Rate Scheduler
# ============================================================================

# Loss function
criterion = nn.CrossEntropyLoss()
print("✓ Loss Function: CrossEntropyLoss")

# Optimizer (Adam)
optimizer = optim.Adam(
    model.parameters(),
    lr=TrainConfig.LEARNING_RATE,
    weight_decay=TrainConfig.WEIGHT_DECAY
)
print(f"✓ Optimizer: Adam")
print(f"  - Learning Rate: {TrainConfig.LEARNING_RATE}")
print(f"  - Weight Decay: {TrainConfig.WEIGHT_DECAY}")

# Learning rate scheduler (reduce on plateau)
scheduler = optim.lr_scheduler.ReduceLROnPlateau(
    optimizer,
    mode='min',
    factor=0.5,
    patience=3,
    verbose=True
)
print(f"✓ LR Scheduler: ReduceLROnPlateau")
print(f"  - Factor: 0.5")
print(f"  - Patience: 3 epochs")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 8: TRAINING LOOP (Single Epoch)
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                  CELL 8: TRAINING LOOP (Single Epoch)                       ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Training & Validation Functions
# ============================================================================

def train_epoch(model, dataloader, criterion, optimizer, device):
    """
    Train for one epoch.
    
    Returns:
        avg_loss: Average loss over the epoch
        accuracy: Classification accuracy
    """
    model.train()
    total_loss = 0.0
    correct = 0
    total = 0
    
    print("  Training...")
    for batch_idx, (images, labels) in enumerate(dataloader):
        images, labels = images.to(device), labels.to(device)
        
        # Forward pass
        outputs = model(images)
        loss = criterion(outputs, labels)
        
        # Backward pass
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()
        
        # Accumulate metrics
        total_loss += loss.item()
        _, predicted = outputs.max(1)
        correct += predicted.eq(labels).sum().item()
        total += labels.size(0)
        
        # Print progress
        if (batch_idx + 1) % max(1, len(dataloader) // 5) == 0:
            acc = 100.0 * correct / total
            avg_loss = total_loss / (batch_idx + 1)
            print(f"    Batch {batch_idx+1}/{len(dataloader)}: "
                  f"Loss={avg_loss:.4f}, Acc={acc:.2f}%")
    
    avg_loss = total_loss / len(dataloader)
    accuracy = 100.0 * correct / total
    
    return avg_loss, accuracy


def validate_epoch(model, dataloader, criterion, device):
    """
    Validate for one epoch.
    
    Returns:
        avg_loss: Average loss over the epoch
        accuracy: Classification accuracy
    """
    model.eval()
    total_loss = 0.0
    correct = 0
    total = 0
    
    print("  Validating...")
    with torch.no_grad():
        for batch_idx, (images, labels) in enumerate(dataloader):
            images, labels = images.to(device), labels.to(device)
            
            # Forward pass
            outputs = model(images)
            loss = criterion(outputs, labels)
            
            # Accumulate metrics
            total_loss += loss.item()
            _, predicted = outputs.max(1)
            correct += predicted.eq(labels).sum().item()
            total += labels.size(0)
    
    avg_loss = total_loss / len(dataloader)
    accuracy = 100.0 * correct / total
    
    return avg_loss, accuracy


# Create data loaders
if train_dataset is not None:
    train_loader = DataLoader(
        train_dataset,
        batch_size=TrainConfig.BATCH_SIZE,
        shuffle=True,
        num_workers=TrainConfig.NUM_WORKERS,
        pin_memory=True if DEVICE.type == 'cuda' else False
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=TrainConfig.BATCH_SIZE,
        shuffle=False,
        num_workers=TrainConfig.NUM_WORKERS,
        pin_memory=True if DEVICE.type == 'cuda' else False
    )
    
    print(f"✓ DataLoaders created:")
    print(f"  Train batches: {len(train_loader)}")
    print(f"  Val batches: {len(val_loader)}")
    print(f"  Batch size: {TrainConfig.BATCH_SIZE}")
    
    # ========================================================================
    # Training Loop
    # ========================================================================
    
    print(f"\n✓ Starting training for {TrainConfig.EPOCHS} epoch(s)...\n")
    
    metrics_history = {
        'train_loss': [],
        'train_acc': [],
        'val_loss': [],
        'val_acc': []
    }
    
    for epoch in range(TrainConfig.EPOCHS):
        print(f"Epoch {epoch+1}/{TrainConfig.EPOCHS}")
        
        # Train
        train_loss, train_acc = train_epoch(
            model, train_loader, criterion, optimizer, DEVICE
        )
        metrics_history['train_loss'].append(train_loss)
        metrics_history['train_acc'].append(train_acc)
        
        # Validate
        val_loss, val_acc = validate_epoch(
            model, val_loader, criterion, DEVICE
        )
        metrics_history['val_loss'].append(val_loss)
        metrics_history['val_acc'].append(val_acc)
        
        # Print summary
        print(f"\n  ✓ Train Loss: {train_loss:.4f}, Acc: {train_acc:.2f}%")
        print(f"  ✓ Val Loss: {val_loss:.4f}, Acc: {val_acc:.2f}%\n")
        
        # Step scheduler
        scheduler.step(val_loss)
    
    print("✓ Training complete!")

else:
    print("⚠ No dataset available, skipping training loop")
    metrics_history = {'train_loss': [], 'train_acc': [], 'val_loss': [], 'val_acc': []}


"""
═══════════════════════════════════════════════════════════════════════════
CELL 9: VISUALIZE TRAINING METRICS
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                  CELL 9: VISUALIZE TRAINING METRICS                         ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Plot Training Curves
# ============================================================================

if metrics_history['train_loss']:
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Loss curve
    ax1.plot(metrics_history['train_loss'], label='Train', marker='o')
    ax1.plot(metrics_history['val_loss'], label='Val', marker='s')
    ax1.set_xlabel('Epoch')
    ax1.set_ylabel('Loss')
    ax1.set_title('Training & Validation Loss')
    ax1.legend()
    ax1.grid(True, alpha=0.3)
    
    # Accuracy curve
    ax2.plot(metrics_history['train_acc'], label='Train', marker='o')
    ax2.plot(metrics_history['val_acc'], label='Val', marker='s')
    ax2.set_xlabel('Epoch')
    ax2.set_ylabel('Accuracy (%)')
    ax2.set_title('Training & Validation Accuracy')
    ax2.legend()
    ax2.grid(True, alpha=0.3)
    
    plt.tight_layout()
    plt.savefig(TrainConfig.OUTPUT_DIR / "training_curves.png", dpi=100, bbox_inches='tight')
    print(f"✓ Saved training curves to: {TrainConfig.OUTPUT_DIR / 'training_curves.png'}")
    plt.close()


"""
═══════════════════════════════════════════════════════════════════════════
CELL 10: SAVE CHECKPOINT
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                     CELL 10: SAVE CHECKPOINT                               ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Save Model Checkpoint
# ============================================================================

def save_checkpoint(model, optimizer, epoch, metrics, config, output_dir, name):
    """
    Save training checkpoint.
    
    Args:
        model: Model to save
        optimizer: Optimizer state
        epoch: Current epoch
        metrics: Training metrics
        config: Training configuration
        output_dir: Directory to save to
        name: Checkpoint name
    """
    checkpoint = {
        'epoch': epoch,
        'model_state_dict': model.state_dict(),
        'optimizer_state_dict': optimizer.state_dict(),
        'metrics': metrics,
        'config': config,
        'class_names': CLASS_NAMES,
        'num_classes': NUM_CLASSES,
        'model_name': TrainConfig.MODEL_NAME,
    }
    
    # Save as PyTorch checkpoint
    checkpoint_path = output_dir / f"{name}.pt"
    torch.save(checkpoint, checkpoint_path)
    print(f"✓ Checkpoint saved: {checkpoint_path}")
    
    # Also save model weights only (ONNX-friendly)
    weights_path = output_dir / f"{name}_weights.pth"
    torch.save(model.state_dict(), weights_path)
    print(f"✓ Model weights saved: {weights_path}")
    
    # Save metadata as JSON
    metadata = {
        'model_name': TrainConfig.MODEL_NAME,
        'num_classes': NUM_CLASSES,
        'class_names': CLASS_NAMES,
        'input_size': 224,
        'num_channels': 3,
        'epoch': epoch,
        'final_metrics': metrics,
        'timestamp': datetime.now().isoformat(),
    }
    metadata_path = output_dir / f"{name}_metadata.json"
    with open(metadata_path, 'w') as f:
        json.dump(metadata, f, indent=2)
    print(f"✓ Metadata saved: {metadata_path}")
    
    return checkpoint_path, weights_path, metadata_path


# Save checkpoint
if metrics_history['train_loss']:
    final_metrics = {
        'train_loss': metrics_history['train_loss'][-1],
        'train_acc': metrics_history['train_acc'][-1],
        'val_loss': metrics_history['val_loss'][-1],
        'val_acc': metrics_history['val_acc'][-1],
    }
else:
    final_metrics = {'train_loss': 0, 'train_acc': 0, 'val_loss': 0, 'val_acc': 0}

checkpoint_path, weights_path, metadata_path = save_checkpoint(
    model=model,
    optimizer=optimizer,
    epoch=TrainConfig.EPOCHS,
    metrics=final_metrics,
    config=TrainConfig.to_dict(),
    output_dir=TrainConfig.OUTPUT_DIR,
    name=TrainConfig.CHECKPOINT_NAME
)

print("\n✓ Training checkpoint saved successfully!")
print(f"\n  Checkpoint: {checkpoint_path}")
print(f"  Weights: {weights_path}")
print(f"  Metadata: {metadata_path}")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 11: INFERENCE & EVALUATION
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                  CELL 11: INFERENCE & EVALUATION                            ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

# ============================================================================
# Inference Function
# ============================================================================

def predict_single_image(model, image_path: str, device, class_names: List[str]):
    """
    Make prediction on a single image.
    
    Args:
        model: Trained model
        image_path: Path to image
        device: Device to use
        class_names: List of class names
    
    Returns:
        Prediction and confidence
    """
    model.eval()
    
    # Load and preprocess image
    image = Image.open(image_path).convert('RGB')
    image_tensor = val_transforms(image).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.nn.functional.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
    
    predicted_class = class_names[predicted.item()]
    confidence_score = confidence.item()
    
    return predicted_class, confidence_score, probabilities.cpu().numpy()[0]


# Example inference on a random validation image
if val_dataset is not None and len(val_dataset) > 0:
    print("✓ Example inference on validation set:\n")
    
    # Get a few random samples
    for i in range(min(3, len(val_dataset))):
        sample_idx = np.random.randint(0, len(val_dataset))
        image, true_label = val_dataset[sample_idx]
        true_class = CLASS_NAMES[true_label]
        
        # Inference
        model.eval()
        with torch.no_grad():
            image_batch = image.unsqueeze(0).to(DEVICE)
            outputs = model(image_batch)
            probs = torch.nn.functional.softmax(outputs, dim=1)
            confidence, predicted = torch.max(probs, 1)
        
        predicted_class = CLASS_NAMES[predicted.item()]
        confidence_score = confidence.item()
        
        status = "✓" if predicted.item() == true_label else "✗"
        print(f"  {status} True: {true_class:15} | Pred: {predicted_class:15} | Conf: {confidence_score:.4f}")
else:
    print("⚠ No validation data available for inference demo")


"""
═══════════════════════════════════════════════════════════════════════════
CELL 12: NEXT STEPS & RESOURCES
═══════════════════════════════════════════════════════════════════════════
"""

print("\n╔════════════════════════════════════════════════════════════════════════════╗")
print("║                     CELL 12: NEXT STEPS & RESOURCES                        ║")
print("╚════════════════════════════════════════════════════════════════════════════╝\n")

print("""
🎯 WHAT YOU LEARNED:

  1. ✓ Loading datasets with torchvision ImageFolder
  2. ✓ Applying augmentation transforms (training vs validation)
  3. ✓ Creating pretrained models (EfficientNet-B0, ResNet50)
  4. ✓ Single-epoch training loop with metrics tracking
  5. ✓ Saving checkpoints with model weights and metadata
  6. ✓ Inference and visualization

═══════════════════════════════════════════════════════════════════════════

📈 TRAINING METRICS:

  Final Training Loss: {:.4f}
  Final Training Accuracy: {:.2f}%
  Final Validation Loss: {:.4f}
  Final Validation Accuracy: {:.2f}%

═══════════════════════════════════════════════════════════════════════════

🚀 NEXT STEPS:

  1. Train for more epochs:
     - Change EPOCHS in Configuration
     - Run the training loop again
     - Monitor validation accuracy for overfitting

  2. Try different models:
     - Change MODEL_NAME to "resnet50"
     - Compare performance and speed

  3. Improve data augmentation:
     - Add more transforms (mixup, cutout, etc.)
     - Experiment with augmentation intensity

  4. Hyperparameter tuning:
     - Change learning rate, batch size
     - Try different optimizers (SGD, AdamW)
     - Experiment with different schedulers

  5. Export model for deployment:
     - Convert to ONNX: torch.onnx.export()
     - Convert to TFLite for mobile
     - Quantize for faster inference

═══════════════════════════════════════════════════════════════════════════

💡 COLAB SETUP:

  To run this in Google Colab:

  1. Copy this file to Google Drive
  2. Open in Colab
  3. Run these setup cells first:

     # Install dependencies
     !pip install torch torchvision pillow matplotlib

     # Mount Google Drive
     from google.colab import drive
     drive.mount('/content/drive')

     # Change to your Haski directory
     %cd /content/drive/MyDrive/Haski

  4. Change dataset path to:
     DATASET_PATH = "/content/drive/MyDrive/Haski/ml/data/skin_classification"

  5. Run cells sequentially!

═══════════════════════════════════════════════════════════════════════════

📚 RESOURCES:

  - PyTorch Docs: https://pytorch.org/docs/
  - TorchVision Models: https://pytorch.org/vision/stable/models.html
  - ImageNet Transfer Learning: https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html
  - EfficientNet: https://arxiv.org/abs/1905.11946
  - Data Augmentation: https://arxiv.org/abs/2104.14294

═══════════════════════════════════════════════════════════════════════════

✨ TIPS FOR BETTER RESULTS:

  ✓ Use balanced dataset (equal samples per class)
  ✓ Monitor train/val loss for overfitting
  ✓ Use learning rate scheduling
  ✓ Try different batch sizes (memory permitting)
  ✓ Use gradient accumulation for larger effective batch
  ✓ Monitor GPU memory usage
  ✓ Save best model, not just last epoch

═══════════════════════════════════════════════════════════════════════════
""".format(
    final_metrics['train_loss'],
    final_metrics['train_acc'],
    final_metrics['val_loss'],
    final_metrics['val_acc']
))

print("\n✅ Training notebook complete! Check ml/exports/checkpoints/ for saved models.\n")
