# Notebooks Directory - Summary

Comprehensive training notebooks and guides for the Haski skin classifier.

## 📁 Files Overview

### 1. **train_classifier_starter.py** (1200+ lines)

Main training script organized like a Jupyter notebook.

**Contents:**

- ✅ CELL 1: Setup & Imports (device detection, GPU/CPU)
- ✅ CELL 2: Configuration (hyperparameters class)
- ✅ CELL 3: Data Transforms (augmentation pipeline)
- ✅ CELL 4: Dataset Loading (ImageFolder structure)
- ✅ CELL 5: Data Visualization (plot sample images)
- ✅ CELL 6: Create Pretrained Model (EfficientNet-B0, ResNet50)
- ✅ CELL 7: Setup Training (loss, optimizer, scheduler)
- ✅ CELL 8: Training Loop (single epoch)
- ✅ CELL 9: Visualize Metrics (loss/accuracy curves)
- ✅ CELL 10: Save Checkpoint (PyTorch + metadata)
- ✅ CELL 11: Inference & Evaluation (single image prediction)
- ✅ CELL 12: Next Steps (resources & recommendations)

**Features:**

- Works locally or in Google Colab
- Auto-detects GPU/CPU
- Mock data fallback for testing
- Full error handling
- Saves visualization outputs
- Comprehensive documentation

---

### 2. **README.md** (500+ lines)

Detailed documentation with examples.

**Sections:**

- Quick start guide (local & Colab)
- Configuration reference
- Dataset format specification
- Data augmentation details
- Model architecture options
- Training mechanics
- Checkpoint format documentation
- Inference examples
- Troubleshooting guide
- Learning resources
- Best practices

---

### 3. **QUICK_START.md** (200 lines)

Get running in 5 minutes.

**Includes:**

- Installation instructions
- Quick setup (3 commands)
- Expected output
- Configuration snippets
- Output file locations
- Common commands
- Troubleshooting quick fixes

---

### 4. **COLAB_GUIDE.md** (400+ lines)

Complete Google Colab setup guide.

**Covers:**

- Step-by-step Colab setup
- Direct Colab link
- Manual upload process
- Cell-by-cell code
- GPU configuration
- Monitoring training
- Downloading results
- Advanced techniques
- Common Colab issues & fixes
- Tips & best practices

---

## 🎯 Quick Navigation

### "I want to..."

**...train a model locally**
→ [QUICK_START.md](QUICK_START.md) + [README.md](README.md)

**...train in Google Colab**
→ [COLAB_GUIDE.md](COLAB_GUIDE.md)

**...understand the code**
→ [README.md](README.md) + [train_classifier_starter.py](train_classifier_starter.py)

**...debug an issue**
→ [README.md#troubleshooting](README.md#troubleshooting)

**...customize training**
→ [README.md#configuration](README.md#configuration)

**...export model for inference**
→ [README.md#integration-with-haski-pipeline](README.md#integration-with-haski-pipeline)

---

## 🚀 30-Second Start

```bash
# 1. Install PyTorch
pip install torch torchvision pillow matplotlib numpy

# 2. Prepare dataset (ImageFolder format)
mkdir -p ml/data/skin_classification/{normal,dry,oily,combination,sensitive}
# Copy images to respective folders

# 3. Run training
python ml/notebooks/train_classifier_starter.py

# 4. Check outputs
ls ml/exports/checkpoints/
```

---

## 📊 Features Breakdown

### Data Loading

- ✅ ImageFolder dataset (PyTorch standard)
- ✅ Automatic class detection
- ✅ Train/validation split
- ✅ Custom transforms per split
- ✅ DataLoader with multiple workers

### Data Augmentation

- ✅ Random crop & resize
- ✅ Horizontal flipping
- ✅ Random rotation
- ✅ Color jittering
- ✅ Normalization (ImageNet statistics)

### Model

- ✅ EfficientNet-B0 (default)
- ✅ ResNet50 (alternative)
- ✅ Pretrained on ImageNet-1K
- ✅ Transfer learning
- ✅ Custom classification head

### Training

- ✅ Single epoch to N epochs
- ✅ Training & validation loops
- ✅ Metrics tracking
- ✅ Loss function: CrossEntropyLoss
- ✅ Optimizer: Adam (configurable)
- ✅ Learning rate scheduler: ReduceLROnPlateau

### Output

- ✅ Model checkpoint (.pt)
- ✅ Model weights (.pth)
- ✅ Metadata (.json)
- ✅ Sample images visualization
- ✅ Training curves plot

### Inference

- ✅ Single image prediction
- ✅ Confidence scores
- ✅ Top-k predictions
- ✅ Batch inference ready

---

## 🔧 Configuration Options

### Dataset

```python
DATASET_PATH = Path("ml/data/skin_classification")
BATCH_SIZE = 32
VAL_SPLIT = 0.2
```

### Model

```python
MODEL_NAME = "efficientnet_b0"  # or "resnet50"
NUM_CLASSES = 5
PRETRAINED = True
```

### Training

```python
EPOCHS = 1
LEARNING_RATE = 0.001
WEIGHT_DECAY = 1e-4
```

### Paths

```python
OUTPUT_DIR = Path("ml/exports/checkpoints")
```

---

## 📈 Expected Training Results

For a well-prepared dataset (1000+ images, 5 classes):

**After 1 Epoch:**

- Training Accuracy: ~70-80%
- Validation Accuracy: ~75-85%

**After 50 Epochs:**

- Training Accuracy: ~95%+
- Validation Accuracy: ~85-92%

_Results vary based on dataset quality and balance._

---

## 💾 Checkpoint Format

### Complete Checkpoint (.pt)

```python
{
    'epoch': int,
    'model_state_dict': dict,
    'optimizer_state_dict': dict,
    'metrics': dict,
    'config': dict,
    'class_names': ['normal', 'dry', ...],
    'num_classes': 5,
    'model_name': 'efficientnet_b0'
}
```

### Model Weights Only (.pth)

```python
# Direct model.state_dict()
# Compatible with ONNX export
```

### Metadata (.json)

```json
{
  "model_name": "efficientnet_b0",
  "num_classes": 5,
  "class_names": ["normal", "dry", "oily", "combination", "sensitive"],
  "input_size": 224,
  "final_metrics": {
    "train_loss": 1.23,
    "train_acc": 75.5,
    "val_loss": 1.12,
    "val_acc": 78.25
  }
}
```

---

## 🎓 Learning Path

1. **Beginner:** Run with defaults → [QUICK_START.md](QUICK_START.md)
2. **Intermediate:** Customize config → [README.md#configuration](README.md#configuration)
3. **Advanced:** Modify training loop → [train_classifier_starter.py](train_classifier_starter.py)
4. **Expert:** Implement custom techniques → See inline comments

---

## 🔗 Integration with Haski

### Loading Checkpoint in Inference

```python
from app.services.ml_infer import analyze_image

# Model automatically loads latest checkpoint
result = analyze_image('test_image.jpg')
print(result['skin_type'])  # Prediction from trained model
```

### Using Weights for Quantization

```python
import torch
checkpoint = torch.load('skin_classifier_*.pt')
model.load_state_dict(checkpoint['model_state_dict'])

# Quantize for mobile
quantized_model = torch.quantization.quantize_dynamic(model, {torch.nn.Linear}, dtype=torch.qint8)
torch.jit.save(torch.jit.trace(quantized_model, example_input), 'quantized.pt')
```

### Export to ONNX

```python
import torch.onnx

dummy_input = torch.randn(1, 3, 224, 224)
torch.onnx.export(model, dummy_input, 'skin_classifier.onnx',
                  input_names=['input'], output_names=['output'],
                  opset_version=12)
```

---

## 🐳 Docker Usage

```dockerfile
FROM pytorch/pytorch:2.0-cuda11.8-runtime-ubuntu20.04

WORKDIR /app
COPY ml/notebooks/train_classifier_starter.py .

RUN pip install matplotlib pillow

CMD ["python", "train_classifier_starter.py"]
```

---

## ⚡ Performance Tips

### Faster Training

- Use GPU: Automatically detected
- Increase batch size: 32 → 64 (if memory allows)
- Use mixed precision: `torch.cuda.amp.autocast()`
- Reduce image size: 224 → 192

### Better Accuracy

- Train longer: EPOCHS = 100
- More data augmentation
- Fine-tune learning rate
- Balance dataset (equal samples per class)

### Reduced Memory

- Reduce batch size: 32 → 16 or 8
- Use gradient accumulation
- Reduce image size
- Use smaller model (EfficientNet-B0 vs ResNet50)

---

## 📞 Support

### Troubleshooting

- [README.md#troubleshooting](README.md#troubleshooting)
- [COLAB_GUIDE.md#common-issues-in-colab](COLAB_GUIDE.md#common-issues-in-colab)

### Learning

- [README.md#learning-resources](README.md#learning-resources)
- [PyTorch Tutorials](https://pytorch.org/tutorials/)

### Issues

- Check dataset format (ImageFolder)
- Verify image files exist
- Check GPU memory
- Review configuration

---

## 📋 Checklist

- [ ] PyTorch installed
- [ ] Dataset prepared (ImageFolder)
- [ ] Configuration reviewed
- [ ] Script runs without errors
- [ ] Checkpoint saved
- [ ] Results visualized
- [ ] Ready for longer training

---

## 📊 Statistics

| Metric              | Value |
| ------------------- | ----- |
| Script lines        | 1200+ |
| Documentation lines | 1100+ |
| Training cells      | 12    |
| Models supported    | 2     |
| Output formats      | 3     |
| Config options      | 10+   |
| Python version      | 3.8+  |
| PyTorch version     | 1.13+ |

---

## ✅ Status

**Status:** ✅ Production Ready

- Tested locally ✅
- Tested in Colab ✅
- GPU support ✅
- CPU fallback ✅
- Error handling ✅
- Documentation complete ✅

---

## 🎉 Next Steps

1. Run the notebook: `python ml/notebooks/train_classifier_starter.py`
2. Check outputs in `ml/exports/checkpoints/`
3. Train longer by adjusting EPOCHS
4. Experiment with different configurations
5. Export model for production deployment

**Happy training!** 🚀
