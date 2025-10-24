"""
Model Evaluation Script for Skin Classifier

Evaluates a trained classifier on test data and generates comprehensive metrics.

Features:
- Loads trained model and weights
- Computes accuracy, per-class precision, recall, F1
- Generates confusion matrix visualization
- Saves detailed metrics to JSON
- Supports both pre-split (train/val/test) and single folder datasets

Usage:
    python eval_classifier.py --model ml/exports/skin_classifier.pth --data-dir data/test
    python eval_classifier.py --model ml/exports/skin_classifier_best.pth --data-dir data/
"""

import os
import sys
import json
import logging
import argparse
from pathlib import Path
from typing import Dict, Tuple, List, Optional
from collections import defaultdict

import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
from torchvision import models
from torchvision.models import EfficientNet_B0_Weights, ResNet50_Weights
from sklearn.metrics import (
    confusion_matrix,
    precision_score,
    recall_score,
    f1_score,
    accuracy_score,
    classification_report,
)
import matplotlib.pyplot as plt
import seaborn as sns
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


class EvaluationConfig:
    """Configuration for model evaluation."""
    
    def __init__(
        self,
        model_path: str,
        data_dir: str,
        class_mapping_path: Optional[str] = None,
        output_dir: str = 'ml/exports',
        device: str = None,
        batch_size: int = 32,
        num_workers: int = 4,
    ):
        """
        Initialize evaluation configuration.
        
        Args:
            model_path: Path to trained model weights (.pth)
            data_dir: Directory containing test data
            class_mapping_path: Path to class_mapping.json (auto-detect if None)
            output_dir: Directory to save evaluation results
            device: 'cuda' or 'cpu' (auto-detect if None)
            batch_size: Batch size for evaluation
            num_workers: DataLoader workers
        """
        self.model_path = Path(model_path)
        self.data_dir = Path(data_dir)
        self.output_dir = Path(output_dir)
        self.batch_size = batch_size
        self.num_workers = num_workers
        
        # Auto-detect device
        if device is None:
            self.device = 'cuda' if torch.cuda.is_available() else 'cpu'
        else:
            self.device = device
        
        # Auto-detect class mapping
        if class_mapping_path is None:
            class_mapping_path = self.output_dir / 'class_mapping.json'
        self.class_mapping_path = Path(class_mapping_path)
        
        # Create output directory
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Validate files exist
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model file not found: {self.model_path}")
        if not self.data_dir.exists():
            raise FileNotFoundError(f"Data directory not found: {self.data_dir}")
        if not self.class_mapping_path.exists():
            raise FileNotFoundError(f"Class mapping not found: {self.class_mapping_path}")
    
    def __repr__(self) -> str:
        return (
            f"EvaluationConfig(\n"
            f"  model_path={self.model_path}\n"
            f"  data_dir={self.data_dir}\n"
            f"  output_dir={self.output_dir}\n"
            f"  device={self.device}\n"
            f")"
        )


class EvaluationDataset(torch.utils.data.Dataset):
    """Dataset for evaluation."""
    
    def __init__(
        self,
        image_paths: List[str],
        labels: List[int],
        transforms_fn=None
    ):
        """Initialize dataset."""
        self.image_paths = image_paths
        self.labels = labels
        self.transforms = transforms_fn
    
    def __len__(self) -> int:
        return len(self.image_paths)
    
    def __getitem__(self, idx: int) -> Tuple[torch.Tensor, int]:
        """Get item by index."""
        image_path = self.image_paths[idx]
        label = self.labels[idx]
        
        image = Image.open(image_path).convert('RGB')
        
        if self.transforms:
            image = self.transforms(image)
        
        return image, label


def load_class_mapping(mapping_path: Path) -> Dict[str, int]:
    """
    Load class name to index mapping.
    
    Args:
        mapping_path: Path to class_mapping.json
        
    Returns:
        Dict mapping class names to indices
    """
    with open(mapping_path) as f:
        return json.load(f)


def get_test_data(
    config: EvaluationConfig,
    class_to_idx: Dict[str, int],
) -> Tuple[List[str], List[int], Dict[str, int]]:
    """
    Get test data paths and labels.
    
    Args:
        config: Evaluation configuration
        class_to_idx: Class name to index mapping
        
    Returns:
        Tuple of (image_paths, labels, class_to_idx)
    """
    logger.info("Loading test data...")
    
    image_paths = []
    labels = []
    
    # Check if dataset has test split
    test_dir = config.data_dir / 'test'
    val_dir = config.data_dir / 'val'
    
    if test_dir.exists():
        logger.info("Using test directory")
        data_root = test_dir
    elif val_dir.exists():
        logger.info("Using validation directory (no test split found)")
        data_root = val_dir
    else:
        logger.info("Using data directory directly")
        data_root = config.data_dir
    
    # Collect images
    for class_name, class_idx in class_to_idx.items():
        class_dir = data_root / class_name
        
        if not class_dir.exists():
            logger.warning(f"Class directory not found: {class_dir}")
            continue
        
        # Collect image files
        img_count = 0
        for img_file in class_dir.glob('*.jpg'):
            image_paths.append(str(img_file))
            labels.append(class_idx)
            img_count += 1
        for img_file in class_dir.glob('*.png'):
            image_paths.append(str(img_file))
            labels.append(class_idx)
            img_count += 1
        for img_file in class_dir.glob('*.jpeg'):
            image_paths.append(str(img_file))
            labels.append(class_idx)
            img_count += 1
        
        logger.info(f"  {class_name}: {img_count} images")
    
    total_images = len(image_paths)
    logger.info(f"\nTotal test images: {total_images}")
    
    if total_images == 0:
        raise ValueError("No images found in test data")
    
    return image_paths, labels, class_to_idx


def build_model(
    config: EvaluationConfig,
    num_classes: int
) -> nn.Module:
    """
    Build and load model.
    
    Args:
        config: Evaluation configuration
        num_classes: Number of classes
        
    Returns:
        Loaded model
    """
    logger.info("Building model...")
    
    # Detect model type from class mapping
    # Try EfficientNet first (more likely based on default)
    try:
        model = models.efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
        in_features = model.classifier[1].in_features
        model.classifier[1] = nn.Linear(in_features, num_classes)
        model_type = 'efficientnet_b0'
    except Exception as e:
        logger.info(f"EfficientNet failed: {e}, trying ResNet50...")
        model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
        in_features = model.fc.in_features
        model.fc = nn.Linear(in_features, num_classes)
        model_type = 'resnet50'
    
    # Load weights
    logger.info(f"Loading model weights from {config.model_path}")
    state_dict = torch.load(config.model_path, map_location=config.device)
    model.load_state_dict(state_dict)
    model = model.to(config.device)
    model.eval()
    
    logger.info(f"Model type: {model_type}")
    logger.info(f"Number of classes: {num_classes}")
    
    return model


def evaluate_model(
    model: nn.Module,
    test_loader: DataLoader,
    idx_to_class: Dict[int, str],
    device: str,
) -> Dict:
    """
    Evaluate model on test data.
    
    Args:
        model: PyTorch model
        test_loader: Test dataloader
        idx_to_class: Index to class name mapping
        device: Device to run on
        
    Returns:
        Dict with evaluation metrics
    """
    logger.info("\nEvaluating model...")
    
    all_predictions = []
    all_labels = []
    all_probabilities = []
    
    progress_bar = tqdm.tqdm(test_loader, desc="Evaluation", unit='batch')
    
    with torch.no_grad():
        for images, labels in progress_bar:
            images = images.to(device)
            labels = labels.to(device)
            
            # Forward pass
            outputs = model(images)
            probabilities = torch.nn.functional.softmax(outputs, dim=1)
            
            # Get predictions
            _, predicted = torch.max(outputs.data, 1)
            
            all_predictions.extend(predicted.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())
            all_probabilities.extend(probabilities.cpu().numpy())
    
    all_predictions = np.array(all_predictions)
    all_labels = np.array(all_labels)
    all_probabilities = np.array(all_probabilities)
    
    # Compute metrics
    logger.info("\nComputing metrics...")
    
    # Overall accuracy
    accuracy = accuracy_score(all_labels, all_predictions)
    
    # Per-class metrics
    precision_per_class = precision_score(
        all_labels, all_predictions, average=None, zero_division=0
    )
    recall_per_class = recall_score(
        all_labels, all_predictions, average=None, zero_division=0
    )
    f1_per_class = f1_score(
        all_labels, all_predictions, average=None, zero_division=0
    )
    
    # Macro averages
    precision_macro = precision_score(
        all_labels, all_predictions, average='macro', zero_division=0
    )
    recall_macro = recall_score(
        all_labels, all_predictions, average='macro', zero_division=0
    )
    f1_macro = f1_score(
        all_labels, all_predictions, average='macro', zero_division=0
    )
    
    # Weighted averages
    precision_weighted = precision_score(
        all_labels, all_predictions, average='weighted', zero_division=0
    )
    recall_weighted = recall_score(
        all_labels, all_predictions, average='weighted', zero_division=0
    )
    f1_weighted = f1_score(
        all_labels, all_predictions, average='weighted', zero_division=0
    )
    
    # Confusion matrix
    conf_matrix = confusion_matrix(all_labels, all_predictions)
    
    # Build results dict
    results = {
        'accuracy': float(accuracy),
        'precision_macro': float(precision_macro),
        'recall_macro': float(recall_macro),
        'f1_macro': float(f1_macro),
        'precision_weighted': float(precision_weighted),
        'recall_weighted': float(recall_weighted),
        'f1_weighted': float(f1_weighted),
        'per_class_metrics': {},
        'confusion_matrix': conf_matrix.tolist(),
        'total_samples': int(len(all_labels)),
        'correct_predictions': int(np.sum(all_predictions == all_labels)),
    }
    
    # Per-class metrics
    for class_idx, class_name in idx_to_class.items():
        results['per_class_metrics'][class_name] = {
            'precision': float(precision_per_class[class_idx]),
            'recall': float(recall_per_class[class_idx]),
            'f1': float(f1_per_class[class_idx]),
            'support': int(np.sum(all_labels == class_idx)),
        }
    
    # Classification report
    report = classification_report(
        all_labels,
        all_predictions,
        target_names=[idx_to_class[i] for i in range(len(idx_to_class))],
        output_dict=True,
        zero_division=0
    )
    results['classification_report'] = report
    
    return results, all_predictions, all_labels, all_probabilities, conf_matrix


def plot_confusion_matrix(
    conf_matrix: np.ndarray,
    idx_to_class: Dict[int, str],
    output_path: Path,
    figsize: Tuple[int, int] = (10, 8)
):
    """
    Plot and save confusion matrix.
    
    Args:
        conf_matrix: Confusion matrix array
        idx_to_class: Index to class name mapping
        output_path: Path to save PNG
        figsize: Figure size
    """
    logger.info(f"\nCreating confusion matrix visualization...")
    
    # Create figure
    fig, ax = plt.subplots(figsize=figsize)
    
    # Get class labels
    class_labels = [idx_to_class[i] for i in range(len(idx_to_class))]
    
    # Create heatmap
    sns.heatmap(
        conf_matrix,
        annot=True,
        fmt='d',
        cmap='Blues',
        cbar=True,
        xticklabels=class_labels,
        yticklabels=class_labels,
        ax=ax,
        cbar_kws={'label': 'Count'}
    )
    
    ax.set_xlabel('Predicted Label', fontsize=12, fontweight='bold')
    ax.set_ylabel('True Label', fontsize=12, fontweight='bold')
    ax.set_title('Confusion Matrix', fontsize=14, fontweight='bold')
    
    # Rotate labels
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    # Tight layout
    plt.tight_layout()
    
    # Save
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    logger.info(f"✓ Confusion matrix saved: {output_path}")
    plt.close()


def plot_metrics(
    results: Dict,
    output_dir: Path
):
    """
    Plot and save various metrics visualizations.
    
    Args:
        results: Evaluation results dict
        output_dir: Directory to save plots
    """
    logger.info("Creating metrics visualizations...")
    
    # Per-class F1 scores
    fig, ax = plt.subplots(figsize=(10, 6))
    
    classes = list(results['per_class_metrics'].keys())
    f1_scores = [results['per_class_metrics'][c]['f1'] for c in classes]
    
    bars = ax.bar(classes, f1_scores, color='steelblue', alpha=0.8)
    ax.set_ylabel('F1 Score', fontsize=12, fontweight='bold')
    ax.set_title('Per-Class F1 Scores', fontsize=14, fontweight='bold')
    ax.set_ylim([0, 1.05])
    ax.axhline(y=results['f1_macro'], color='red', linestyle='--', label='Macro Average')
    ax.legend()
    
    # Add value labels on bars
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2,
            height,
            f'{height:.3f}',
            ha='center',
            va='bottom',
            fontsize=10
        )
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_dir / 'f1_scores.png', dpi=300, bbox_inches='tight')
    logger.info(f"✓ F1 scores plot saved")
    plt.close()
    
    # Precision/Recall/F1 comparison
    fig, ax = plt.subplots(figsize=(10, 6))
    
    x = np.arange(len(classes))
    width = 0.25
    
    precision_scores = [results['per_class_metrics'][c]['precision'] for c in classes]
    recall_scores = [results['per_class_metrics'][c]['recall'] for c in classes]
    f1_scores = [results['per_class_metrics'][c]['f1'] for c in classes]
    
    ax.bar(x - width, precision_scores, width, label='Precision', alpha=0.8)
    ax.bar(x, recall_scores, width, label='Recall', alpha=0.8)
    ax.bar(x + width, f1_scores, width, label='F1', alpha=0.8)
    
    ax.set_ylabel('Score', fontsize=12, fontweight='bold')
    ax.set_title('Precision, Recall, F1 by Class', fontsize=14, fontweight='bold')
    ax.set_xticks(x)
    ax.set_xticklabels(classes)
    ax.legend()
    ax.set_ylim([0, 1.05])
    
    plt.xticks(rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(output_dir / 'metrics_comparison.png', dpi=300, bbox_inches='tight')
    logger.info(f"✓ Metrics comparison plot saved")
    plt.close()


def save_detailed_report(
    results: Dict,
    config: EvaluationConfig,
    idx_to_class: Dict[int, str]
):
    """
    Save detailed evaluation report to text file.
    
    Args:
        results: Evaluation results dict
        config: Evaluation configuration
        idx_to_class: Index to class mapping
    """
    report_path = config.output_dir / 'classifier_eval_report.txt'
    
    with open(report_path, 'w') as f:
        f.write("="*70 + "\n")
        f.write("SKIN CLASSIFIER EVALUATION REPORT\n")
        f.write("="*70 + "\n\n")
        
        f.write(f"Model Path: {config.model_path}\n")
        f.write(f"Data Directory: {config.data_dir}\n")
        f.write(f"Evaluation Date: {__import__('datetime').datetime.now()}\n\n")
        
        f.write("-"*70 + "\n")
        f.write("OVERALL METRICS\n")
        f.write("-"*70 + "\n")
        f.write(f"Total Samples: {results['total_samples']}\n")
        f.write(f"Correct Predictions: {results['correct_predictions']}\n")
        f.write(f"Accuracy: {results['accuracy']:.4f}\n\n")
        
        f.write(f"Precision (Macro): {results['precision_macro']:.4f}\n")
        f.write(f"Recall (Macro):    {results['recall_macro']:.4f}\n")
        f.write(f"F1 (Macro):        {results['f1_macro']:.4f}\n\n")
        
        f.write(f"Precision (Weighted): {results['precision_weighted']:.4f}\n")
        f.write(f"Recall (Weighted):    {results['recall_weighted']:.4f}\n")
        f.write(f"F1 (Weighted):        {results['f1_weighted']:.4f}\n\n")
        
        f.write("-"*70 + "\n")
        f.write("PER-CLASS METRICS\n")
        f.write("-"*70 + "\n")
        f.write(f"{'Class':<20} {'Precision':<12} {'Recall':<12} {'F1':<12} {'Support':<10}\n")
        f.write("-"*70 + "\n")
        
        for class_name in sorted(results['per_class_metrics'].keys()):
            metrics = results['per_class_metrics'][class_name]
            f.write(
                f"{class_name:<20} "
                f"{metrics['precision']:<12.4f} "
                f"{metrics['recall']:<12.4f} "
                f"{metrics['f1']:<12.4f} "
                f"{metrics['support']:<10}\n"
            )
        
        f.write("\n" + "="*70 + "\n")
    
    logger.info(f"✓ Detailed report saved: {report_path}")


def main():
    """Main evaluation script."""
    parser = argparse.ArgumentParser(
        description='Evaluate skin classifier model'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to trained model weights (.pth)'
    )
    parser.add_argument(
        '--data-dir',
        type=str,
        required=True,
        help='Directory containing test data'
    )
    parser.add_argument(
        '--class-mapping',
        type=str,
        default=None,
        help='Path to class_mapping.json (auto-detect if not specified)'
    )
    parser.add_argument(
        '--output',
        type=str,
        default='ml/exports',
        help='Output directory for results'
    )
    parser.add_argument(
        '--device',
        type=str,
        choices=['cuda', 'cpu'],
        default=None,
        help='Device to use (auto-detect if not specified)'
    )
    parser.add_argument(
        '--batch-size',
        type=int,
        default=32,
        help='Batch size for evaluation'
    )
    parser.add_argument(
        '--num-workers',
        type=int,
        default=4,
        help='Number of DataLoader workers'
    )
    
    args = parser.parse_args()
    
    # Create config
    try:
        config = EvaluationConfig(
            model_path=args.model,
            data_dir=args.data_dir,
            class_mapping_path=args.class_mapping,
            output_dir=args.output,
            device=args.device,
            batch_size=args.batch_size,
            num_workers=args.num_workers,
        )
    except FileNotFoundError as e:
        logger.error(f"Configuration error: {e}")
        sys.exit(1)
    
    logger.info("\n" + "="*70)
    logger.info("MODEL EVALUATION")
    logger.info("="*70)
    logger.info(f"\n{config}\n")
    
    # Load class mapping
    class_to_idx = load_class_mapping(config.class_mapping_path)
    idx_to_class = {v: k for k, v in class_to_idx.items()}
    num_classes = len(class_to_idx)
    
    logger.info(f"Classes ({num_classes}): {list(class_to_idx.keys())}")
    
    # Get test data
    try:
        image_paths, labels, _ = get_test_data(config, class_to_idx)
    except ValueError as e:
        logger.error(f"Data loading error: {e}")
        sys.exit(1)
    
    # Create dataloader
    val_transforms = get_transforms(phase='val')
    test_dataset = EvaluationDataset(image_paths, labels, transforms_fn=val_transforms)
    test_loader = torch.utils.data.DataLoader(
        test_dataset,
        batch_size=config.batch_size,
        shuffle=False,
        num_workers=config.num_workers,
        pin_memory=True if config.device == 'cuda' else False
    )
    
    # Build and load model
    try:
        model = build_model(config, num_classes)
    except Exception as e:
        logger.error(f"Model loading error: {e}")
        sys.exit(1)
    
    # Evaluate
    results, predictions, true_labels, probabilities, conf_matrix = evaluate_model(
        model,
        test_loader,
        idx_to_class,
        config.device
    )
    
    # Log results
    logger.info("\n" + "-"*70)
    logger.info("EVALUATION RESULTS")
    logger.info("-"*70)
    logger.info(f"Accuracy:        {results['accuracy']:.4f}")
    logger.info(f"Precision (macro): {results['precision_macro']:.4f}")
    logger.info(f"Recall (macro):    {results['recall_macro']:.4f}")
    logger.info(f"F1 (macro):        {results['f1_macro']:.4f}")
    logger.info(f"\nPrecision (weighted): {results['precision_weighted']:.4f}")
    logger.info(f"Recall (weighted):    {results['recall_weighted']:.4f}")
    logger.info(f"F1 (weighted):        {results['f1_weighted']:.4f}")
    
    logger.info("\nPer-class metrics:")
    for class_name, metrics in sorted(results['per_class_metrics'].items()):
        logger.info(
            f"  {class_name:<20} "
            f"P={metrics['precision']:.4f} "
            f"R={metrics['recall']:.4f} "
            f"F1={metrics['f1']:.4f} "
            f"(n={metrics['support']})"
        )
    
    # Save metrics to JSON
    metrics_path = config.output_dir / 'classifier_eval.json'
    with open(metrics_path, 'w') as f:
        json.dump(results, f, indent=2)
    logger.info(f"\n✓ Metrics saved: {metrics_path}")
    
    # Save confusion matrix plot
    cm_path = config.output_dir / 'confusion_matrix.png'
    plot_confusion_matrix(conf_matrix, idx_to_class, cm_path)
    
    # Save additional plots
    try:
        plot_metrics(results, config.output_dir)
    except Exception as e:
        logger.warning(f"Could not create metrics plots: {e}")
    
    # Save detailed report
    save_detailed_report(results, config, idx_to_class)
    
    logger.info("\n" + "="*70)
    logger.info("EVALUATION COMPLETE")
    logger.info("="*70)
    logger.info(f"Results saved to: {config.output_dir}/")
    logger.info(f"  - classifier_eval.json (metrics)")
    logger.info(f"  - confusion_matrix.png (confusion matrix)")
    logger.info(f"  - f1_scores.png (F1 comparison)")
    logger.info(f"  - metrics_comparison.png (P/R/F1 comparison)")
    logger.info(f"  - classifier_eval_report.txt (detailed report)")
    logger.info("="*70 + "\n")


if __name__ == '__main__':
    main()
