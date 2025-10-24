# Representative Data Generator for TFLite Quantization

## Overview

`representative_data.py` generates representative datasets for TFLite int8 post-training quantization. It preprocesses images from your validation/test datasets and yields batches compatible with TensorFlow's quantization pipeline.

**Why it matters:** Representative data is essential for accurate int8 quantization. The generator samples real images from your dataset to calibrate the quantizer, resulting in better model accuracy at lower bitwidth.

## Features

- ✅ **Classification & Detection Support** - Works with both image classification and YOLO detection datasets
- ✅ **Automatic Image Discovery** - Finds val/test splits automatically
- ✅ **Proper Preprocessing** - ImageNet normalization and resizing
- ✅ **Batch Generation** - Configurable batch sizes for TFLite converter
- ✅ **Reproducible** - Seeded random sampling for deterministic results
- ✅ **CLI & Python API** - Use from command line or import in code
- ✅ **Module Generation** - Create ready-to-use Python modules

## Installation

```bash
# Already have dependencies
pip install pillow numpy

# For TFLite batch generation
pip install tensorflow
```

## Quick Start

### 1. From Command Line

```bash
# Basic usage (test batch generation)
python ml/exports/representative_data.py --data-dir ml/data

# Generate from classification dataset
python ml/exports/representative_data.py \
  --data-dir ml/data \
  --dataset-type classification \
  --num-samples 100 \
  --batch-size 1

# Generate from YOLO detection dataset
python ml/exports/representative_data.py \
  --data-dir ml/data/output \
  --dataset-type detection \
  --num-samples 50 \
  --batch-size 4

# Create ready-to-use module
python ml/exports/representative_data.py \
  --data-dir ml/data \
  --output representative_dataset.py \
  --create-module
```

### 2. In Python Code

```python
from ml.exports.representative_data import RepresentativeDataGenerator

# Create generator
generator = RepresentativeDataGenerator(
    data_dir='ml/data',
    dataset_type='classification',
    num_samples=100,
    batch_size=1,
    input_size=(224, 224)
)

# Print summary
generator.print_summary()

# Generate batches for inspection
for i, batch in enumerate(generator.generate_batches()):
    print(f"Batch {i}: shape={batch.shape}, range=[{batch.min():.2f}, {batch.max():.2f}]")

# Generate TFLite-compatible batches
for batch in generator.generate_tflite_batches():
    # Use with TFLite converter
    pass
```

### 3. With TFLite Converter

```python
import tensorflow as tf
from ml.exports.representative_data import RepresentativeDataGenerator

# Create generator
def representative_dataset():
    gen = RepresentativeDataGenerator(
        data_dir='ml/data',
        dataset_type='classification',
        num_samples=100,
        batch_size=1
    )
    for batch in gen.generate_tflite_batches():
        yield batch

# Use with converter
converter = tf.lite.TFLiteConverter.from_saved_model('saved_model/')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
converter.representative_dataset = representative_dataset
converter.inference_input_type = tf.uint8
converter.inference_output_type = tf.uint8

tflite_quantized_model = converter.convert()
```

## Dataset Structure

### Classification Dataset

Expected directory structure:

```
ml/data/
├── train/
│   ├── class1/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   └── class2/
│       └── image3.jpg
├── val/              ← Used for representative data
│   ├── class1/
│   │   └── image1.jpg
│   └── class2/
│       └── image1.jpg
└── test/             ← Used if val not found
    ├── class1/
    │   └── image1.jpg
    └── class2/
        └── image1.jpg
```

### Detection Dataset (YOLO)

Expected directory structure:

```
ml/data/output/
├── images/
│   ├── train/
│   │   ├── image1.jpg
│   │   └── image2.jpg
│   ├── val/           ← Used for representative data
│   │   └── image1.jpg
│   └── test/          ← Used if val not found
│       └── image1.jpg
├── labels/
│   ├── train/
│   │   ├── image1.txt
│   │   └── image2.txt
│   ├── val/
│   │   └── image1.txt
│   └── test/
│       └── image1.txt
└── data.yaml
```

## Command-Line Options

| Option            | Default          | Description                                   |
| ----------------- | ---------------- | --------------------------------------------- |
| `--data-dir`      | `ml/data`        | Path to dataset directory                     |
| `--dataset-type`  | `classification` | Dataset type: `classification` or `detection` |
| `--num-samples`   | `100`            | Maximum images to use for calibration         |
| `--batch-size`    | `1`              | Batch size for generated batches              |
| `--input-size`    | `224 224`        | Target image size (height width)              |
| `--seed`          | `42`             | Random seed for reproducibility               |
| `--output`        | None             | Path to save generated module                 |
| `--create-module` | False            | Generate ready-to-use Python module           |
| `--test-batches`  | `3`              | Number of test batches to generate            |

## Class Reference

### `RepresentativeDataGenerator`

Main class for generating representative batches.

#### Constructor

```python
RepresentativeDataGenerator(
    data_dir: str,
    dataset_type: str = 'classification',
    num_samples: int = 100,
    batch_size: int = 1,
    input_size: Tuple[int, int] = (224, 224),
    seed: int = 42
)
```

#### Methods

**`generate_batches() → Generator[np.ndarray]`**

Generate batches of preprocessed images in float32 format.

```python
for batch in generator.generate_batches():
    print(batch.shape)  # (batch_size, 3, H, W)
    print(batch.dtype)  # float32
```

**`generate_tflite_batches() → Generator[List]`**

Generate batches compatible with TFLite converter (uint8 format).

```python
for batch in generator.generate_tflite_batches():
    # batch is [tf.constant(uint8_array)]
    yield batch
```

**`get_statistics() → dict`**

Get statistics about loaded dataset.

```python
stats = generator.get_statistics()
print(f"Total images: {stats['total_images']}")
print(f"Num batches: {stats['num_batches']}")
```

**`print_summary() → None`**

Print formatted summary of dataset.

```python
generator.print_summary()
# Output:
# ============================================================
# Representative Dataset Summary
# ============================================================
# Dataset Type:     classification
# Data Directory:   ml/data
# Total Images:     95
# Batch Size:       1
# Num Batches:      95
# Input Size:       (224, 224)
# ============================================================
```

### `create_representative_dataset_module()`

Generate a ready-to-use Python module.

```python
create_representative_dataset_module(
    output_path='representative_dataset.py',
    data_dir='ml/data',
    dataset_type='classification',
    num_samples=100,
    batch_size=1
)
```

Creates a standalone module that can be imported and used directly.

## Image Preprocessing

Images are preprocessed following standard deep learning practices:

1. **Load** - Read RGB image from file
2. **Resize** - Resize to (224, 224) using bilinear interpolation
3. **Normalize** - Divide by 255.0 to [0, 1]
4. **Standardize** - Apply ImageNet normalization:
   - Mean: [0.485, 0.456, 0.406]
   - Std: [0.229, 0.224, 0.225]
5. **Transpose** - Convert from (H, W, C) to (C, H, W) format
6. **Quantize** (optional) - Convert to uint8 for TFLite

### Preprocessing Details

```python
# After normalization, values are approximately in range [-2, 2]
# For TFLite int8, these are converted to uint8:
# uint8_value = ((float_value + 2.0) * 63.75).astype(np.uint8)
# This maps [-2, 2] → [0, 255]
```

## Integration with export_models.py

The representative data generator integrates seamlessly with `export_models.py`:

```python
from ml.exports.representative_data import RepresentativeDataGenerator

def representative_dataset():
    gen = RepresentativeDataGenerator(
        data_dir='ml/data',
        num_samples=100,
        batch_size=4
    )
    for batch in gen.generate_tflite_batches():
        yield batch

# Use in export_models.py
converter = tf.lite.TFLiteConverter.from_saved_model(saved_model_path)
converter.representative_dataset = representative_dataset
converter.optimizations = [tf.lite.Optimize.DEFAULT]
tflite_model = converter.convert()
```

## Examples

### Example 1: Basic Classification Dataset

```bash
python ml/exports/representative_data.py \
  --data-dir ml/data \
  --dataset-type classification \
  --num-samples 100
```

Output:

```
============================================================
Representative Dataset Summary
============================================================
Dataset Type:     classification
Data Directory:   ml/data
Total Images:     100
Batch Size:       1
Num Batches:      100
Input Size:       (224, 224)
============================================================

Generating 3 test batches...

Batch 0:
  Shape:     (1, 3, 224, 224)
  Data type: float32
  Min value: -2.1234
  Max value:  2.3456
  Mean:      -0.0123
  Std:        0.9876
```

### Example 2: Detection Dataset with Larger Batch

```bash
python ml/exports/representative_data.py \
  --data-dir ml/data/output \
  --dataset-type detection \
  --num-samples 50 \
  --batch-size 4
```

### Example 3: Create Standalone Module

```bash
python ml/exports/representative_data.py \
  --data-dir ml/data \
  --output representative_dataset.py \
  --create-module
```

Then use it directly:

```python
from representative_dataset import representative_data_gen

# Use with TFLite converter
converter.representative_dataset = representative_data_gen
```

### Example 4: Python Integration

```python
from ml.exports.representative_data import RepresentativeDataGenerator
import tensorflow as tf

# Create generator
gen = RepresentativeDataGenerator(
    data_dir='ml/data',
    dataset_type='classification',
    num_samples=100,
    batch_size=4
)

# Print summary
gen.print_summary()

# Inspect batch statistics
for i, batch in enumerate(gen.generate_batches()):
    print(f"\nBatch {i}:")
    print(f"  Shape: {batch.shape}")
    print(f"  Range: [{batch.min():.3f}, {batch.max():.3f}]")
    print(f"  Mean: {batch.mean():.3f}, Std: {batch.std():.3f}")
    if i >= 2:
        break

# Use with TFLite quantization
converter = tf.lite.TFLiteConverter.from_saved_model('models/saved_model')
converter.optimizations = [tf.lite.Optimize.DEFAULT]
converter.representative_dataset = lambda: gen.generate_tflite_batches()
converter.target_spec.supported_ops = [
    tf.lite.OpsSet.TFLITE_BUILTINS_INT8
]
tflite_model = converter.convert()

# Save
with open('model_quantized.tflite', 'wb') as f:
    f.write(tflite_model)
```

## Troubleshooting

| Problem                   | Solution                                                         |
| ------------------------- | ---------------------------------------------------------------- |
| "No images found"         | Verify dataset structure matches classification/detection format |
| "Failed to load image"    | Check image format (JPEG/PNG supported) and file permissions     |
| "No val/test split found" | Generator looks for `val/` or `test/` directories automatically  |
| ImportError: tensorflow   | Install with: `pip install tensorflow`                           |
| Slow image loading        | Reduce `--num-samples` or use smaller `--batch-size`             |
| Memory errors             | Reduce `--batch-size` or `--num-samples`                         |

## Performance Tips

1. **Sample Size**: 50-100 images usually sufficient for calibration
2. **Batch Size**: 1-4 recommended; larger batches use more memory
3. **Image Diversity**: Use val/test split to ensure diverse samples
4. **Preprocessing**: All preprocessing happens on-the-fly (no disk caching)

## Files

- **`representative_data.py`** - Main module
- **`ml/data/`** - Source dataset directory (classification structure)
- **`ml/data/output/`** - Prepared datasets (detection structure)

## Version

- **Version:** 1.0
- **Status:** Production Ready ✅
- **Last Updated:** 2024
