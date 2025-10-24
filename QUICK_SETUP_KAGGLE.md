# ⚡ QUICK KAGGLE SETUP (2 minutes)

## Your Status

❌ Kaggle API not configured yet

## Steps to Configure

### 1️⃣ Get Your Kaggle API Token (30 seconds)

- Visit: https://www.kaggle.com/settings/account
- Scroll to "API" section
- Click **"Create New API Token"** button
- A file `kaggle.json` will download

### 2️⃣ Place the File (30 seconds)

**Copy the kaggle.json file to:**

```
C:\Users\priya\.kaggle\kaggle.json
```

**Using File Explorer:**

1. Press `Win+R`, type: `%USERPROFILE%\.kaggle`
2. Paste `kaggle.json` there
3. Done!

### 3️⃣ Verify (30 seconds)

Run this in PowerShell:

```powershell
kaggle datasets list --limit 1
```

If you see a dataset listed, you're ready! ✅

---

## Then Run These Downloads

Once configured, paste these commands into PowerShell:

```powershell
cd d:\Haski-main\ml\data\raw

# Download 1: HAM10000 (10K skin images)
Write-Output "Downloading HAM10000..."
kaggle datasets download -d kmader/skin-cancer-mnist-melanoma

# Download 2: Acne Classification (2K acne images)
Write-Output "Downloading Acne..."
kaggle datasets download -d movileanu/acne-severity-classification

# Download 3: Try Fitzpatrick 17k (if available)
Write-Output "Searching for Fitzpatrick..."
kaggle datasets list --search fitzpatrick
```

---

## 🎯 Summary

1. Download `kaggle.json` from https://www.kaggle.com/settings/account
2. Save to `C:\Users\priya\.kaggle\kaggle.json`
3. Run download commands above
4. Wait for downloads to complete (~5-20 min total)
5. Extract files
6. Train your model!

**Ready?** Go get your API token and come back! 🚀
