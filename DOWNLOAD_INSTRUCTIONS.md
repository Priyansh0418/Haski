# Dataset Download Instructions

## Prerequisites: Set Up Kaggle API

### Step 1: Get Kaggle API Credentials

1. Go to https://www.kaggle.com/settings/account
2. Click **"Create New API Token"**
3. This downloads `kaggle.json`

### Step 2: Place Kaggle Credentials

```powershell
# Create Kaggle config directory
mkdir $env:USERPROFILE\.kaggle -ErrorAction SilentlyContinue

# Move the kaggle.json file there
# Windows: Place kaggle.json in C:\Users\{YourUsername}\.kaggle\

# Or run this PowerShell command:
$kaggleJson = @"
{
  "username": "your_kaggle_username",
  "key": "your_kaggle_api_key"
}
"@
$kaggleJson | Set-Content $env:USERPROFILE\.kaggle\kaggle.json
```

### Step 3: Verify Setup

```powershell
cd d:\Haski-main
kaggle datasets list --limit 1
```

---

## Download Commands

Once Kaggle is configured, run these commands in order:

### DOWNLOAD 1: HAM10000 (Skin Cancer - 10,015 images)

```powershell
cd d:\Haski-main\ml\data\raw
kaggle datasets download -d kmader/skin-cancer-mnist-melanoma
```

**Expected:**

- File: `skin-cancer-mnist-melanoma.zip` (~1.2 GB)
- Time: 5-15 minutes

### DOWNLOAD 2: Acne Classification (2,000 images)

```powershell
cd d:\Haski-main\ml\data\raw
kaggle datasets download -d movileanu/acne-severity-classification
```

**Expected:**

- File: `acne-severity-classification.zip` (~200 MB)
- Time: 2-5 minutes

### DOWNLOAD 3: Fitzpatrick 17k (16,575 images - if available on Kaggle)

```powershell
cd d:\Haski-main\ml\data\raw
# First check if available
kaggle datasets list --search fitzpatrick

# If found, download:
kaggle datasets download -d [fitzpatrick-dataset-id]
```

---

## Alternative: Download from Web Browser

If Kaggle API authentication is problematic, download manually:

1. **HAM10000**: https://www.kaggle.com/datasets/kmader/skin-cancer-mnist-melanoma

   - Click "Download" button
   - Save to `ml/data/raw/`

2. **Acne**: https://www.kaggle.com/datasets/movileanu/acne-severity-classification

   - Click "Download" button
   - Save to `ml/data/raw/`

3. **Fitzpatrick 17k**: Search on Kaggle or GitHub
   - Alternative: https://github.com/mattingly/fitzpatrick17k (if available)

---

## Extract Downloaded Files

```powershell
cd d:\Haski-main\ml\data\raw

# Extract HAM10000
Expand-Archive -Path skin-cancer-mnist-melanoma.zip -DestinationPath .

# Extract Acne
Expand-Archive -Path acne-severity-classification.zip -DestinationPath .

# Verify extractions
Get-ChildItem -Directory
```

---

## Next Steps After Download

Once all files are downloaded and extracted:

```powershell
cd d:\Haski-main

# Generate dataset manifest
python ml/data/generate_manifest.py `
  --data-dir ml/data/raw `
  --output ml/data/manifest.json

# Prepare dataset for training
python ml/data/prepare_dataset.py `
  --sources ml/data/raw/* `
  --output ml/data/training `
  --train-split 0.7 `
  --val-split 0.15 `
  --test-split 0.15

# Start training
make train-classifier EPOCHS=50
```

---

## Troubleshooting

### "Kaggle API not configured"

- Verify `$env:USERPROFILE\.kaggle\kaggle.json` exists
- Check file permissions (should be readable)
- Run: `kaggle datasets list` to verify

### "Dataset not found"

- Some datasets may require acceptance of terms
- Visit the Kaggle dataset page and accept before downloading
- Alternative: Download manually via browser

### "Insufficient storage"

- All 3 datasets require ~2 GB total
- Ensure `D:\` has at least 5 GB free space

### Download is slow

- Kaggle has rate limiting
- Downloads may pause temporarily
- Let it run, or resume later

---

## File Structure After Download

```
ml/data/raw/
├── skin-cancer-mnist-melanoma/
│   ├── HAM10000_images_part_1/
│   ├── HAM10000_images_part_2/
│   └── HAM10000_metadata.csv
├── acne-severity-classification/
│   ├── Mild/
│   ├── Moderate/
│   └── Severe/
└── fitzpatrick17k/  (if downloaded separately)
    ├── data/
    └── metadata/
```

---

## Ready to Start?

### Option A: Automated (Easiest)

1. Set up Kaggle API (see above)
2. Run download commands
3. Everything extracts automatically

### Option B: Manual (If API issues)

1. Download via Kaggle website
2. Extract `.zip` files manually
3. Run prepare_dataset.py

**Choose your preferred method and start!** 🚀
