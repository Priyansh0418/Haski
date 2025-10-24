"""
Multi-Task Learning Framework for Skin Analysis

Advanced prototype implementing:
1. Shared EfficientNet backbone
2. Classification head (skin type, hair type)
3. Segmentation head (lesion localization using UNet decoder)

Features:
- Joint training with balanced loss
- Multi-task loss weighting
- Task-specific performance tracking
- Flexible dataset handling (TODO)
- PyTorch implementation with clear architecture

Usage:
    python train_multitask.py --data-dir data/ --epochs 100
    
Example inference:
    from train_multitask import MultiTaskModel
    model = MultiTaskModel.load('ml/exports/multitask_best.pth')
    results = model.predict('image.jpg')
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from collections import defaultdict
from datetime import datetime

import numpy as np
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader, Dataset
from torchvision import models
from torchvision.models import EfficientNet_B0_Weights
from PIL import Image
import tqdm

# Try to import PyTorch Lightning (optional)
try:
    import pytorch_lightning as pl
    LIGHTNING_AVAILABLE = True
except ImportError:
    LIGHTNING_AVAILABLE = False

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# ============================================================================
# Segmentation Decoder (UNet-style)
# ============================================================================

class SegmentationDecoder(nn.Module):
    """
    UNet-style decoder for lesion segmentation.
    
    Progressively upsamples from low-level features to generate segmentation mask.
    """
    
    def __init__(
        self,
        in_channels: int = 1280,  # EfficientNet-B0 output
        num_classes: int = 1,      # Binary segmentation (lesion vs no lesion)
    ):
        """
        Initialize segmentation decoder.
        
        Args:
            in_channels: Input channels from backbone
            num_classes: Number of segmentation classes (1 for binary)
        """
        super().__init__()
        
        # Decoder blocks with progressive upsampling
        self.decoder1 = self._decoder_block(in_channels, 512, upsample=2)
        self.decoder2 = self._decoder_block(512, 256, upsample=2)
        self.decoder3 = self._decoder_block(256, 128, upsample=2)
        self.decoder4 = self._decoder_block(128, 64, upsample=2)
        
        # Final segmentation head
        self.final_conv = nn.Sequential(
            nn.Conv2d(64, 32, kernel_size=3, padding=1),
            nn.BatchNorm2d(32),
            nn.ReLU(inplace=True),
            nn.Conv2d(32, num_classes, kernel_size=1),
        )
    
    @staticmethod
    def _decoder_block(
        in_channels: int,
        out_channels: int,
        upsample: int = 2,
    ) -> nn.Module:
        """Create a decoder block with upsampling."""
        return nn.Sequential(
            nn.Upsample(scale_factor=upsample, mode='bilinear', align_corners=False),
            nn.Conv2d(in_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
            nn.Conv2d(out_channels, out_channels, kernel_size=3, padding=1),
            nn.BatchNorm2d(out_channels),
            nn.ReLU(inplace=True),
        )
    
    def forward(self, x: torch.Tensor) -> torch.Tensor:
        """Forward pass through decoder."""
        x = self.decoder1(x)
        x = self.decoder2(x)
        x = self.decoder3(x)
        x = self.decoder4(x)
        x = self.final_conv(x)
        return x


# ============================================================================
# Multi-Task Model
# ============================================================================

class MultiTaskModel(nn.Module):
    """
    Multi-task learning model with shared backbone and dual heads.
    
    Architecture:
    - Backbone: EfficientNet-B0 (pre-trained ImageNet)
    - Head 1: Classification (skin type, hair type)
    - Head 2: Segmentation (lesion localization)
    """
    
    def __init__(
        self,
        num_classes_classification: int = 10,  # skin types (5) + hair types (5)
        num_classes_segmentation: int = 1,      # Binary segmentation
        backbone_freeze: bool = False,
    ):
        """
        Initialize multi-task model.
        
        Args:
            num_classes_classification: Number of classification classes
            num_classes_segmentation: Number of segmentation classes
            backbone_freeze: Whether to freeze backbone weights (for transfer learning)
        """
        super().__init__()
        
        self.num_classes_classification = num_classes_classification
        self.num_classes_segmentation = num_classes_segmentation
        
        # ====================================================================
        # Shared Backbone (EfficientNet-B0)
        # ====================================================================
        self.backbone = models.efficientnet_b0(
            weights=EfficientNet_B0_Weights.IMAGENET1K_V1
        )
        
        # Remove classification head
        self.backbone = nn.Sequential(*list(self.backbone.children())[:-2])
        
        # Optionally freeze backbone
        if backbone_freeze:
            for param in self.backbone.parameters():
                param.requires_grad = False
        
        backbone_out_channels = 1280  # EfficientNet-B0 output channels
        
        # ====================================================================
        # Head 1: Classification Head
        # ====================================================================
        self.classification_head = nn.Sequential(
            nn.AdaptiveAvgPool2d((1, 1)),
            nn.Flatten(),
            nn.Linear(backbone_out_channels, 512),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(512, 256),
            nn.ReLU(inplace=True),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes_classification),
        )
        
        # ====================================================================
        # Head 2: Segmentation Head (UNet Decoder)
        # ====================================================================
        self.segmentation_head = SegmentationDecoder(
            in_channels=backbone_out_channels,
            num_classes=num_classes_segmentation,
        )
    
    def forward(
        self,
        x: torch.Tensor,
        return_backbone_features: bool = False,
    ) -> Tuple[torch.Tensor, torch.Tensor, Optional[torch.Tensor]]:
        """
        Forward pass through multi-task model.
        
        Args:
            x: Input image tensor (batch_size, 3, 224, 224)
            return_backbone_features: Return intermediate features for analysis
            
        Returns:
            Tuple of:
            - Classification logits (batch_size, num_classes_classification)
            - Segmentation logits (batch_size, 1, H, W)
            - Backbone features (if return_backbone_features=True)
        """
        # Backbone forward pass
        backbone_features = self.backbone(x)
        
        # Task 1: Classification
        classification_logits = self.classification_head(backbone_features)
        
        # Task 2: Segmentation
        segmentation_logits = self.segmentation_head(backbone_features)
        
        if return_backbone_features:
            return classification_logits, segmentation_logits, backbone_features
        
        return classification_logits, segmentation_logits, None
    
    @staticmethod
    def load(checkpoint_path: str, device: str = 'cpu') -> 'MultiTaskModel':
        """
        Load model from checkpoint.
        
        Args:
            checkpoint_path: Path to .pth checkpoint
            device: Device to load model on
            
        Returns:
            Loaded model
        """
        checkpoint = torch.load(checkpoint_path, map_location=device)
        
        # Extract config
        config = checkpoint.get('config', {})
        model = MultiTaskModel(
            num_classes_classification=config.get('num_classes_classification', 10),
            num_classes_segmentation=config.get('num_classes_segmentation', 1),
        )
        
        # Load state dict
        model.load_state_dict(checkpoint['state_dict'])
        model = model.to(device)
        model.eval()
        
        return model
    
    def save_checkpoint(
        self,
        path: str,
        optimizer: Optional[optim.Optimizer] = None,
        epoch: int = 0,
        metrics: Optional[Dict] = None,
    ):
        """
        Save model checkpoint.
        
        Args:
            path: Path to save checkpoint
            optimizer: Optimizer state (optional)
            epoch: Current epoch
            metrics: Training metrics (optional)
        """
        checkpoint = {
            'state_dict': self.state_dict(),
            'config': {
                'num_classes_classification': self.num_classes_classification,
                'num_classes_segmentation': self.num_classes_segmentation,
            },
            'epoch': epoch,
            'metrics': metrics or {},
        }
        
        if optimizer:
            checkpoint['optimizer'] = optimizer.state_dict()
        
        torch.save(checkpoint, path)
        logger.info(f"✓ Checkpoint saved: {path}")
    
    def predict(
        self,
        image_path: str,
        device: str = 'cpu',
        conf_thresh: float = 0.5,
    ) -> Dict[str, Any]:
        """
        Run inference on single image.
        
        Args:
            image_path: Path to input image
            device: Device to run inference on
            conf_thresh: Confidence threshold for segmentation
            
        Returns:
            Dict with classification and segmentation results
        """
        from torchvision import transforms
        
        # Load and preprocess image
        image = Image.open(image_path).convert('RGB')
        transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])
        
        image_tensor = transform(image).unsqueeze(0).to(device)
        
        # Forward pass
        with torch.no_grad():
            class_logits, seg_logits, _ = self.forward(image_tensor)
        
        # Classification results
        class_probs = torch.softmax(class_logits, dim=1)
        class_confidence, class_pred = torch.max(class_probs, 1)
        
        # Segmentation results
        seg_probs = torch.sigmoid(seg_logits)
        seg_mask = (seg_probs > conf_thresh).float()
        
        return {
            'classification': {
                'predicted_class_id': int(class_pred[0]),
                'confidence': float(class_confidence[0]),
                'probabilities': class_probs[0].cpu().numpy().tolist(),
            },
            'segmentation': {
                'mask': seg_mask[0, 0].cpu().numpy(),  # Binary mask
                'confidence_map': seg_probs[0, 0].cpu().numpy(),  # Probability map
                'lesion_area_ratio': float(seg_mask.sum() / seg_mask.numel()),
            },
        }


# ============================================================================
# Multi-Task Dataset
# ============================================================================

class MultiTaskDataset(Dataset):
    """
    Dataset for multi-task learning.
    
    TODO: Implement proper data loading
    - Load images and classification labels
    - Load segmentation masks (if available)
    - Handle cases where segmentation masks might not exist
    """
    
    def __init__(
        self,
        image_paths: List[str],
        classification_labels: List[int],
        segmentation_masks: Optional[List[str]] = None,
        transforms_fn=None,
    ):
        """
        Initialize dataset.
        
        Args:
            image_paths: List of image file paths
            classification_labels: List of classification labels
            segmentation_masks: List of segmentation mask paths (optional)
            transforms_fn: Data augmentation transforms
        """
        self.image_paths = image_paths
        self.classification_labels = classification_labels
        self.segmentation_masks = segmentation_masks
        self.transforms = transforms_fn
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Dict[str, torch.Tensor]:
        """Get item by index."""
        # Load image
        image_path = self.image_paths[idx]
        image = Image.open(image_path).convert('RGB')
        
        # Apply transforms
        if self.transforms:
            image = self.transforms(image)
        
        result = {
            'image': image,
            'classification_label': self.classification_labels[idx],
        }
        
        # Load segmentation mask if available
        if self.segmentation_masks and self.segmentation_masks[idx]:
            mask_path = self.segmentation_masks[idx]
            mask = Image.open(mask_path).convert('L')
            mask = torch.from_numpy(np.array(mask)).float() / 255.0
            result['segmentation_mask'] = mask
        else:
            # Create empty mask if not available
            result['segmentation_mask'] = torch.zeros((224, 224), dtype=torch.float32)
        
        return result


# ============================================================================
# Training Loop
# ============================================================================

class MultiTaskTrainer:
    """
    Trainer for multi-task learning model.
    
    Handles joint training with task-specific loss weighting.
    """
    
    def __init__(
        self,
        model: MultiTaskModel,
        device: str = 'cpu',
        classification_weight: float = 1.0,
        segmentation_weight: float = 0.5,
        learning_rate: float = 0.001,
    ):
        """
        Initialize trainer.
        
        Args:
            model: MultiTaskModel instance
            device: Device to train on
            classification_weight: Weight for classification loss
            segmentation_weight: Weight for segmentation loss
            learning_rate: Learning rate
        """
        self.model = model.to(device)
        self.device = device
        self.classification_weight = classification_weight
        self.segmentation_weight = segmentation_weight
        
        # Loss functions
        self.classification_loss_fn = nn.CrossEntropyLoss()
        self.segmentation_loss_fn = nn.BCEWithLogitsLoss()
        
        # Optimizer
        self.optimizer = optim.Adam(
            model.parameters(),
            lr=learning_rate,
            weight_decay=1e-4,
        )
        
        # Learning rate scheduler
        self.scheduler = optim.lr_scheduler.ReduceLROnPlateau(
            self.optimizer,
            mode='min',
            factor=0.1,
            patience=5,
            verbose=True,
        )
        
        # History
        self.history = {
            'train_loss': [],
            'train_classification_loss': [],
            'train_segmentation_loss': [],
            'val_loss': [],
            'val_classification_loss': [],
            'val_segmentation_loss': [],
            'epochs': 0,
        }
    
    def train_epoch(
        self,
        train_loader: DataLoader,
        epoch: int,
        total_epochs: int,
    ) -> Dict[str, float]:
        """
        Train for one epoch.
        
        Args:
            train_loader: Training dataloader
            epoch: Current epoch
            total_epochs: Total epochs
            
        Returns:
            Dict with epoch metrics
        """
        self.model.train()
        
        total_loss = 0.0
        total_classification_loss = 0.0
        total_segmentation_loss = 0.0
        total_samples = 0
        
        progress_bar = tqdm.tqdm(
            train_loader,
            desc=f"Epoch {epoch+1}/{total_epochs} [Train]",
            unit='batch'
        )
        
        for batch_idx, batch in enumerate(progress_bar):
            # Get batch
            images = batch['image'].to(self.device)
            class_labels = batch['classification_label'].to(self.device)
            seg_masks = batch['segmentation_mask'].to(self.device)
            
            # Forward pass
            self.optimizer.zero_grad()
            class_logits, seg_logits, _ = self.model(images)
            
            # Classification loss
            classification_loss = self.classification_loss_fn(
                class_logits, class_labels
            )
            
            # Segmentation loss (reshape for BCEWithLogitsLoss)
            seg_logits_flat = seg_logits.view(-1)
            seg_masks_flat = seg_masks.view(-1)
            segmentation_loss = self.segmentation_loss_fn(
                seg_logits_flat, seg_masks_flat
            )
            
            # Combined loss with weighting
            total_task_loss = (
                self.classification_weight * classification_loss +
                self.segmentation_weight * segmentation_loss
            )
            
            # Backward pass
            total_task_loss.backward()
            self.optimizer.step()
            
            # Update metrics
            batch_size = images.size(0)
            total_loss += total_task_loss.item() * batch_size
            total_classification_loss += classification_loss.item() * batch_size
            total_segmentation_loss += segmentation_loss.item() * batch_size
            total_samples += batch_size
            
            # Update progress bar
            progress_bar.set_postfix({
                'loss': total_loss / total_samples,
                'class_loss': total_classification_loss / total_samples,
                'seg_loss': total_segmentation_loss / total_samples,
            })
        
        return {
            'loss': total_loss / total_samples,
            'classification_loss': total_classification_loss / total_samples,
            'segmentation_loss': total_segmentation_loss / total_samples,
        }
    
    def val_epoch(
        self,
        val_loader: DataLoader,
        epoch: int,
        total_epochs: int,
    ) -> Dict[str, float]:
        """
        Validate for one epoch.
        
        Args:
            val_loader: Validation dataloader
            epoch: Current epoch
            total_epochs: Total epochs
            
        Returns:
            Dict with validation metrics
        """
        self.model.eval()
        
        total_loss = 0.0
        total_classification_loss = 0.0
        total_segmentation_loss = 0.0
        total_samples = 0
        
        progress_bar = tqdm.tqdm(
            val_loader,
            desc=f"Epoch {epoch+1}/{total_epochs} [Val]",
            unit='batch'
        )
        
        with torch.no_grad():
            for batch in progress_bar:
                # Get batch
                images = batch['image'].to(self.device)
                class_labels = batch['classification_label'].to(self.device)
                seg_masks = batch['segmentation_mask'].to(self.device)
                
                # Forward pass
                class_logits, seg_logits, _ = self.model(images)
                
                # Losses
                classification_loss = self.classification_loss_fn(
                    class_logits, class_labels
                )
                
                seg_logits_flat = seg_logits.view(-1)
                seg_masks_flat = seg_masks.view(-1)
                segmentation_loss = self.segmentation_loss_fn(
                    seg_logits_flat, seg_masks_flat
                )
                
                total_task_loss = (
                    self.classification_weight * classification_loss +
                    self.segmentation_weight * segmentation_loss
                )
                
                # Update metrics
                batch_size = images.size(0)
                total_loss += total_task_loss.item() * batch_size
                total_classification_loss += classification_loss.item() * batch_size
                total_segmentation_loss += segmentation_loss.item() * batch_size
                total_samples += batch_size
                
                progress_bar.set_postfix({
                    'loss': total_loss / total_samples,
                    'class_loss': total_classification_loss / total_samples,
                    'seg_loss': total_segmentation_loss / total_samples,
                })
        
        return {
            'loss': total_loss / total_samples,
            'classification_loss': total_classification_loss / total_samples,
            'segmentation_loss': total_segmentation_loss / total_samples,
        }
    
    def train(
        self,
        train_loader: DataLoader,
        val_loader: DataLoader,
        epochs: int = 100,
        patience: int = 10,
    ) -> Dict:
        """
        Run full training loop.
        
        Args:
            train_loader: Training dataloader
            val_loader: Validation dataloader
            epochs: Number of epochs
            patience: Early stopping patience
            
        Returns:
            Training history
        """
        logger.info("\n" + "="*70)
        logger.info("MULTI-TASK LEARNING TRAINING")
        logger.info("="*70)
        logger.info(f"Classification loss weight: {self.classification_weight}")
        logger.info(f"Segmentation loss weight: {self.segmentation_weight}\n")
        
        best_val_loss = float('inf')
        patience_counter = 0
        
        for epoch in range(epochs):
            # Train
            train_metrics = self.train_epoch(train_loader, epoch, epochs)
            
            # Validate
            val_metrics = self.val_epoch(val_loader, epoch, epochs)
            
            # Update history
            self.history['train_loss'].append(train_metrics['loss'])
            self.history['train_classification_loss'].append(
                train_metrics['classification_loss']
            )
            self.history['train_segmentation_loss'].append(
                train_metrics['segmentation_loss']
            )
            self.history['val_loss'].append(val_metrics['loss'])
            self.history['val_classification_loss'].append(
                val_metrics['classification_loss']
            )
            self.history['val_segmentation_loss'].append(
                val_metrics['segmentation_loss']
            )
            self.history['epochs'] = epoch + 1
            
            # Log metrics
            logger.info(
                f"\nEpoch {epoch+1}/{epochs}\n"
                f"  Train Loss: {train_metrics['loss']:.4f} "
                f"(classification={train_metrics['classification_loss']:.4f}, "
                f"segmentation={train_metrics['segmentation_loss']:.4f})\n"
                f"  Val Loss:   {val_metrics['loss']:.4f} "
                f"(classification={val_metrics['classification_loss']:.4f}, "
                f"segmentation={val_metrics['segmentation_loss']:.4f})"
            )
            
            # Learning rate scheduling
            self.scheduler.step(val_metrics['loss'])
            
            # Save best model
            if val_metrics['loss'] < best_val_loss:
                best_val_loss = val_metrics['loss']
                patience_counter = 0
                logger.info(f"✓ Best model updated (val_loss={best_val_loss:.4f})")
            else:
                patience_counter += 1
            
            # Early stopping
            if patience_counter >= patience:
                logger.info(f"Early stopping triggered at epoch {epoch+1}")
                break
        
        return self.history


# ============================================================================
# Main Training Script
# ============================================================================

def main():
    """Main training script."""
    parser = argparse.ArgumentParser(
        description='Train multi-task skin analysis model'
    )
    
    parser.add_argument(
        '--data-dir',
        type=str,
        default='ml/training/data',
        help='Dataset directory'
    )
    parser.add_argument(
        '--epochs',
        type=int,
        default=50,
        help='Number of epochs'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=16,
        help='Batch size'
    )
    parser.add_argument(
        '--lr',
        type=float,
        default=0.001,
        help='Learning rate'
    )
    parser.add_argument(
        '--classification-weight',
        type=float,
        default=1.0,
        help='Weight for classification loss'
    )
    parser.add_argument(
        '--segmentation-weight',
        type=float,
        default=0.5,
        help='Weight for segmentation loss'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='ml/exports',
        help='Output directory'
    )
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        help='Device (auto-detect if not specified)'
    )
    parser.add_argument(
        '--freeze-backbone',
        action='store_true',
        help='Freeze backbone weights'
    )
    
    args = parser.parse_args()
    
    # Auto-detect device
    if args.device is None:
        args.device = 'cuda' if torch.cuda.is_available() else 'cpu'
    
    logger.info(f"Device: {args.device}")
    
    # Create output directory
    output_dir = Path(args.output)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # ========================================================================
    # TODO: Dataset Loading
    # ========================================================================
    # This is a placeholder. Implement proper dataset loading:
    # 1. Load images from data_dir
    # 2. Load classification labels (skin type, hair type)
    # 3. Load segmentation masks (if available)
    # 4. Create train/val split
    # 5. Apply augmentations
    # ========================================================================
    
    logger.info("\n" + "!"*70)
    logger.info("TODO: Implement dataset loading")
    logger.info("!"*70)
    logger.info("\nPlease implement the following in MultiTaskDataset:")
    logger.info("  1. Load images from directory")
    logger.info("  2. Load classification labels")
    logger.info("  3. Load segmentation masks (optional)")
    logger.info("  4. Create train/val split")
    logger.info("  5. Apply augmentations\n")
    
    # For now, create dummy data for demonstration
    logger.info("Creating dummy dataset for demonstration...")
    
    dummy_image_paths = [
        str(Path(args.data_dir) / f"image_{i}.jpg")
        for i in range(32)  # Minimum 2 batches
    ]
    dummy_labels = [i % 10 for i in range(32)]
    dummy_masks = [None] * 32
    
    # Create datasets
    from torchvision import transforms as T
    
    train_transforms = T.Compose([
        T.Resize(256),
        T.CenterCrop(224),
        T.ToTensor(),
        T.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225],
        ),
    ])
    
    train_dataset = MultiTaskDataset(
        dummy_image_paths[:24],
        dummy_labels[:24],
        dummy_masks[:24],
        transforms_fn=train_transforms,
    )
    
    val_dataset = MultiTaskDataset(
        dummy_image_paths[24:],
        dummy_labels[24:],
        dummy_masks[24:],
        transforms_fn=train_transforms,
    )
    
    train_loader = DataLoader(
        train_dataset,
        batch_size=args.batch_size,
        shuffle=True,
        num_workers=0,
    )
    
    val_loader = DataLoader(
        val_dataset,
        batch_size=args.batch_size,
        shuffle=False,
        num_workers=0,
    )
    
    logger.info(f"Train samples: {len(train_dataset)}")
    logger.info(f"Val samples: {len(val_dataset)}")
    
    # ========================================================================
    # Model & Training
    # ========================================================================
    
    model = MultiTaskModel(
        num_classes_classification=10,  # 5 skin types + 5 hair types
        num_classes_segmentation=1,      # Binary segmentation
        backbone_freeze=args.freeze_backbone,
    )
    
    trainer = MultiTaskTrainer(
        model=model,
        device=args.device,
        classification_weight=args.classification_weight,
        segmentation_weight=args.segmentation_weight,
        learning_rate=args.lr,
    )
    
    # Train
    history = trainer.train(
        train_loader=train_loader,
        val_loader=val_loader,
        epochs=args.epochs,
        patience=10,
    )
    
    # ========================================================================
    # Save Results
    # ========================================================================
    
    # Save model checkpoint
    checkpoint_path = output_dir / 'multitask_best.pth'
    model.save_checkpoint(
        str(checkpoint_path),
        optimizer=trainer.optimizer,
        epoch=history['epochs'],
        metrics=history,
    )
    
    # Save training history
    history_path = output_dir / 'multitask_history.json'
    with open(history_path, 'w') as f:
        json.dump(
            {
                'train_loss': [float(x) for x in history['train_loss']],
                'train_classification_loss': [
                    float(x) for x in history['train_classification_loss']
                ],
                'train_segmentation_loss': [
                    float(x) for x in history['train_segmentation_loss']
                ],
                'val_loss': [float(x) for x in history['val_loss']],
                'val_classification_loss': [
                    float(x) for x in history['val_classification_loss']
                ],
                'val_segmentation_loss': [
                    float(x) for x in history['val_segmentation_loss']
                ],
                'epochs': history['epochs'],
            },
            f,
            indent=2,
        )
    
    logger.info("\n" + "="*70)
    logger.info("TRAINING COMPLETE")
    logger.info("="*70)
    logger.info(f"✓ Model saved: {checkpoint_path}")
    logger.info(f"✓ History saved: {history_path}")
    logger.info("="*70 + "\n")


# ============================================================================
# Example Inference
# ============================================================================

if __name__ == '__main__':
    # Training mode
    if len(sys.argv) > 1 and sys.argv[1] == '--infer':
        # Example inference
        logger.info("\n" + "="*70)
        logger.info("MULTI-TASK INFERENCE EXAMPLE")
        logger.info("="*70 + "\n")
        
        # Load model
        model_path = 'ml/exports/multitask_best.pth'
        device = 'cuda' if torch.cuda.is_available() else 'cpu'
        
        logger.info(f"Loading model from {model_path}...")
        model = MultiTaskModel.load(model_path, device=device)
        
        # Example image (create dummy for demo)
        image_path = 'test_image.jpg'
        logger.info(f"Running inference on {image_path}...")
        
        # Predict (would fail with non-existent image, but shows API)
        try:
            result = model.predict(image_path, device=device)
            
            logger.info("\nClassification Results:")
            logger.info(f"  Predicted class ID: {result['classification']['predicted_class_id']}")
            logger.info(f"  Confidence: {result['classification']['confidence']:.4f}")
            
            logger.info("\nSegmentation Results:")
            logger.info(f"  Lesion area ratio: {result['segmentation']['lesion_area_ratio']:.4f}")
            logger.info(f"  Mask shape: {result['segmentation']['mask'].shape}")
        
        except FileNotFoundError:
            logger.info(f"Image not found: {image_path}")
            logger.info("\nTo use inference, provide a valid image path.")
            logger.info("API example:")
            logger.info("  model = MultiTaskModel.load('ml/exports/multitask_best.pth')")
            logger.info("  result = model.predict('image.jpg')")
            logger.info("  print(result)")
    
    else:
        # Training mode
        main()
