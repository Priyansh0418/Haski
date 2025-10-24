# Quick Start Guide - Training Notebook

Get running in 5 minutes!

## 🚀 Quick Setup

### 1. Install PyTorch (if not already installed)

```bash
# CPU only
pip install torch torchvision pillow matplotlib numpy

# With CUDA (faster)
# Visit https://pytorch.org/get-started/locally/ for your CUDA version
```

### 2. Prepare Dataset

Create ImageFolder structure:

```
ml/data/skin_classification/
├── normal/
│   ├── image1.jpg
│   ├── image2.jpg
│   └── ...
├── dry/
│   ├── image1.jpg
│   └── ...
└── ...
```

### 3. Run Training

```bash
cd d:\Haski-main
python ml/notebooks/train_classifier_starter.py
```

**Done!** ✅

---

## 📊 What Happens

The script automatically:

1. ✅ Detects GPU/CPU
2. ✅ Loads dataset from ImageFolder
3. ✅ Shows sample training images
4. ✅ Creates pretrained model (EfficientNet-B0)
5. ✅ Trains for 1 epoch (changeable)
6. ✅ Validates on held-out data
7. ✅ Saves checkpoint + metadata
8. ✅ Creates training curves visualization

---

## 🎯 Configuration (in ~10 seconds)

Edit these lines to customize:

```python
class TrainConfig:
    DATASET_PATH = Path("ml/data/skin_classification")    # Your data
    BATCH_SIZE = 32                                        # Batch size
    EPOCHS = 1                                             # Train for N epochs
    LEARNING_RATE = 0.001                                 # Learning rate
    MODEL_NAME = "efficientnet_b0"                         # Model type
    NUM_CLASSES = 5                                        # Number of classes
```

---

## 📈 Expected Output

```
✓ Device: cuda
✓ PyTorch Version: 2.0.0
✓ CUDA Available: True

✓ Dataset loaded from: ml/data/skin_classification
  Total samples: 1000
  Classes: ['normal', 'dry', 'oily', 'combination', 'sensitive']

✓ Model created
  - Model: EfficientNet-B0
  - Pretrained backbone: True
  - Total parameters: 4,012,345

✓ Starting training for 1 epoch(s)...

Epoch 1/1
  Training...
    Batch 1/32: Loss=2.1234, Acc=25.00%
    Batch 6/32: Loss=1.8342, Acc=45.31%
    Batch 11/32: Loss=1.5234, Acc=62.50%
    ...
  ✓ Train Loss: 1.2345, Acc: 75.50%

  Validating...
  ✓ Val Loss: 1.1234, Acc: 78.25%

✓ Checkpoint saved: ml/exports/checkpoints/skin_classifier_20231215_143022.pt
```

---

## 📂 Output Files

After running, you'll find:

```
ml/exports/checkpoints/
├── skin_classifier_20231215_143022.pt           # Full checkpoint
├── skin_classifier_20231215_143022_weights.pth  # Model weights
├── skin_classifier_20231215_143022_metadata.json # Info
├── sample_images.png                            # Training samples
└── training_curves.png                          # Loss/accuracy plots
```

---

## 🔥 Use Checkpoint

```python
import torch
from ml.notebooks.train_classifier_starter import model, CLASS_NAMES

# Load checkpoint
checkpoint = torch.load('ml/exports/checkpoints/skin_classifier_*.pt')
model.load_state_dict(checkpoint['model_state_dict'])

# Predict
from PIL import Image
image = Image.open('test.jpg')
image_tensor = transforms.compose([...])(image).unsqueeze(0)
output = model(image_tensor)
prediction = CLASS_NAMES[output.argmax(1).item()]
print(f"Prediction: {prediction}")
```

---

## 🌐 Google Colab

```python
# Cell 1
!pip install torch torchvision pillow matplotlib

# Cell 2
from google.colab import drive
drive.mount('/content/drive')

# Cell 3
%cd /content/drive/MyDrive/Haski

# Cell 4
%run ml/notebooks/train_classifier_starter.py
```

---

## ⚡ Tips

💡 **Faster Training:**

- Use GPU: Automatically detected
- Increase batch size: 32 → 64 (if memory allows)
- Use EfficientNet-B0 instead of ResNet50

💡 **Better Results:**

- Train longer: EPOCHS = 50
- Adjust learning rate: LEARNING_RATE = 0.0005
- Add more data: More images per class

💡 **Debug Issues:**

- Check dataset format (ImageFolder structure)
- Verify image files exist and are readable
- Check GPU memory: `nvidia-smi`

---

## 🎓 Next: Full Training

After 1 epoch works:

```python
# 1. Change epochs
EPOCHS = 50

# 2. Optionally enable early stopping
# 3. Save best model logic

# 4. Run training again
python ml/notebooks/train_classifier_starter.py

# 5. Monitor GPU/CPU usage
# Windows: Task Manager → Performance
# Linux: watch nvidia-smi
```

---

## ✅ Checklist

- [ ] PyTorch installed
- [ ] Dataset in ImageFolder format
- [ ] Run script: `python ml/notebooks/train_classifier_starter.py`
- [ ] Check ml/exports/checkpoints/ for output
- [ ] Verify checkpoint, weights, and metadata files created

**Done!** You've trained a model! 🎉

---

See [README.md](README.md) for detailed documentation.
