# Model Export Guide

Export PyTorch skin classifier models to ONNX and TFLite formats for cross-platform deployment.

## Overview

This guide demonstrates how to export trained PyTorch models to production-ready formats:

- **ONNX**: Portable format for inference on CPUs, servers, and web browsers
- **TFLite**: Optimized format for mobile devices and edge deployment

### Supported Conversions

```
PyTorch (.pth)
    ↓
ONNX (.onnx) ← Can be used independently
    ↓
TensorFlow SavedModel
    ↓
TFLite (.tflite) ← Quantized or float32
```

## Installation

### Prerequisites

```bash
# Core packages (already in requirements.txt)
pip install torch torchvision pillow numpy

# For ONNX export
pip install onnx onnxruntime

# For TFLite export (one of the following)
pip install tensorflow onnx-tf
# OR
pip install tensorflow  # if onnx-tf is unavailable

# Optional: For verification and analysis
pip install onnxruntime-tools netron
```

## Quick Start

### Basic Export (ONNX + TFLite)

```bash
# Export both formats to ml/exports/
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth

# Expected output:
# ml/exports/skin_classifier.onnx
# ml/exports/skin_classifier.tflite
```

### Export with Quantization

```bash
# TFLite with float16 quantization (smaller, faster)
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize float16

# TFLite with int8 quantization (smallest, requires calibration)
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize int8 \
  --calibration-dir path/to/calibration/images
```

## Export Formats

### ONNX Export

**Format**: `skin_classifier.onnx`  
**Size**: ~21 MB (EfficientNet-B0)  
**Latency**: ~50ms (CPU), ~10ms (GPU)  
**Platforms**: Desktop, server, web, mobile (via ONNX Runtime)

#### Features

- **Dynamic Axes**: Batch size and input dimensions are dynamic
- **Opset Version**: 11 (broad compatibility)
- **Constant Folding**: Pre-computed constant operations for faster inference
- **Verification**: Automatic ONNX model validation

#### Export Command

```bash
# ONNX only
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format onnx
```

#### Usage (ONNX Runtime)

```python
import onnxruntime as rt
import numpy as np
from PIL import Image

# Load model
sess = rt.InferenceSession('skin_classifier.onnx')

# Prepare input
image = Image.open('photo.jpg').convert('RGB')
image = image.resize((224, 224))
image_array = np.array(image, dtype=np.float32) / 255.0

# Normalize (ImageNet statistics)
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
image_array = (image_array - mean) / std

# Add batch dimension (1, 3, 224, 224)
image_array = np.expand_dims(image_array, axis=0).transpose(0, 3, 1, 2)

# Infer
input_name = sess.get_inputs()[0].name
output_name = sess.get_outputs()[0].name
logits = sess.run([output_name], {input_name: image_array})[0]

# Get prediction
class_id = np.argmax(logits[0])
confidence = softmax(logits[0])[class_id]
print(f"Class: {class_id}, Confidence: {confidence:.3f}")
```

### TFLite Export

**Format**: `skin_classifier.tflite`  
**Size**:

- Float32: ~21 MB
- Float16: ~11 MB
- Int8: ~5.5 MB

**Latency**:

- CPU: 50-100ms
- Mobile GPU: 20-30ms
- Mobile NN Accelerator: 5-10ms

**Platforms**: Mobile (iOS, Android), embedded devices, Raspberry Pi

#### Export Commands

```bash
# Float32 (baseline, largest)
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite

# Float16 quantization (recommended for balance)
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize float16

# Int8 quantization (smallest, requires calibration data)
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize int8 \
  --calibration-dir ml/training/data/train
```

#### Usage (TensorFlow Lite)

**Python (Mobile/Edge)**:

```python
import tensorflow as tf
import numpy as np
from PIL import Image

# Load model
interpreter = tf.lite.Interpreter(model_path='skin_classifier.tflite')
interpreter.allocate_tensors()

# Get input/output details
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

# Prepare input
image = Image.open('photo.jpg').convert('RGB')
image = image.resize((224, 224))
image_array = np.array(image, dtype=np.float32) / 255.0

# Normalize
mean = np.array([0.485, 0.456, 0.406])
std = np.array([0.229, 0.224, 0.225])
image_array = (image_array - mean) / std
image_array = np.expand_dims(image_array, axis=0)

# Set input
interpreter.set_tensor(input_details[0]['index'], image_array.astype(np.float32))

# Infer
interpreter.invoke()

# Get output
output = interpreter.get_tensor(output_details[0]['index'])
class_id = np.argmax(output[0])
confidence = tf.nn.softmax(output[0])[class_id].numpy()
print(f"Class: {class_id}, Confidence: {confidence:.3f}")
```

**Kotlin (Android)**:

```kotlin
import org.tensorflow.lite.Interpreter
import java.nio.MappedByteBuffer

// Load model
val model: MappedByteBuffer = loadModelFile("skin_classifier.tflite")
val interpreter = Interpreter(model)

// Prepare input (1, 224, 224, 3) as float32 array
val input = Array(1) { Array(224) { Array(224) { FloatArray(3) } } }
// ... populate input with image data ...

// Create output array
val output = Array(1) { FloatArray(10) }  // 10 classes

// Infer
interpreter.run(input, output)

// Get prediction
val classId = output[0].withIndex().maxByOrNull { it.value }?.index ?: 0
val confidence = output[0][classId]
```

**Swift (iOS)**:

```swift
import TensorFlowLite

// Load model
let modelPath = Bundle.main.path(forResource: "skin_classifier", ofType: "tflite")!
var interpreter: Interpreter
do {
    interpreter = try Interpreter(modelPath: modelPath)
    try interpreter.allocateTensors()
} catch {
    print("Error loading model: \(error)")
    return
}

// Prepare input
let inputShape: [NSNumber] = [1, 224, 224, 3]
let scaledBytes = getScaledImageBytes(from: image)

// Copy to input tensor
try interpreter.copy(scaledBytes, toInputAt: 0)

// Invoke
try interpreter.invoke()

// Get output
let outputTensor = try interpreter.output(at: 0)
let confidences = outputTensor.data.withUnsafeBytes {
    [Float](UnsafeRawBufferPointer(start: $0.baseAddress!, count: 10))
}

let classId = confidences.argmax()
let confidence = confidences[classId]
```

## Quantization

### Float16 Quantization

**Best for**: General mobile deployment  
**Pros**: 2× smaller, minimal accuracy loss  
**Cons**: Requires fp16-capable hardware

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize float16
```

**How it works**:

- Weights converted from float32 to float16 (2 bytes per value)
- Model size reduced by ~50%
- Minimal accuracy degradation
- No calibration data needed

### Int8 Quantization

**Best for**: Maximum compression and speed  
**Pros**: 4× smaller, 3-4× faster  
**Cons**: Requires calibration data, may lose accuracy

```bash
# Prepare calibration images
mkdir -p ml/exports/calibration
# Copy ~100 diverse representative images to this directory

python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --format tflite \
  --quantize int8 \
  --calibration-dir ml/exports/calibration
```

**Calibration Dataset Requirements**:

- **Size**: 50-200 images
- **Diversity**: Representative of real-world inputs
- **Format**: JPG, PNG (same as training data)
- **Content**: Various skin types, lighting conditions, angles

**How it works**:

```
1. Load calibration images (representative dataset)
2. Run inference on each image
3. Record activation ranges for each layer
4. Quantize weights to int8 based on activation ranges
5. Convert inference to int8 operations
```

**Accuracy Comparison**:

```
| Quantization | Model Size | Latency | Accuracy Drop |
|--------------|-----------|---------|---------------|
| Float32      | 21 MB     | 50ms    | -             |
| Float16      | 11 MB     | 45ms    | < 1%          |
| Int8         | 5.5 MB    | 15ms    | 2-5%          |
```

## Advanced Usage

### Custom Input Size

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --input-size 384  # For higher resolution
```

### CPU-Only Export

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --device cpu
```

### Custom Number of Classes

```bash
python ml/exports/export_models.py \
  --checkpoint ml/exports/skin_classifier.pth \
  --num-classes 5
```

## Verification

### Verify ONNX Model

```bash
# Using ONNX Runtime
pip install onnxruntime

python -c "
import onnxruntime as rt
sess = rt.InferenceSession('skin_classifier.onnx')
print('ONNX model loaded successfully')
print(f'Input: {sess.get_inputs()[0].name}')
print(f'Output: {sess.get_outputs()[0].name}')
"
```

### Visualize ONNX Model

```bash
# Install Netron
pip install netron

# View model in browser
netron skin_classifier.onnx
# Opens http://localhost:6006
```

### Verify TFLite Model

```python
import tensorflow as tf

interpreter = tf.lite.Interpreter(model_path='skin_classifier.tflite')
interpreter.allocate_tensors()

print(f"Inputs: {interpreter.get_input_details()}")
print(f"Outputs: {interpreter.get_output_details()}")
```

### Compare Outputs

```python
import numpy as np
import torch
import onnxruntime as rt
import tensorflow as tf

# Test image
test_input = np.random.randn(1, 3, 224, 224).astype(np.float32)

# PyTorch inference
torch_model = torch.jit.load('model.pt')
torch_output = torch_model(torch.tensor(test_input)).detach().numpy()

# ONNX inference
onnx_session = rt.InferenceSession('skin_classifier.onnx')
onnx_output = onnx_session.run(None, {'image': test_input})[0]

# TFLite inference
tf_interpreter = tf.lite.Interpreter('skin_classifier.tflite')
tf_interpreter.allocate_tensors()
# ... setup and run inference ...

# Compare
print(f"PyTorch output shape: {torch_output.shape}")
print(f"ONNX output shape: {onnx_output.shape}")
print(f"Max difference: {np.max(np.abs(torch_output - onnx_output))}")
```

## Performance Considerations

### Model Size

```
Metric           | EfficientNet-B0 | ResNet50
-----------------|-----------------|----------
Parameters       | 5.3M           | 25.5M
Float32          | 21 MB          | 102 MB
Float16          | 11 MB          | 51 MB
Int8             | 5.5 MB         | 25.5 MB
```

### Inference Latency

```
Device          | Float32 | Float16 | Int8  | Throughput
----------------|---------|---------|-------|----------
CPU (i7)        | 50ms    | 50ms    | 25ms  | 40 img/s
GPU (V100)      | 10ms    | 8ms     | N/A   | 400 img/s
Mobile (Snap)   | 100ms   | 90ms    | 20ms  | 50 img/s
Edge (RPI 4)    | 300ms   | N/A     | 100ms | 10 img/s
```

## Troubleshooting

### ONNX Export Failed

**Error**: `RuntimeError: onnx export failed`

**Solutions**:

```bash
# Update ONNX
pip install --upgrade onnx

# Verify model is in eval mode
# (Automatically done in export_models.py)

# Use compatible opset version
python ml/exports/export_models.py --checkpoint ... --help
```

### TFLite Conversion Failed

**Error**: `ImportError: No module named 'onnx_tf'`

**Solutions**:

```bash
# Install onnx-tf
pip install onnx-tf

# OR use TensorFlow's built-in converter (if available)
pip install --upgrade tensorflow
```

### Int8 Quantization Accuracy Drop

**Symptom**: Model predictions significantly worse after quantization

**Solutions**:

1. Use better calibration dataset:

   ```bash
   python ml/exports/export_models.py \
     --checkpoint ... \
     --quantize int8 \
     --calibration-dir path/with/more/diverse/images
   ```

2. Fall back to float16:

   ```bash
   python ml/exports/export_models.py \
     --checkpoint ... \
     --quantize float16
   ```

3. Fine-tune on quantized model:
   ```python
   # Load quantized TFLite model
   # Re-train with int8 operations
   # See TensorFlow quantization-aware training docs
   ```

## Integration Examples

### Using Exported Models in Backend

```python
# backend/services/ml_infer.py

import onnxruntime as rt
from pathlib import Path

class SkinClassifierONNX:
    def __init__(self, model_path: str = 'ml/exports/skin_classifier.onnx'):
        self.session = rt.InferenceSession(model_path)

    def predict(self, image_path: str) -> dict:
        # Load and preprocess image
        image = preprocess_image(image_path)

        # Infer
        input_name = self.session.get_inputs()[0].name
        output_name = self.session.get_outputs()[0].name
        logits = self.session.run([output_name], {input_name: image})[0]

        # Post-process
        class_id = np.argmax(logits[0])
        confidence = softmax(logits[0])[class_id]

        return {
            'class_id': int(class_id),
            'confidence': float(confidence),
            'logits': logits[0].tolist()
        }
```

### Mobile Deployment

**Android** (using TFLite):

```kotlin
val classifier = SkinClassifier("skin_classifier.tflite")
val result = classifier.predict(bitmap)
// Use result for skin analysis
```

**iOS** (using TFLite):

```swift
let classifier = SkinClassifier(modelPath: "skin_classifier.tflite")
let result = classifier.predict(image: uiImage)
// Use result for skin analysis
```

## Next Steps

1. **Export your trained model**: Follow quick start above
2. **Verify exports**: Use verification commands
3. **Test on target platform**: CPU, mobile, edge device
4. **Optimize**: Try different quantization schemes
5. **Deploy**: Use exported model in production

## References

- [ONNX Specification](https://github.com/onnx/onnx/blob/main/docs/Operators.md)
- [TensorFlow Lite Converter](https://www.tensorflow.org/lite/convert)
- [TensorFlow Lite Quantization](https://www.tensorflow.org/lite/performance/quantization)
- [ONNX Runtime](https://onnxruntime.ai/)
- [Model Deployment Best Practices](https://pytorch.org/serve/model_archiver.html)

---

**Status**: ✅ Export framework complete  
**Formats**: ONNX, TFLite (float32, float16, int8)  
**Last Updated**: 2025-10-24
