# 📥 Dataset Download Guide - Updated

## Issue Encountered

The HAM10000 dataset on Kaggle requires you to accept the dataset license terms first before it can be downloaded via API.

## Solution: Accept Terms & Download Manually

### Method 1: Manual Download (Fastest)

1. **HAM10000 Dataset**

   - Visit: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-melanoma
   - Click **"Join Competition"** or **"Accept"** button
   - Click **"Download"** button
   - Save to: `d:\Haski-main\ml\data\raw\`

2. **Acne Classification**
   - Visit: https://www.kaggle.com/datasets/movileanu/acne-severity-classification
   - Click **"Download"** button
   - Save to: `d:\Haski-main\ml\data\raw\`

### Method 2: Accept Terms in Browser, Then CLI Download

```powershell
cd d:\Haski-main\ml\data\raw

# After accepting terms on the website:
kaggle datasets download -d kmader/skin-cancer-mnist-melanoma
kaggle datasets download -d movileanu/acne-severity-classification
```

### Method 3: Find Alternative Kaggle Datasets (No License)

```powershell
# Search for skin/acne datasets without restrictions
kaggle datasets list --search skin
kaggle datasets list --search acne
```

---

## Quick Manual Download Steps

### For Windows:

1. Open browser to: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-melanoma
2. Click blue **"Download"** button (top right)
3. File downloads as `skin-cancer-mnist-melanoma.zip`
4. Cut/paste to: `D:\Haski-main\ml\data\raw\`
5. Repeat for acne dataset

### Extract Files

Once downloaded:

```powershell
cd d:\Haski-main\ml\data\raw

# Extract HAM10000
Expand-Archive -Path skin-cancer-mnist-melanoma.zip -DestinationPath ./ham10000

# Extract Acne
Expand-Archive -Path acne-severity-classification.zip -DestinationPath ./acne
```

---

## Verify Kaggle Credentials Work

Try a public dataset with no license:

```powershell
cd d:\Haski-main\ml\data\raw
kaggle datasets download -d aashita/nifty-50-stock-market-data
```

If this works, your credentials are valid!

---

## Alternative: Use Pre-made Balanced Dataset

If Kaggle is being difficult, I can create a synthetic balanced dataset:

```powershell
cd d:\Haski-main
python ml/data/create_synthetic_dataset.py \
  --num-images 5000 \
  --output ml/data/training \
  --diverse-skin-tones
```

This creates a balanced dataset for testing immediately!

---

## Recommended Next Step

**Option A (Recommended):**

1. Download the 2 datasets manually via web browser (fastest, 10 min total)
2. Extract to `ml/data/raw/`
3. Run training pipeline

**Option B (Alternative):**

1. Use synthetic dataset for testing
2. Download real data later
3. Retrain with real data when ready

**Which would you prefer?** Let me know and I'll guide you through!
