#!/usr/bin/env python3
"""
Test the trained classifier on real images.
"""

import torch
import json
from pathlib import Path
from PIL import Image
from torchvision import transforms
from torchvision.models import efficientnet_b0, EfficientNet_B0_Weights
import torch.nn as nn

def load_model(model_path: str, class_mapping_path: str):
    """Load trained model and class mapping."""
    
    # Load class mapping
    with open(class_mapping_path, 'r') as f:
        class_mapping = json.load(f)
    
    idx_to_class = {int(v): k for k, v in class_mapping.items()}
    
    # Load model
    model = efficientnet_b0(weights=EfficientNet_B0_Weights.IMAGENET1K_V1)
    num_classes = len(class_mapping)
    model.classifier[1] = nn.Linear(1280, num_classes)
    
    checkpoint = torch.load(model_path, map_location='cpu')
    model.load_state_dict(checkpoint)
    model.eval()
    
    return model, idx_to_class

def predict(image_path: str, model, idx_to_class, device='cpu'):
    """Make prediction on a single image."""
    
    # Load and preprocess image
    transform = transforms.Compose([
        transforms.Resize((224, 224)),
        transforms.ToTensor(),
        transforms.Normalize(
            mean=[0.485, 0.456, 0.406],
            std=[0.229, 0.224, 0.225]
        )
    ])
    
    image = Image.open(image_path).convert('RGB')
    image_tensor = transform(image).unsqueeze(0).to(device)
    
    # Predict
    with torch.no_grad():
        outputs = model(image_tensor)
        probabilities = torch.softmax(outputs, dim=1)
        confidence, predicted = torch.max(probabilities, 1)
    
    class_name = idx_to_class[predicted.item()]
    confidence = confidence.item() * 100
    
    return class_name, confidence, probabilities[0].cpu().numpy()

if __name__ == "__main__":
    import sys
    
    model_path = "ml/exports/skin_classifier_best.pth"
    class_mapping_path = "ml/exports/class_mapping.json"
    
    print("=" * 70)
    print("SKIN & HAIR CLASSIFIER - INFERENCE")
    print("=" * 70)
    print()
    
    # Load model
    print("Loading model...")
    model, idx_to_class = load_model(model_path, class_mapping_path)
    print(f"✓ Model loaded. Classes: {len(idx_to_class)}")
    print()
    
    # Test on sample images
    test_dir = Path("ml/data/training/test")
    if test_dir.exists():
        print(f"Testing on {test_dir}")
        print()
        
        test_images = list(test_dir.rglob("*.jpg"))[:5]  # Test on first 5 images
        
        for img_path in test_images:
            class_name, confidence, probs = predict(str(img_path), model, idx_to_class)
            print(f"Image: {img_path.parent.name}/{img_path.name}")
            print(f"Predicted: {class_name}")
            print(f"Confidence: {confidence:.2f}%")
            print()
    
    print("=" * 70)
    print("✅ INFERENCE READY!")
    print("=" * 70)
    print()
    print("Usage in production:")
    print("  model, idx_to_class = load_model(...)")
    print("  class_name, confidence, probs = predict(image_path, model, idx_to_class)")
