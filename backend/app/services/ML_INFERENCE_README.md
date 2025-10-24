# Backend ML Inference Service Integration

## Overview

The `ml_infer.py` module provides production-ready ML inference for the Haski backend API. It integrates exported TFLite and ONNX models with intelligent fallback to mock responses for testing.

## Features

- **Dual Model Support**: TFLite (priority) and ONNX (fallback) inference
- **Intelligent Fallback**: Uses mock responses when models unavailable (for testing)
- **Image Format Support**: Accepts file paths or raw bytes
- **ImageNet Preprocessing**: Proper normalization (224×224, mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
- **Structured Output**: JSON-compatible response with confidence scores
- **Production Logging**: Detailed logging for debugging and monitoring

## Main API

### `analyze_image(image: Union[bytes, str]) -> dict`

Analyze an image and return structured prediction results.

**Parameters:**

- `image` (Union[bytes, str]): File path or image bytes (JPEG/PNG)

**Returns:**

```json
{
  "skin_type": "combination",
  "hair_type": "wavy",
  "conditions_detected": ["mild_acne"],
  "confidence_scores": {
    "skin_type": 0.84,
    "hair_type": 0.76,
    "condition": 0.67
  },
  "model_version": "v1-exported",
  "model_type": "tflite" // or "onnx" or "mock"
}
```

**Example Usage:**

```python
from services.ml_infer import analyze_image

# From file path
result = analyze_image("path/to/image.jpg")

# From bytes
with open("image.jpg", "rb") as f:
    result = analyze_image(f.read())

print(f"Skin type: {result['skin_type']}")
print(f"Conditions: {result['conditions_detected']}")
```

### `analyze_image_local(image_path: str) -> dict`

Convenience wrapper for local file analysis.

```python
from services.ml_infer import analyze_image_local

result = analyze_image_local("path/to/image.jpg")
```

## Class Mappings

### Skin Types (5 classes)

- `normal`
- `dry`
- `oily`
- `combination`
- `sensitive`

### Hair Types (4 classes)

- `straight`
- `wavy`
- `curly`
- `coily`

### Skin Conditions (5 classes)

- `healthy` (no conditions detected when this is predicted)
- `mild_acne`
- `severe_acne`
- `eczema`
- `psoriasis`

## Model Priority

The service attempts to load models in this order:

1. **TFLite** (`ml/exports/skin_classifier.tflite`)
   - Optimized for on-device and edge inference
   - Smallest model size (~5-10 MB)
   - Fastest inference (~10-50ms)
2. **ONNX** (`ml/exports/skin_classifier.onnx`)
   - Cross-platform inference
   - Good performance on servers
   - Requires onnxruntime
3. **Mock** (Fallback for testing)
   - Used when no models available
   - Returns deterministic test responses
   - Allows testing without models

## Installation & Setup

### 1. Export Models

The exported models must be present in `ml/exports/`:

```bash
# From project root
python ml/exports/export_models.py --checkpoint /path/to/model.pt
```

This creates:

- `ml/exports/skin_classifier.onnx` (ONNX format)
- `ml/exports/skin_classifier.tflite` (TFLite format)

### 2. Install Dependencies

**For TFLite inference:**

```bash
pip install tflite-runtime  # Lightweight, recommended
# OR
pip install tensorflow      # Full TensorFlow (larger)
```

**For ONNX inference:**

```bash
pip install onnxruntime
```

**Always required:**

```bash
pip install pillow numpy
```

### 3. Backend Integration

Add to your FastAPI/Flask endpoint:

```python
from fastapi import File, UploadFile
from services.ml_infer import analyze_image

@app.post("/api/v1/analyze")
async def analyze_skin(file: UploadFile = File(...)):
    image_bytes = await file.read()
    result = analyze_image(image_bytes)
    return result
```

## Preprocessing Details

Images are preprocessed as follows:

1. **Load**: RGB image from file or bytes
2. **Resize**: To 224×224 pixels
3. **Normalize**: Divide by 255 to [0, 1]
4. **Standardize**: Apply ImageNet normalization
   - Mean: [0.485, 0.456, 0.406]
   - Std: [0.229, 0.224, 0.225]
5. **Batch**: Add batch dimension (1, 224, 224, 3)
6. **Transpose**: Convert to ONNX format (1, 3, 224, 224) if using ONNX

## Postprocessing Details

1. **Softmax**: Convert logits to probabilities
2. **Split**: Separate predictions by class type
   - Skin type: indices 0-4
   - Hair type: indices 5-8
   - Condition: indices 9-13
3. **Argmax**: Get most confident class
4. **Map**: Convert class IDs to names
5. **Confidence**: Extract probability for predicted class

## Quantization Handling

The service automatically handles quantized models (int8, uint8):

- **Input quantization**: Converts float images to uint8 when needed
- **Output dequantization**: Converts uint8 logits back to float using scale/zero_point

This is transparent to the caller.

## Logging & Debugging

The module uses Python's `logging` module with INFO level by default.

Enable debug logging:

```python
import logging
logging.basicConfig(level=logging.DEBUG)

from services.ml_infer import analyze_image
result = analyze_image("image.jpg")  # More verbose output
```

### Debug environment variable (optional)

```bash
export ML_DEBUG_DIR=/path/to/debug
# Saves last analysis results to /path/to/debug/last_analysis.json
```

## Error Handling

The service gracefully handles various error scenarios:

| Scenario                    | Behavior                      |
| --------------------------- | ----------------------------- |
| Models not found            | Uses mock responses           |
| Image file not found        | Raises `FileNotFoundError`    |
| Invalid image format        | Falls back to mock            |
| Inference fails             | Tries next model or uses mock |
| No models + no dependencies | Returns mock response         |

## Performance Characteristics

Typical inference latencies (on modern hardware):

| Model            | Format  | Hardware | Latency  | Notes              |
| ---------------- | ------- | -------- | -------- | ------------------ |
| TFLite (float32) | .tflite | CPU      | 10-20 ms | Recommended        |
| TFLite (int8)    | .tflite | CPU      | 5-10 ms  | Quantized, fastest |
| ONNX             | .onnx   | CPU      | 20-40 ms | Cross-platform     |
| ONNX             | .onnx   | GPU      | 5-10 ms  | With CUDA          |
| Mock             | -       | -        | <1 ms    | No processing      |

## Testing

Run the included test suite:

```bash
cd backend/app/services
python test_ml_infer.py
```

Tests cover:

- ✓ Class mappings validation
- ✓ Model initialization
- ✓ Response format validation
- ✓ Byte input inference
- ✓ File path input inference
- ✓ Local wrapper functionality

## Troubleshooting

### "No module named 'onnxruntime'"

```bash
pip install onnxruntime
```

### "No module named 'tensorflow'"

```bash
pip install tensorflow
# OR just use tflite_runtime (lightweight)
pip install tflite-runtime
```

### "Models not found" warning

Ensure exported models are in `ml/exports/`:

```bash
ls ml/exports/skin_classifier.*
```

If not present, export them:

```bash
python ml/exports/export_models.py --checkpoint path/to/pytorch/model.pt
```

### Slow inference

1. Check if TFLite is being used (faster than ONNX)
2. Use quantized int8 model for even faster inference
3. If GPU available, ensure CUDA is enabled for ONNX

### Image preprocessing issues

Ensure image is valid RGB:

- Supported formats: JPEG, PNG, BMP, etc.
- Minimum size: 224×224 (smaller images will be upscaled)
- Automatically converted to RGB

## Architecture

```
analyze_image(image)
    ↓
[Initialize models if needed]
    ↓
Handle input (path or bytes)
    ↓
Preprocess image (resize, normalize)
    ↓
[Try TFLite inference]
    ↓
[If failed, try ONNX inference]
    ↓
[If both failed, use mock response]
    ↓
Postprocess (logits → predictions)
    ↓
Format response (JSON-compatible dict)
    ↓
Return result
```

## Future Enhancements

- [ ] Batch inference for multiple images
- [ ] Model versioning and A/B testing
- [ ] Performance caching
- [ ] WebP and AVIF image support
- [ ] Model optimization (pruning, distillation)
- [ ] Confidence thresholding

## Version History

- **v1-exported** (current): Uses exported TFLite/ONNX models with intelligent fallback
- v0-mock: Mock-only responses for development

## Files

- `ml_infer.py` - Main inference service module
- `test_ml_infer.py` - Test suite
- `../../../ml/exports/export_models.py` - Model export utility
- `../../../ml/exports/example_inference.py` - Example usage patterns
