# Representative Data Integration Guide

## Overview

The `representative_data.py` module is now fully integrated with `export_models.py`. This guide shows how to use representative data generation for optimal int8 quantization of TFLite models.

## Key Integration Points

### 1. Automatic Integration in export_models.py

When you export with `--quantize int8`, the system automatically:

- Loads `RepresentativeDataGenerator` if available
- Scans your dataset directory for val/test splits
- Generates representative batches for calibration
- Passes them to TFLite converter for int8 quantization

### 2. New Command-Line Options

```bash
python export_models.py --checkpoint model.pt --quantize int8 \
  --dataset-dir ml/data \
  --dataset-type classification \
  --num-calib-samples 100
```

**New Options:**

- `--dataset-dir` - Path to prepared dataset (default: `ml/data`)
- `--dataset-type` - Dataset type: `classification` or `detection` (default: `classification`)
- `--num-calib-samples` - Number of images for calibration (default: 100)

## Usage Examples

### Example 1: Export with int8 Quantization (Classification)

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize int8 \
  --dataset-dir ml/data \
  --dataset-type classification \
  --num-calib-samples 100
```

**What happens:**

1. Loads PyTorch checkpoint
2. Exports to ONNX format
3. Creates RepresentativeDataGenerator from `ml/data/`
4. Generates 100 image batches for calibration
5. Uses batches to calibrate int8 quantization
6. Saves quantized TFLite model

### Example 2: Export Both Formats with int8

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format both \
  --quantize int8 \
  --dataset-dir ml/data \
  --num-calib-samples 50
```

**Output:**

- `ml/exports/skin_classifier.onnx` - Full precision ONNX
- `ml/exports/skin_classifier.tflite` - int8 quantized TFLite

### Example 3: Detection Dataset

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize int8 \
  --dataset-dir ml/data/output \
  --dataset-type detection \
  --num-calib-samples 50
```

### Example 4: Generate Representative Data Separately

You can also generate representative data independently:

```bash
# Test and inspect
python ml/exports/representative_data.py \
  --data-dir ml/data \
  --dataset-type classification \
  --num-samples 100

# Create standalone module
python ml/exports/representative_data.py \
  --data-dir ml/data \
  --output representative_dataset.py \
  --create-module
```

## How It Works

### 1. Dataset Detection

The generator automatically discovers images from:

**Classification:**

```
ml/data/
├── val/class1/*.jpg    ← Used
├── val/class2/*.jpg    ← Used
└── test/...            ← Used if no val/
```

**Detection (YOLO):**

```
ml/data/output/
├── images/val/*.jpg    ← Used
├── images/test/*.jpg   ← Used if no val/
└── labels/...
```

### 2. Image Preprocessing

Each image is:

1. Resized to 224×224
2. Normalized to [0, 1]
3. Standardized with ImageNet stats
4. Converted to (C, H, W) format
5. Converted to uint8 for TFLite

### 3. Batch Generation

Batches are yielded as `[tf.constant(batch)]` compatible with:

```python
converter.representative_dataset = representative_dataset_gen
converter.optimizations = [tf.lite.Optimize.DEFAULT]
```

## Performance Impact

### Model Size Reduction

| Model           | Format | Quantization          | Size   |
| --------------- | ------ | --------------------- | ------ |
| EfficientNet-B0 | TFLite | None                  | ~10 MB |
| EfficientNet-B0 | TFLite | float16               | ~5 MB  |
| EfficientNet-B0 | TFLite | int8 (representative) | ~3 MB  |
| EfficientNet-B0 | TFLite | int8 (no calibration) | ~3 MB  |

### Inference Speed

| Quantization            | Latency  | Accuracy |
| ----------------------- | -------- | -------- |
| float32                 | 20-40 ms | 100%     |
| float16                 | 15-25 ms | ~99%     |
| int8 (good calibration) | 5-10 ms  | ~98%     |
| int8 (poor calibration) | 5-10 ms  | ~85%     |

**Note:** Using representative data ensures int8 models maintain accuracy!

## Integration with export_models.py

### Modified Imports

```python
try:
    from representative_data import RepresentativeDataGenerator
except ImportError:
    RepresentativeDataGenerator = None
```

### Modified main() Function

When `--quantize int8`:

```python
if args.quantize == 'int8':
    if RepresentativeDataGenerator:
        dataset_gen = RepresentativeDataGenerator(
            data_dir=args.dataset_dir,
            dataset_type=args.dataset_type,
            num_samples=args.num_calib_samples,
            batch_size=1,
            input_size=(args.input_size, args.input_size)
        )
        dataset_gen.print_summary()

        def representative_data_gen():
            return dataset_gen.generate_tflite_batches()
```

### Modified export_all() Function

```python
def export_all(
    self,
    ...
    representative_data_gen=None
):
    # Passes to export_to_tflite()
    tflite_path = self.export_to_tflite(
        ...
        representative_data_gen=representative_data_gen
    )
```

## Troubleshooting

### Problem: "No images found in dataset"

**Solution:** Verify dataset structure

```bash
ls ml/data/val/        # Should show class directories
ls ml/data/val/class1/ # Should show images
```

### Problem: "representative_data module not found"

**Solution:** Place `representative_data.py` in `ml/exports/` directory

```bash
ls ml/exports/representative_data.py
```

### Problem: "Failed to create representative dataset"

**Solution:** Check dataset type matches

```bash
# For classification
--dataset-type classification --dataset-dir ml/data

# For detection
--dataset-type detection --dataset-dir ml/data/output
```

### Problem: Slow int8 export

**Solution:** Reduce calibration samples

```bash
--num-calib-samples 20  # Instead of 100
```

## Advanced Usage

### Python API Integration

```python
from ml.exports.export_models import ModelExporter
from ml.exports.representative_data import RepresentativeDataGenerator

# Create exporter
exporter = ModelExporter('model.pth')
exporter.load_checkpoint()

# Create representative dataset
gen = RepresentativeDataGenerator(
    data_dir='ml/data',
    num_samples=100
)
gen.print_summary()

# Export with calibration
exporter.export_to_tflite(
    onnx_path='model.onnx',
    output_path='model_int8.tflite',
    quantize='int8',
    representative_data_gen=lambda: gen.generate_tflite_batches()
)
```

### Custom Preprocessing

Extend RepresentativeDataGenerator for custom preprocessing:

```python
class CustomDataGenerator(RepresentativeDataGenerator):
    def _preprocess_image(self, image_path):
        # Custom preprocessing
        image = Image.open(image_path)
        # ... your custom logic ...
        return processed_array

gen = CustomDataGenerator(data_dir='ml/data')
```

## Supported Workflows

### Workflow 1: Full Export Pipeline

```bash
# 1. Prepare dataset
python ml/data/prepare_dataset.py --task classification --source /path/to/images

# 2. Export with int8 quantization
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format both \
  --quantize int8 \
  --dataset-dir ml/data

# 3. Outputs
# - ml/exports/skin_classifier.onnx (ONNX, full precision)
# - ml/exports/skin_classifier.tflite (TFLite, int8 quantized)
```

### Workflow 2: Compare Quantization Methods

```bash
# Float32 (baseline)
python ml/exports/export_models.py \
  --checkpoint model.pth --format tflite

# Float16 quantization
python ml/exports/export_models.py \
  --checkpoint model.pth --format tflite --quantize float16

# Int8 with representative data
python ml/exports/export_models.py \
  --checkpoint model.pth --format tflite --quantize int8 \
  --dataset-dir ml/data --num-calib-samples 100

# Compare model sizes and inference speeds
ls -lh ml/exports/*.tflite
python ml/exports/example_inference.py --mode benchmark
```

## Files Overview

| File                           | Purpose                             |
| ------------------------------ | ----------------------------------- |
| `representative_data.py`       | Core generator module               |
| `REPRESENTATIVE_DATA_GUIDE.md` | Comprehensive documentation         |
| `export_models.py`             | Modified to use representative data |
| `ml/data/`                     | Dataset directory structure         |

## Summary

The representative data integration provides:

✅ Automatic dataset discovery from `ml/data/`  
✅ Support for classification and detection datasets  
✅ Optimal int8 quantization with calibration  
✅ Reduced model size (3-5 MB) with maintained accuracy  
✅ Easy CLI usage with sensible defaults  
✅ Python API for advanced integration

**Result:** Export production-ready int8 TFLite models in one command!

```bash
python ml/exports/export_models.py \
  --checkpoint skin_classifier.pth \
  --format tflite \
  --quantize int8 \
  --dataset-dir ml/data
```
