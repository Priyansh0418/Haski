# Running in Google Colab

Complete guide to running the training notebook in Google Colab.

## 📱 Method 1: Direct Colab Link

**Simplest:** Open directly in Colab

[![Open in Colab](https://colab.research.google.com/assets/colab-badge.svg)](https://colab.research.google.com/github/Priyansh0418/Haski/blob/main/ml/notebooks/train_classifier_starter.py)

Then proceed to [Setup Steps](#setup-steps) below.

---

## 📋 Method 2: Manual Setup

### Step 1: Upload to Google Drive

1. Download `train_classifier_starter.py` from GitHub
2. Upload to Google Drive:
   - Navigate to Drive
   - Create folder: `/Haski`
   - Create folder: `/Haski/ml`
   - Create folder: `/Haski/ml/notebooks`
   - Upload `train_classifier_starter.py`

### Step 2: Upload Dataset

1. Create folder: `/Haski/ml/data/skin_classification/`
2. Create subfolders:
   - `/Haski/ml/data/skin_classification/normal/`
   - `/Haski/ml/data/skin_classification/dry/`
   - `/Haski/ml/data/skin_classification/oily/`
   - `/Haski/ml/data/skin_classification/combination/`
   - `/Haski/ml/data/skin_classification/sensitive/`
3. Upload images to respective folders

---

## 🚀 Setup Steps

### Cell 1: Install PyTorch

```python
# Install PyTorch with CUDA support
!pip install torch torchvision pillow matplotlib numpy --upgrade
```

**Output:**

```
Successfully installed torch-2.0.0 torchvision-0.15.0 ...
```

---

### Cell 2: Mount Google Drive

```python
from google.colab import drive
drive.mount('/content/drive')
```

**Follow prompt:** Click link → Authorize → Copy token → Paste

**Output:**

```
Go to this URL in a browser: https://accounts.google.com/o/oauth2/auth?...
Enter your authorization code
Mounted at /content/drive
```

---

### Cell 3: Verify Directory Structure

```python
import os
from pathlib import Path

# Check if Haski directory exists
haski_path = Path('/content/drive/MyDrive/Haski')
print(f"Haski path exists: {haski_path.exists()}")

# List contents
os.system('ls -la /content/drive/MyDrive/Haski/ml/')
```

**Expected output:**

```
Haski path exists: True
data  notebooks  exports
```

---

### Cell 4: Navigate to Project

```python
import os
os.chdir('/content/drive/MyDrive/Haski')

# Verify
os.system('pwd')
os.system('ls -la')
```

**Output:**

```
/content/drive/MyDrive/Haski
backend  ml  frontend  docs  ...
```

---

### Cell 5: Run Training Script

```python
%run ml/notebooks/train_classifier_starter.py
```

**The script will:**

- ✅ Detect GPU (Colab has Tesla T4/P100)
- ✅ Load dataset
- ✅ Create model
- ✅ Train for 1 epoch
- ✅ Save checkpoint
- ✅ Display plots

---

## 🎯 Complete Colab Session

Here's the full notebook as executable cells:

```python
# ============================================================================
# CELL 1: INSTALL DEPENDENCIES
# ============================================================================

!pip install torch torchvision pillow matplotlib numpy --upgrade


# ============================================================================
# CELL 2: MOUNT GOOGLE DRIVE
# ============================================================================

from google.colab import drive
drive.mount('/content/drive')


# ============================================================================
# CELL 3: SET WORKING DIRECTORY
# ============================================================================

import os
os.chdir('/content/drive/MyDrive/Haski')
print(f"Current directory: {os.getcwd()}")
os.system('ls -la ml/')


# ============================================================================
# CELL 4: VERIFY DATASET
# ============================================================================

import os
from pathlib import Path

dataset_path = Path('ml/data/skin_classification')
if dataset_path.exists():
    classes = [d.name for d in dataset_path.iterdir() if d.is_dir()]
    print(f"✓ Dataset found with classes: {classes}")

    # Count images per class
    for class_dir in dataset_path.iterdir():
        if class_dir.is_dir():
            num_images = len(list(class_dir.glob('*.jpg'))) + len(list(class_dir.glob('*.png')))
            print(f"  {class_dir.name}: {num_images} images")
else:
    print("✗ Dataset not found at ml/data/skin_classification/")
    print("Please upload dataset to Google Drive first!")


# ============================================================================
# CELL 5: RUN TRAINING NOTEBOOK
# ============================================================================

%run ml/notebooks/train_classifier_starter.py


# ============================================================================
# CELL 6: CHECK OUTPUTS
# ============================================================================

import os
from pathlib import Path

output_dir = Path('ml/exports/checkpoints')
print(f"✓ Output directory: {output_dir}")
print(f"\nFiles generated:")
for file in sorted(output_dir.glob('*'))[:10]:  # Last 10 files
    size_mb = file.stat().st_size / (1024*1024)
    print(f"  - {file.name} ({size_mb:.1f} MB)")


# ============================================================================
# CELL 7: DOWNLOAD CHECKPOINT (OPTIONAL)
# ============================================================================

from google.colab import files
import os

# Find latest checkpoint
checkpoint_dir = Path('ml/exports/checkpoints')
latest_checkpoint = max(checkpoint_dir.glob('*.pt'), key=lambda x: x.stat().st_mtime)

print(f"Downloading: {latest_checkpoint.name}")
files.download(str(latest_checkpoint))
print("✓ Download started!")
```

---

## ⚙️ Colab Configuration

### Recommended Runtime Settings

1. **Change Runtime Type:**

   - Menu: Runtime → Change Runtime Type
   - Hardware accelerator: **GPU** (Tesla T4 or Tesla P100)
   - Click Save

2. **Check GPU:**
   ```python
   !nvidia-smi
   ```
   Output:
   ```
   +-----------------------------------------------------------------------------+
   | NVIDIA-SMI 525.105.02   Driver Version: 525.105.02                         |
   +-------------+
   | GPU Name        Persistence-M| Bus-Id        Disp.A | Volatile Uncorr. ECC|
   | 0  Tesla T4            Off  | 00000000:00:04.0 Off |                  0 |
   |  0%   34C    P8    10W /  70W |      0MiB / 15360MiB |      0%      Default |
   ```

---

## 🎬 Full Training in Colab

To train for more epochs:

```python
# CELL: LONGER TRAINING

# Option 1: Modify configuration and re-run
train_notebook_code = open('ml/notebooks/train_classifier_starter.py').read()

# Change EPOCHS
modified_code = train_notebook_code.replace('EPOCHS = 1', 'EPOCHS = 50')

# Execute
exec(modified_code)
```

Or directly:

```python
# CELL: CUSTOM TRAINING

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms

# [Add training code here from the notebook]
```

---

## 📊 Monitoring Training

### Real-time Metrics

```python
# CELL: MONITORING

import matplotlib.pyplot as plt
import torch

# Track metrics during training
metrics = {'train_loss': [], 'val_loss': [], 'train_acc': [], 'val_acc': []}

# During training loop:
metrics['train_loss'].append(train_loss)
metrics['val_loss'].append(val_loss)

# Plot live
plt.figure(figsize=(12, 4))
plt.subplot(1, 2, 1)
plt.plot(metrics['train_loss'], label='Train')
plt.plot(metrics['val_loss'], label='Val')
plt.xlabel('Epoch')
plt.ylabel('Loss')
plt.legend()
plt.grid(True)
plt.show()
```

---

## 💾 Save Outputs

### Download Checkpoint

```python
from google.colab import files

# Download model
files.download('ml/exports/checkpoints/skin_classifier_*.pt')
files.download('ml/exports/checkpoints/skin_classifier_*_metadata.json')
```

### Save to Google Drive Permanently

```python
import shutil

# Copy to Drive backup folder
checkpoint_latest = 'ml/exports/checkpoints/skin_classifier_*.pt'
backup_dir = '/content/drive/MyDrive/Haski/ml/exports/backups/'
os.makedirs(backup_dir, exist_ok=True)
shutil.copy(checkpoint_latest, backup_dir)
print(f"✓ Backed up to {backup_dir}")
```

---

## 🔥 Advanced: Custom Training

```python
# CELL: CUSTOM TRAINING LOOP

import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from torchvision import datasets, models, transforms
import tqdm

# Your custom training code here
# The notebook is structured to allow modifications

# Example: Custom learning rate schedule
class CustomScheduler:
    def __init__(self, optimizer, max_epochs):
        self.optimizer = optimizer
        self.max_epochs = max_epochs

    def step(self, epoch):
        # Cosine annealing
        lr = 0.001 * (1 + torch.cos(torch.pi * epoch / self.max_epochs)) / 2
        for param_group in self.optimizer.param_groups:
            param_group['lr'] = lr

# Use in training loop
# scheduler = CustomScheduler(optimizer, EPOCHS)
# scheduler.step(epoch)
```

---

## ⚠️ Common Issues in Colab

### Issue 1: "Dataset not found"

**Cause:** Dataset not uploaded or wrong path

**Fix:**

```python
# Verify path
import os
os.system('ls -la /content/drive/MyDrive/Haski/ml/data/')

# Or upload directly to Colab
from google.colab import files
uploaded = files.upload()  # Upload files directly
```

---

### Issue 2: "CUDA out of memory"

**Cause:** GPU memory exceeded

**Fix:**

```python
# Reduce batch size in config
BATCH_SIZE = 16  # Instead of 32

# Or clear cache
import torch
torch.cuda.empty_cache()

# Or use CPU
import os
os.environ['CUDA_VISIBLE_DEVICES'] = '-1'  # Force CPU
```

---

### Issue 3: Session Timeout

**Cause:** Colab disconnects after 30 min inactivity

**Prevention:**

```python
# Run this to keep session alive
import time
import random

def keep_alive():
    while True:
        print("Keep alive ping")
        time.sleep(random.randint(60, 120))

# In background
import threading
thread = threading.Thread(target=keep_alive, daemon=True)
thread.start()
```

---

### Issue 4: Import Errors

**Cause:** Missing packages

**Fix:**

```python
# Install missing package
!pip install package_name

# Example
!pip install torchvision --upgrade
```

---

## 🎓 Tips for Colab

✅ **Save Frequently**

- Save checkpoint to Drive during training
- Download important files

✅ **Use GPU**

- Runtime → Change Runtime Type → GPU
- ~10x faster training

✅ **Monitor Resources**

```python
!nvidia-smi  # Check GPU
!free -h     # Check RAM
```

✅ **Create Checkpoints**

```python
# Save every epoch
if epoch % 10 == 0:
    torch.save(model.state_dict(), f'checkpoint_epoch_{epoch}.pt')
```

✅ **Document Results**

```python
# Create summary
summary = f"""
# Training Results
- Model: {MODEL_NAME}
- Epochs: {EPOCHS}
- Final Accuracy: {val_acc:.2%}
- Time: {elapsed_time}
"""
with open('RESULTS.md', 'w') as f:
    f.write(summary)
```

---

## 📚 Resources

- [Google Colab Docs](https://colab.research.google.com/notebooks/intro.ipynb)
- [PyTorch on Colab](https://pytorch.org/get-started/locally/)
- [TensorFlow vs PyTorch](https://www.learnpytorch.io/)

---

## ✅ Checklist

- [ ] Haski project uploaded to Drive
- [ ] Dataset in correct ImageFolder format
- [ ] Installed PyTorch in Colab
- [ ] Mounted Google Drive
- [ ] Ran training script
- [ ] Downloaded checkpoint
- [ ] Verified output files

---

**Ready to train in Colab!** 🚀
