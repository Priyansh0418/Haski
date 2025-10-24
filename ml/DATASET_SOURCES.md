# Real Skin & Hair Image Dataset Sources

## 1. **Public Dermatology Datasets** (Medical-Grade, Free)

### 📊 HAM10000 - The Gold Standard

- **Size:** 10,015 images
- **Quality:** High-resolution, professionally annotated
- **Classes:** Melanoma, nevus, basal cell carcinoma, actinic keratosis, benign keratosis, dermatofibroma, vascular lesion, etc.
- **Link:** https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-melanoma
- **Fitzpatrick Diversity:** Moderate (mostly lighter skin tones)
- **Pros:** Widely used, well-documented, medical-grade labels
- **Cons:** Limited diversity, mainly lesions (not general skin health)
- **Cost:** FREE

### 🔬 ISIC (International Skin Imaging Collaboration)

- **Size:** 23,000+ images
- **Quality:** Professional dermoscopic images
- **Classes:** Melanoma, carcinoma, benign nevi, keratosis, etc.
- **Link:** https://www.isic-archive.com
- **Fitzpatrick Diversity:** Good (skin tone representation improved)
- **Pros:** Largest public dermoscopy dataset, multiple challenges available
- **Cons:** Requires registration, some images may need license
- **Cost:** FREE (with registration)

### 🏥 Fitzpatrick 17k Dataset

- **Size:** 16,575 images
- **Quality:** High, diverse skin tones
- **Classes:** 114 skin conditions, Fitzpatrick Types I-VI represented
- **Link:** https://github.com/mattingly/fitzpatrick17k
- **Fitzpatrick Diversity:** Excellent (equal representation I-VI)
- **Pros:** Explicitly balanced for diversity, MIT license
- **Cons:** Mix of professional and crowdsourced
- **Cost:** FREE

### 💇 Hair Loss Classification Dataset

- **Size:** 1,200+ images
- **Quality:** Good
- **Classes:** Hair loss severity (Norwood scale), alopecia types
- **Link:** https://www.kaggle.com/datasets/nodoubttome/hair-loss-classification
- **Fitzpatrick Diversity:** Moderate
- **Pros:** Specialized for hair loss, well-labeled
- **Cons:** Smaller dataset
- **Cost:** FREE

### 🧴 Acne Classification Dataset

- **Size:** 2,000+ images
- **Quality:** Good
- **Classes:** Acne severity (mild, moderate, severe)
- **Link:** https://www.kaggle.com/datasets/movileanu/acne-severity-classification
- **Fitzpatrick Diversity:** Moderate
- **Pros:** Well-classified by severity
- **Cons:** Limited diversity
- **Cost:** FREE

---

## 2. **Kaggle Datasets** (Community, Mostly Free)

### 🎯 Top Kaggle Skin Datasets

| Dataset                  | Size   | Classes    | Fitzpatrick | Cost |
| ------------------------ | ------ | ---------- | ----------- | ---- |
| Skin Cancer MNIST        | 10,015 | 7          | Moderate    | FREE |
| Acne Classification      | 2,000  | 4          | Moderate    | FREE |
| Hair Loss Classification | 1,200  | 5          | Moderate    | FREE |
| Skin Lesion Images       | 5,000+ | Multiple   | Good        | FREE |
| Portrait Faces (Hair)    | 10,000 | Hair types | Moderate    | FREE |

**Access:** https://www.kaggle.com/datasets (search: skin, acne, hair loss, dermatology)

---

## 3. **Synthetic Data & Augmentation Tools**

### 🤖 Synthetic Skin Image Generation

- **Tool:** NVIDIA StyleGAN for face/skin
- **Tool:** Diffusion models (Stable Diffusion with prompts)
- **Approach:** Generate synthetic diverse skin tones
- **Pros:** Unlimited diversity, perfect privacy
- **Cons:** May not capture real conditions accurately
- **Cost:** FREE (open-source models)

### 📸 Data Augmentation Instead

- **Tool:** Albumentations library (already in requirements!)
- **Approach:** Start with 1000 images → augment to 10,000
- **Transformations:** Rotation, zoom, color shift, elastic deform
- **Pros:** Realistic variations from real data
- **Cost:** FREE

---

## 4. **Commercial Datasets** (Paid, Higher Quality)

### 💰 DermNet NZ

- **Size:** 10,000+ curated images
- **Quality:** Excellent, professional dermatologists
- **Classes:** 600+ skin conditions
- **Fitzpatrick Diversity:** Good
- **Link:** https://www.dermnetnz.org
- **Cost:** Licensed use available
- **Contact:** For research/commercial use

### 💰 Roboflow Universe

- **Size:** Millions (crowdsourced)
- **Quality:** Variable
- **Classes:** Custom datasets available
- **Fitzpatrick Diversity:** High
- **Link:** https://universe.roboflow.com
- **Cost:** FREE for public use, $$ for premium
- **Pros:** Pre-split datasets, augmented versions available

### 💰 MediapipeBlaze Face Detection Dataset

- **Size:** Varies
- **Quality:** High (Google quality)
- **Classes:** Face/skin detection ready
- **Link:** https://github.com/google/mediapipe
- **Cost:** FREE

---

## 5. **How to Combine Multiple Sources** (Recommended)

### 🎯 Strategy: Multi-Source Dataset

```
ml/data/raw/
├── isic_melanoma/          (5,000 images) - ISIC dataset
├── fitzpatrick_17k/        (4,000 images) - Diverse skin tones
├── acne_classification/    (2,000 images) - Acne focus
├── hair_loss/              (1,200 images) - Hair loss
├── synthetic_augmented/    (5,000 images) - Augmented from above
└── custom_collected/       (2,000 images) - Your own data
   = 19,200 TOTAL images (excellent starting point!)
```

### Steps:

1. Download from each source (takes 1-2 hours)
2. Standardize folder structure
3. Generate manifest with `python ml/data/generate_manifest.py`
4. Balance classes if needed
5. Augment with Albumentations to 30,000+

---

## 6. **Quick Download Script** (Automated)

### Using Kaggle API

```bash
# Install Kaggle CLI
pip install kaggle

# Set up credentials (get from https://www.kaggle.com/settings)
# Place kaggle.json in ~/.kaggle/

# Download datasets
kaggle datasets download -d kmader/skin-cancer-mnist-melanoma -p ml/data/raw/
kaggle datasets download -d nodoubttome/hair-loss-classification -p ml/data/raw/
kaggle datasets download -d movileanu/acne-severity-classification -p ml/data/raw/
```

### Using Roboflow

```bash
# Install Roboflow
pip install roboflow

# Python code
from roboflow import Roboflow

rf = Roboflow(api_key="YOUR_API_KEY")
project = rf.workspace("workspace-name").project("project-name")
dataset = project.versions(1).download("folder")
```

---

## 7. **Privacy & Licensing Checklist**

Before using any dataset, verify:

- ✅ **License:** MIT, CC0, CC-BY-4.0, Apache 2.0 (check before use)
- ✅ **Usage Rights:** Can you use for commercial AI training?
- ✅ **Attribution:** Required? (mention in docs)
- ✅ **Privacy:** Anonymized? GDPR compliant?
- ✅ **Medical Accuracy:** Reviewed by dermatologists?
- ✅ **Diversity:** Representative of global population?

---

## 8. **Recommended First Dataset (Step-by-Step)**

### Option A: HAM10000 (Easiest Start)

```bash
# 1. Download from Kaggle
kaggle datasets download -d kmader/skin-cancer-mnist-melanoma

# 2. Extract
unzip skin-cancer-mnist-melanoma.zip -d ml/data/raw/

# 3. Organize with your script
python ml/data/prepare_dataset.py \
  --source ml/data/raw/HAM10000 \
  --output ml/data/skin_conditions \
  --train-split 0.7 \
  --val-split 0.15
```

### Option B: Fitzpatrick 17k (Best Diversity)

```bash
# 1. Clone the repository
git clone https://github.com/mattingly/fitzpatrick17k.git

# 2. Copy images
cp -r fitzpatrick17k/data ml/data/raw/fitzpatrick17k

# 3. Use our prepare_dataset.py to organize
python ml/data/prepare_dataset.py \
  --source ml/data/raw/fitzpatrick17k \
  --output ml/data/skin_conditions \
  --stratify  # Keep diversity
```

### Option C: Combine Everything (Best)

```bash
# Download all sources
mkdir ml/data/raw
cd ml/data/raw

# HAM10000
kaggle datasets download -d kmader/skin-cancer-mnist-melanoma

# Acne
kaggle datasets download -d movileanu/acne-severity-classification

# Hair Loss
kaggle datasets download -d nodoubttome/hair-loss-classification

# Combine all
python ../prepare_dataset.py \
  --sources ./*/  \
  --output ../skin_conditions \
  --merge-classes \
  --balance
```

---

## 9. **Starting Data Collection Today**

### Immediate Actions:

1. **Download HAM10000** (15 min)
   - Easiest, most reliable starting point
   - 10,015 images immediately available
2. **Create your own collection** (ongoing)

   - Use your phone camera + LabelImg
   - Start with 100 images for testing
   - Use DATA_COLLECTION.md guide

3. **Augment to scale** (30 min)

   - Use Albumentations in prepare_dataset.py
   - Multiply 1K images → 10K with augmentation

4. **Test your training script** (done!)
   - Run: `make train-classifier` with real data

---

## 10. **Integration with Haski Pipeline**

Once you have downloaded datasets:

```bash
# 1. Organize structure
cd d:\Haski-main

# 2. Prepare dataset
python ml/data/prepare_dataset.py \
  --source ml/data/raw/HAM10000 \
  --output ml/data/skin_conditions \
  --train-split 0.7

# 3. Generate manifest
python ml/data/generate_manifest.py \
  --data-dir ml/data/skin_conditions \
  --output ml/data/manifest.json

# 4. Train classifier
make train-classifier EPOCHS=50 BATCH_SIZE=32

# 5. Export model
make export
```

---

## Summary Table

| Source            | Images   | Fitzpatrick | Quality    | Cost    | Recommended       |
| ----------------- | -------- | ----------- | ---------- | ------- | ----------------- |
| HAM10000          | 10K      | Moderate    | ⭐⭐⭐⭐⭐ | FREE    | ✅ First choice   |
| ISIC              | 23K      | Good        | ⭐⭐⭐⭐⭐ | FREE    | ✅ Best overall   |
| Fitzpatrick 17k   | 16K      | Excellent   | ⭐⭐⭐⭐   | FREE    | ✅ Best diversity |
| Kaggle (Various)  | 50K+     | Variable    | ⭐⭐⭐⭐   | FREE    | ✅ Great options  |
| DermNet NZ        | 10K      | Good        | ⭐⭐⭐⭐⭐ | $$      | Limited budget    |
| Roboflow Universe | Millions | High        | ⭐⭐⭐     | FREE/$$ | Custom needs      |

---

## Next Steps

**Choose one dataset to start:**

1. HAM10000 (fastest) - Download now!
2. ISIC (most professional) - Great for production
3. Fitzpatrick 17k (best diversity) - If fairness is critical

Then update the training command to use real data!
