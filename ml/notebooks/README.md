# ML Training Notebooks

Jupyter-style Python scripts for training and experimenting with the Haski skin classifier models.

## 📋 Notebooks Overview

### train_classifier_starter.py

A comprehensive beginner-friendly training guide organized like a Jupyter notebook.

**What's included:**

- ✅ Setup & imports with device detection (CUDA/CPU)
- ✅ Configuration class with all hyperparameters
- ✅ Image transforms (augmentation for training, center crop for validation)
- ✅ Dataset loading with ImageFolder (PyTorch standard)
- ✅ Data visualization (sample training images)
- ✅ Pretrained model creation (EfficientNet-B0, ResNet50)
- ✅ Training loop (single epoch)
- ✅ Validation loop
- ✅ Metrics tracking and visualization
- ✅ Checkpoint saving (PyTorch + metadata)
- ✅ Inference on single images
- ✅ Next steps and resources

**Organized as 12 cells:**

1. Setup & Imports
2. Configuration
3. Data Transforms
4. Dataset Loading (ImageFolder)
5. Data Visualization
6. Create Pretrained Model (Transfer Learning)
7. Setup Training (Loss, Optimizer, Scheduler)
8. Training Loop (Single Epoch)
9. Visualize Training Metrics
10. Save Checkpoint
11. Inference & Evaluation
12. Next Steps & Resources

---

## 🚀 Quick Start

### Local Setup

```bash
# Install dependencies
pip install torch torchvision pillow matplotlib numpy

# Navigate to project
cd d:\Haski-main

# Run the training notebook
python ml/notebooks/train_classifier_starter.py
```

**Expected output:**

```
✓ Device: cuda (or cpu)
✓ PyTorch Version: 2.0.0
✓ CUDA Available: True

✓ Configuration Loaded:
  DATASET_PATH: ml/data/skin_classification
  BATCH_SIZE: 32
  ...

✓ Dataset loaded from: ml/data/skin_classification
  Total samples: 1000
  Classes: ['normal', 'dry', 'oily', 'combination', 'sensitive']

[Training progress...]

Epoch 1/1
  Training...
    Batch 1/32: Loss=2.1234, Acc=25.00%
    ...
  ✓ Train Loss: 1.2345, Acc: 75.50%
  ✓ Val Loss: 1.1234, Acc: 78.25%

✓ Checkpoint saved: ml/exports/checkpoints/skin_classifier_20231215_143022.pt
```

### Google Colab Setup

```python
# Cell 1: Install dependencies
!pip install torch torchvision pillow matplotlib numpy

# Cell 2: Mount Google Drive
from google.colab import drive
drive.mount('/content/drive')

# Cell 3: Navigate to project
%cd /content/drive/MyDrive/Haski

# Cell 4: Run the notebook
%run ml/notebooks/train_classifier_starter.py
```

Or open directly in Colab:
[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Priyansh0418/Haski/blob/main/ml/notebooks/train_classifier_starter.py)

---

## 📊 Configuration

Edit the `TrainConfig` class to customize training:

```python
class TrainConfig:
    # Dataset
    DATASET_PATH = Path("ml/data/skin_classification")  # ImageFolder path
    BATCH_SIZE = 32                                      # Samples per batch
    VAL_SPLIT = 0.2                                      # 20% validation

    # Model
    MODEL_NAME = "efficientnet_b0"                       # or "resnet50"
    NUM_CLASSES = 5                                      # Output classes
    PRETRAINED = True                                    # Use ImageNet weights

    # Training
    EPOCHS = 1                                           # Number of epochs
    LEARNING_RATE = 0.001                               # Initial LR
    WEIGHT_DECAY = 1e-4                                 # L2 regularization

    # Paths
    OUTPUT_DIR = Path("ml/exports/checkpoints")         # Save location
```

---

## 🎯 Dataset Format

The script expects ImageFolder structure:

```
dataset_path/
├── class1/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── class2/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
└── ...
```

Classes are automatically detected from folder names.

**Example for skin types:**

```
ml/data/skin_classification/
├── normal/
├── dry/
├── oily/
├── combination/
└── sensitive/
```

---

## 🖼️ Data Augmentation

### Training Transforms

- **RandomResizedCrop(224)** - Random crop and resize
- **RandomHorizontalFlip(0.5)** - Horizontal flip
- **RandomRotation(15°)** - Rotation ±15°
- **ColorJitter** - Brightness, contrast, saturation, hue
- **Normalize** - ImageNet statistics (mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])

### Validation Transforms

- **Resize(256)** - Resize to 256
- **CenterCrop(224)** - Center crop to 224
- **Normalize** - ImageNet statistics

**Output:** All images normalized to (B, 3, 224, 224) with values in [-2, 2]

---

## 🧠 Models Supported

### EfficientNet-B0 (Default)

- **Params:** ~5.3M
- **Speed:** Fast
- **Accuracy:** High
- **Best for:** Mobile/edge deployment

### ResNet50

- **Params:** ~23.5M
- **Speed:** Medium
- **Accuracy:** Very High
- **Best for:** High accuracy requirements

Both use ImageNet-1K pretrained weights for transfer learning.

---

## 📈 Training

### Single Epoch Training

```python
model.train()
for epoch in range(EPOCHS):
    # Training loop
    for images, labels in train_loader:
        outputs = model(images)
        loss = criterion(outputs, labels)
        optimizer.zero_grad()
        loss.backward()
        optimizer.step()

    # Validation loop
    model.eval()
    with torch.no_grad():
        for images, labels in val_loader:
            outputs = model(images)
            # Compute metrics
```

### Metrics Tracked

- **Training Loss:** CrossEntropyLoss
- **Training Accuracy:** Percentage correct
- **Validation Loss:** CrossEntropyLoss
- **Validation Accuracy:** Percentage correct

### Learning Rate Scheduling

- **Scheduler:** ReduceLROnPlateau
- **Factor:** 0.5
- **Patience:** 3 epochs
- **Trigger:** No improvement in validation loss

---

## 💾 Checkpoint Saving

Saves three files:

### 1. `{name}.pt` (Complete Checkpoint)

```python
checkpoint = {
    'epoch': int,
    'model_state_dict': dict,
    'optimizer_state_dict': dict,
    'metrics': dict,
    'config': dict,
    'class_names': list,
    'num_classes': int,
    'model_name': str,
}
```

**Load:**

```python
checkpoint = torch.load('checkpoint.pt')
model.load_state_dict(checkpoint['model_state_dict'])
optimizer.load_state_dict(checkpoint['optimizer_state_dict'])
```

### 2. `{name}_weights.pth` (Model Weights Only)

```python
torch.save(model.state_dict(), 'weights.pth')
model.load_state_dict(torch.load('weights.pth'))
```

### 3. `{name}_metadata.json` (Training Info)

```json
{
  "model_name": "efficientnet_b0",
  "num_classes": 5,
  "class_names": ["normal", "dry", "oily", "combination", "sensitive"],
  "input_size": 224,
  "num_channels": 3,
  "epoch": 1,
  "final_metrics": {
    "train_loss": 1.2345,
    "train_acc": 75.5,
    "val_loss": 1.1234,
    "val_acc": 78.25
  },
  "timestamp": "2023-12-15T14:30:22.123456"
}
```

---

## 🔍 Inference

### Single Image Prediction

```python
from PIL import Image
import torch

# Load model
checkpoint = torch.load('checkpoint.pt')
model.load_state_dict(checkpoint['model_state_dict'])
model.eval()

# Load image
image = Image.open('test.jpg').convert('RGB')
image_tensor = val_transforms(image).unsqueeze(0).to(device)

# Predict
with torch.no_grad():
    outputs = model(image_tensor)
    probs = torch.softmax(outputs, dim=1)
    confidence, predicted = torch.max(probs, 1)

predicted_class = CLASS_NAMES[predicted.item()]
confidence_score = confidence.item()

print(f"Prediction: {predicted_class} ({confidence_score:.2%})")
```

---

## 📊 Output Files

After training, check `ml/exports/checkpoints/`:

```
ml/exports/checkpoints/
├── skin_classifier_20231215_143022.pt              # Complete checkpoint
├── skin_classifier_20231215_143022_weights.pth     # Model weights
├── skin_classifier_20231215_143022_metadata.json   # Metadata
├── sample_images.png                               # Training samples
└── training_curves.png                             # Loss & accuracy curves
```

---

## 🎓 Learning Resources

### Official Documentation

- [PyTorch Documentation](https://pytorch.org/docs/)
- [TorchVision Models](https://pytorch.org/vision/stable/models.html)
- [Transfer Learning Tutorial](https://pytorch.org/tutorials/beginner/transfer_learning_tutorial.html)

### Papers

- [EfficientNet: Rethinking Model Scaling for Convolutional Neural Networks](https://arxiv.org/abs/1905.11946)
- [ResNet: Deep Residual Learning for Image Recognition](https://arxiv.org/abs/1512.03385)
- [RandAugment: Practical automated data augmentation with a reduced search space](https://arxiv.org/abs/1909.13719)

### Tutorials

- [CNN Image Classification with PyTorch](https://pytorch.org/tutorials/beginner/blitz/cifar10_tutorial.html)
- [Data Augmentation Techniques](https://pytorch.org/vision/stable/transforms.html)
- [Learning Rate Scheduling](https://pytorch.org/docs/stable/optim.html#how-to-adjust-learning-rate)

---

## ⚙️ Troubleshooting

### CUDA Out of Memory

**Problem:** `RuntimeError: CUDA out of memory`

**Solutions:**

1. Reduce `BATCH_SIZE` (32 → 16 or 8)
2. Reduce image size (224 → 192)
3. Use CPU (device will auto-detect)
4. Use gradient accumulation

```python
# Gradient accumulation (every 4 batches)
accumulation_steps = 4
for batch_idx, (images, labels) in enumerate(dataloader):
    outputs = model(images)
    loss = criterion(outputs, labels) / accumulation_steps
    loss.backward()

    if (batch_idx + 1) % accumulation_steps == 0:
        optimizer.step()
        optimizer.zero_grad()
```

### Dataset Not Found

**Problem:** `FileNotFoundError: dataset_path not found`

**Solutions:**

1. Create directory structure:

   ```bash
   mkdir -p ml/data/skin_classification/{normal,dry,oily,combination,sensitive}
   ```

2. Update `DATASET_PATH` in config:

   ```python
   DATASET_PATH = Path("/your/actual/path/to/dataset")
   ```

3. Check file permissions:
   ```bash
   ls -la ml/data/skin_classification/
   ```

### Slow Training

**Problem:** Training is very slow

**Solutions:**

1. Increase `NUM_WORKERS` (4 → 8 or 16)
2. Set `pin_memory=True` (already done for CUDA)
3. Use smaller model (ResNet50 → EfficientNet-B0)
4. Use GPU if available

### Model Not Improving

**Problem:** Validation accuracy plateauing

**Solutions:**

1. Increase learning rate or use different optimizer
2. Add more data augmentation
3. Train longer (more epochs)
4. Try different model architecture
5. Check for data quality issues

---

## 📝 Tips for Best Results

✅ **Data Quality**

- Ensure balanced dataset (similar samples per class)
- Check for corrupted images
- Resize to uniform dimensions

✅ **Training**

- Monitor train/val loss for overfitting (divergence = overfitting)
- Save best model, not just last epoch
- Use validation for hyperparameter tuning
- Try learning rate scheduling

✅ **Augmentation**

- More augmentation = more regularization
- Validate that transforms don't distort images
- Use domain-specific augmentation (e.g., skin tones)

✅ **Performance**

- Use GPU for faster training
- Increase batch size for better convergence (if memory allows)
- Use mixed precision for faster training (torch.cuda.amp)

✅ **Deployment**

- Quantize model for mobile (torch.quantization)
- Convert to ONNX (torch.onnx.export)
- Test on target hardware

---

## 🔗 Integration with Haski Pipeline

### Export to Inference Module

```python
# After training, convert checkpoint to inference format
import torch

checkpoint = torch.load('skin_classifier_20231215_143022.pt')
model.load_state_dict(checkpoint['model_state_dict'])

# Export for inference
torch.onnx.export(model, dummy_input, 'skin_classifier.onnx')
# or for TFLite
torch.jit.trace(model, dummy_input).save('skin_classifier.pt')
```

### Use with ml_infer.py

```python
from app.services.ml_infer import analyze_image

result = analyze_image('test_image.jpg')
print(result)
# Output: {
#     'skin_type': 'normal',
#     'hair_type': 'wavy',
#     'conditions_detected': ['healthy'],
#     'confidence_scores': {'skin_type': 0.95, ...},
#     'model_type': 'tflite'
# }
```

---

## 🎬 Getting Started

1. **Prepare dataset** in ImageFolder format
2. **Run the notebook**: `python ml/notebooks/train_classifier_starter.py`
3. **Check outputs** in `ml/exports/checkpoints/`
4. **Tune hyperparameters** and train longer
5. **Export model** for deployment
6. **Integrate** with inference pipeline

---

## 📞 Support

For issues or questions:

1. Check [Troubleshooting](#troubleshooting) section
2. Review [Learning Resources](#learning-resources)
3. Check PyTorch documentation
4. See main README in ml/training/

---

**Status:** ✅ Ready to use
**Python:** 3.8+
**Framework:** PyTorch 1.13+
**Models:** EfficientNet-B0, ResNet50
