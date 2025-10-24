"""
Classifier Inference Module - Skin Type Classification

Provides inference interface for transfer learning classifiers.

Features:
- PyTorch EfficientNet-B0 and ResNet50 support
- ImageNet normalization handling
- Per-class probability distribution
- Confidence-based predictions

Usage:
    from classifier_infer import SkinTypeClassifier
    
    classifier = SkinTypeClassifier(model_path='model.pth', class_names=[...])
    result = classifier.predict(image_path='photo.jpg')
    
    # Result includes:
    # {
    #     'predicted_class': 'dry',
    #     'confidence': 0.92,
    #     'probabilities': {...},
    # }
"""

import logging
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
import json

import numpy as np
import torch
import torch.nn as nn
from torchvision import models, transforms
from torchvision.models import EfficientNet_B0_Weights, ResNet50_Weights
from PIL import Image

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class SkinTypeClassifier:
    """
    Skin type classifier using transfer learning models.
    
    Supports EfficientNet-B0 and ResNet50 architectures with pre-trained weights.
    """
    
    def __init__(
        self,
        model_path: str,
        class_names: Optional[List[str]] = None,
        class_mapping_path: Optional[str] = None,
        model_arch: str = 'efficientnet_b0',
        device: str = None,
    ):
        """
        Initialize classifier.
        
        Args:
            model_path: Path to trained model weights (.pth)
            class_names: List of class names
            class_mapping_path: Path to class_mapping.json (auto-loads class names)
            model_arch: 'efficientnet_b0' or 'resnet50'
            device: 'cuda' or 'cpu' (auto-detect if None)
        """
        self.model_path = Path(model_path)
        self.model_arch = model_arch.lower()
        self.class_names = class_names
        self.device = device or ('cuda' if torch.cuda.is_available() else 'cpu')
        self.model = None
        
        # Load class mapping if provided
        if class_mapping_path:
            self._load_class_mapping(class_mapping_path)
        
        # Load model
        self._load_model()
        
        # Setup transforms
        self._setup_transforms()
    
    def _load_class_mapping(self, mapping_path: str):
        """Load class mapping from JSON file."""
        with open(mapping_path) as f:
            class_to_idx = json.load(f)
        
        # Convert to list indexed by class ID
        self.class_names = [None] * len(class_to_idx)
        for class_name, idx in class_to_idx.items():
            self.class_names[idx] = class_name
        
        logger.info(f"Loaded class mapping: {self.class_names}")
    
    def _load_model(self):
        """Load pre-trained model and fine-tuned weights."""
        if not self.model_path.exists():
            raise FileNotFoundError(f"Model not found: {self.model_path}")
        
        if self.class_names is None:
            raise ValueError(
                "class_names must be provided or load from class_mapping.json"
            )
        
        num_classes = len(self.class_names)
        logger.info(f"Loading {self.model_arch} model with {num_classes} classes")
        
        # Create model
        if self.model_arch == 'efficientnet_b0':
            self.model = models.efficientnet_b0(
                weights=EfficientNet_B0_Weights.IMAGENET1K_V1
            )
            in_features = self.model.classifier[1].in_features
            self.model.classifier[1] = nn.Linear(in_features, num_classes)
        
        elif self.model_arch == 'resnet50':
            self.model = models.resnet50(weights=ResNet50_Weights.IMAGENET1K_V1)
            in_features = self.model.fc.in_features
            self.model.fc = nn.Linear(in_features, num_classes)
        
        else:
            raise ValueError(
                f"Unsupported model architecture: {self.model_arch}. "
                f"Use 'efficientnet_b0' or 'resnet50'"
            )
        
        # Load weights
        state_dict = torch.load(self.model_path, map_location=self.device)
        self.model.load_state_dict(state_dict)
        self.model = self.model.to(self.device)
        self.model.eval()
        
        logger.info(f"✓ Model loaded successfully")
    
    def _setup_transforms(self):
        """Setup validation transforms (minimal augmentation)."""
        self.transform = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize(
                mean=[0.485, 0.456, 0.406],
                std=[0.229, 0.224, 0.225],
            ),
        ])
    
    def predict(
        self,
        image_path: str,
        return_probabilities: bool = True,
        top_k: Optional[int] = None,
    ) -> Dict[str, Any]:
        """
        Classify image.
        
        Args:
            image_path: Path to input image
            return_probabilities: Whether to return probability distribution
            top_k: Return top-k predictions (None = all)
            
        Returns:
            Dict with prediction results:
            {
                'predicted_class': str,
                'confidence': float,
                'probabilities': {...},  # if return_probabilities=True
                'top_k': [{class, confidence}, ...],  # if top_k is set
            }
        """
        # Load image
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")
        
        image = Image.open(image_path).convert('RGB')
        
        # Preprocess
        image_tensor = self.transform(image)
        image_tensor = image_tensor.unsqueeze(0).to(self.device)
        
        # Predict
        with torch.no_grad():
            logits = self.model(image_tensor)
            probabilities = torch.nn.functional.softmax(logits, dim=1)
            confidence, predicted_idx = torch.max(probabilities, 1)
        
        predicted_class = self.class_names[predicted_idx.item()]
        confidence = confidence.item()
        
        result = {
            'predicted_class': predicted_class,
            'confidence': float(confidence),
        }
        
        # Add probability distribution
        if return_probabilities:
            probs = probabilities[0].cpu().numpy()
            prob_dict = {
                self.class_names[i]: float(probs[i])
                for i in range(len(self.class_names))
            }
            result['probabilities'] = prob_dict
        
        # Add top-k predictions
        if top_k is not None:
            top_k_probs, top_k_indices = torch.topk(
                probabilities[0], k=min(top_k, len(self.class_names))
            )
            result['top_k'] = [
                {
                    'class': self.class_names[idx.item()],
                    'confidence': float(prob.item()),
                }
                for prob, idx in zip(top_k_probs, top_k_indices)
            ]
        
        return result
    
    def predict_batch(
        self,
        image_paths: List[str],
        return_probabilities: bool = True,
    ) -> List[Dict[str, Any]]:
        """
        Classify multiple images.
        
        Args:
            image_paths: List of image paths
            return_probabilities: Whether to return probability distribution
            
        Returns:
            List of prediction results
        """
        results = []
        for image_path in image_paths:
            try:
                result = self.predict(
                    image_path,
                    return_probabilities=return_probabilities
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Error processing {image_path}: {e}")
                results.append({
                    'error': str(e),
                    'image_path': str(image_path),
                })
        
        return results


# CLI Interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Classify skin type from image'
    )
    
    parser.add_argument(
        '--model',
        type=str,
        required=True,
        help='Path to model weights'
    )
    parser.add_argument(
        '--image',
        type=str,
        required=True,
        help='Path to input image'
    )
    parser.add_argument(
        '--class-mapping',
        type=str,
        default=None,
        help='Path to class_mapping.json'
    )
    parser.add_argument(
        '--arch',
        type=str,
        default='efficientnet_b0',
        choices=['efficientnet_b0', 'resnet50'],
        help='Model architecture'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Print results as JSON'
    )
    
    args = parser.parse_args()
    
    # Determine class names
    if args.class_mapping:
        classifier = SkinTypeClassifier(
            model_path=args.model,
            class_mapping_path=args.class_mapping,
            model_arch=args.arch,
        )
    else:
        # Default class names
        class_names = ['normal', 'dry', 'oily', 'combination', 'sensitive']
        classifier = SkinTypeClassifier(
            model_path=args.model,
            class_names=class_names,
            model_arch=args.arch,
        )
    
    # Predict
    result = classifier.predict(args.image, return_probabilities=True, top_k=3)
    
    # Print results
    if args.json:
        import json
        print(json.dumps(result, indent=2))
    else:
        print(f"\nPredicted class: {result['predicted_class']}")
        print(f"Confidence: {result['confidence']:.4f}")
        
        if 'probabilities' in result:
            print("\nProbabilities:")
            for class_name, prob in sorted(
                result['probabilities'].items(),
                key=lambda x: x[1],
                reverse=True
            ):
                print(f"  {class_name}: {prob:.4f}")
        
        if 'top_k' in result:
            print("\nTop-3 predictions:")
            for pred in result['top_k']:
                print(f"  {pred['class']}: {pred['confidence']:.4f}")
