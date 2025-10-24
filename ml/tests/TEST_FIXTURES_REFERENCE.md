# Test Fixtures Reference

Comprehensive guide to all fixtures available in the ML inference test suite.

## Quick Reference Table

| Fixture                       | Scope    | Returns | Auto-Creates | Used For                |
| ----------------------------- | -------- | ------- | ------------ | ----------------------- |
| `ml_base_dir`                 | session  | Path    | No           | ML directory reference  |
| `test_data_dir`               | session  | Path    | Yes          | Test data directory     |
| `exports_dir`                 | session  | Path    | Yes          | Model exports directory |
| `sample_classification_image` | function | Path    | Yes          | Classification tests    |
| `sample_detection_image`      | function | Path    | Yes          | Detection tests         |
| `tflite_model_path`           | function | str     | No           | TFLite model reference  |
| `onnx_model_path`             | function | str     | No           | ONNX model reference    |
| `models_info`                 | function | dict    | No           | Model availability info |

## Fixture Details

### Session-Scoped Fixtures (Created Once)

These fixtures are created once per test session and reused across all tests.

#### `ml_base_dir`

**Definition**:

```python
@pytest.fixture(scope="session")
def ml_base_dir():
    """Get ML base directory."""
    return Path(__file__).parent.parent
```

**Returns**: `Path` object pointing to `ml/` directory

**Location**: `d:\Haski-main\ml\`

**Example Usage**:

```python
def test_ml_structure(ml_base_dir):
    """Verify ML directory structure."""
    assert (ml_base_dir / "data").exists()
    assert (ml_base_dir / "exports").exists()
    assert (ml_base_dir / "training").exists()
```

**Common Operations**:

```python
# Get subdirectories
data_dir = ml_base_dir / "data"
exports_dir = ml_base_dir / "exports"
monitoring_dir = ml_base_dir / "monitoring"

# Check existence
assert ml_base_dir.exists()

# Get files
readme = ml_base_dir / "README.md"
```

---

#### `test_data_dir`

**Definition**:

```python
@pytest.fixture(scope="session")
def test_data_dir(ml_base_dir):
    """Get test data directory."""
    data_dir = ml_base_dir / "data" / "test"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir
```

**Returns**: `Path` object pointing to `ml/data/test/`

**Location**: `d:\Haski-main\ml\data\test\`

**Auto-Creates**: Yes (if doesn't exist)

**Created Paths**:

- `ml/data/test/sample_classification.jpg` - Classification test image
- `ml/data/test/sample_detection.jpg` - Detection test image
- `ml/data/test/corrupted.jpg` - Corrupted image (in error handling tests)

**Example Usage**:

```python
def test_with_test_data(test_data_dir):
    """Use test data directory."""
    # List all test images
    images = list(test_data_dir.glob("*.jpg"))
    assert len(images) > 0

    # Create custom test file
    custom_file = test_data_dir / "custom_test.txt"
    custom_file.write_text("test data")
```

**Directory Contents After Tests**:

```
ml/data/test/
├── sample_classification.jpg    (224×224 RGB, random)
├── sample_detection.jpg         (224×224 RGB, gradient)
└── (temporary test files)
```

---

#### `exports_dir`

**Definition**:

```python
@pytest.fixture(scope="session")
def exports_dir(ml_base_dir):
    """Get exports directory."""
    exports_dir = ml_base_dir / "exports"
    exports_dir.mkdir(parents=True, exist_ok=True)
    return exports_dir
```

**Returns**: `Path` object pointing to `ml/exports/`

**Location**: `d:\Haski-main\ml\exports\`

**Auto-Creates**: Yes (if doesn't exist)

**Expected Contents**:

```
ml/exports/
├── skin_classifier.tflite       (TFLite quantized model, optional)
├── skin_classifier.onnx         (ONNX model, optional)
├── representative_data.py       (Calibration data generator)
└── (other model artifacts)
```

**Example Usage**:

```python
def test_model_availability(exports_dir):
    """Check if models exist."""
    tflite_path = exports_dir / "skin_classifier.tflite"
    onnx_path = exports_dir / "skin_classifier.onnx"

    tflite_exists = tflite_path.exists()
    onnx_exists = onnx_path.exists()

    # At least one should exist or mock fallback will be used
    if not tflite_exists and not onnx_exists:
        pytest.skip("No real models available, will use mock")
```

**Note**: Tests gracefully handle missing models by using mock inference.

---

### Function-Scoped Fixtures (Created Per Test)

These fixtures are created fresh for each test function that requests them.

#### `sample_classification_image`

**Definition**:

```python
@pytest.fixture
def sample_classification_image(test_data_dir):
    """Create or load a sample classification image."""
    test_image_path = test_data_dir / "sample_classification.jpg"

    if test_image_path.exists():
        return test_image_path

    # Create synthetic test image (224x224 RGB)
    img_array = np.random.randint(0, 256, (224, 224, 3), dtype=np.uint8)
    img = Image.fromarray(img_array, 'RGB')
    test_data_dir.mkdir(parents=True, exist_ok=True)
    img.save(test_image_path)

    return test_image_path
```

**Returns**: `Path` object pointing to test image file

**File Path**: `ml/data/test/sample_classification.jpg`

**Image Spec**:

- **Format**: JPEG
- **Resolution**: 224×224 pixels
- **Color Space**: RGB (3 channels)
- **Content**: Random pixel values (0-255)

**Creation Strategy**:

1. Check if image already exists → Use it
2. If missing → Create synthetic random image
3. Save to `ml/data/test/sample_classification.jpg`

**Example Usage**:

```python
def test_classification(sample_classification_image):
    """Test classification with sample image."""
    # Get path
    image_path = sample_classification_image

    # Use as string
    result = analyze_image(str(image_path))

    # Verify result
    assert result['skin_type'] in ["normal", "dry", "oily", "combination", "sensitive"]
    assert result['hair_type'] in ["straight", "wavy", "curly", "coily"]
```

**Load as Bytes**:

```python
def test_bytes_input(sample_classification_image):
    """Test with bytes input."""
    with open(sample_classification_image, 'rb') as f:
        image_bytes = f.read()

    result = analyze_image(image_bytes)
    assert result is not None
```

**Preprocess First**:

```python
def test_preprocessing(sample_classification_image):
    """Test preprocessing pipeline."""
    preprocessed = preprocess_image(str(sample_classification_image))

    # Check shape
    assert preprocessed.shape == (1, 3, 224, 224)

    # Check type
    assert preprocessed.dtype == np.float32
```

---

#### `sample_detection_image`

**Definition**:

```python
@pytest.fixture
def sample_detection_image(test_data_dir):
    """Create or load a sample detection image."""
    test_image_path = test_data_dir / "sample_detection.jpg"

    if test_image_path.exists():
        return test_image_path

    # Create synthetic test image with gradients
    img_array = np.zeros((224, 224, 3), dtype=np.uint8)

    for i in range(224):
        for j in range(224):
            img_array[i, j] = [
                (i * 255) // 224,      # Vertical gradient (red)
                (j * 255) // 224,      # Horizontal gradient (green)
                ((i + j) * 255) // 448 # Diagonal gradient (blue)
            ]

    img = Image.fromarray(img_array, 'RGB')
    test_data_dir.mkdir(parents=True, exist_ok=True)
    img.save(test_image_path)

    return test_image_path
```

**Returns**: `Path` object pointing to detection test image

**File Path**: `ml/data/test/sample_detection.jpg`

**Image Spec**:

- **Format**: JPEG
- **Resolution**: 224×224 pixels
- **Color Space**: RGB with gradient patterns
- **Content**: Smooth color gradients (more realistic than random)

**Gradient Pattern**:

```
Red Channel:    0→255 (top→bottom, vertical)
Green Channel:  0→255 (left→right, horizontal)
Blue Channel:   0→255 (diagonal)
```

**Visual**: Creates a smooth color transition, more realistic for detection

**Example Usage**:

```python
def test_detection(sample_detection_image):
    """Test detection with gradient image."""
    image_path = sample_detection_image

    result = analyze_image(str(image_path))
    assert result is not None
    assert result['model_type'] in ['tflite', 'onnx', 'mock']
```

**Difference from Classification Image**:

- Classification: Random noise (tests robustness)
- Detection: Gradient pattern (more realistic structure)

---

#### `tflite_model_path`

**Definition**:

```python
@pytest.fixture
def tflite_model_path(exports_dir):
    """Get TFLite model path."""
    model_path = exports_dir / "skin_classifier.tflite"
    return str(model_path)
```

**Returns**: `str` with path to TFLite model

**File Path**: `ml/exports/skin_classifier.tflite`

**Important**: Returns path even if file doesn't exist (inference handles gracefully)

**Example Usage**:

```python
def test_tflite_inference(tflite_model_path):
    """Test TFLite model if available."""
    model_path = Path(tflite_model_path)

    if model_path.exists():
        # Test with real model
        inference = TFLiteInference(tflite_model_path)
        result = inference.predict(test_array)
    else:
        # Skip or test mock
        pytest.skip("TFLite model not available")
```

**With models_info Fixture**:

```python
def test_tflite_conditional(tflite_model_path, models_info):
    """Conditionally test TFLite."""
    if models_info['tflite_available']:
        # Use real model
        pass
    else:
        # Use mock or skip
        pytest.skip("TFLite not available")
```

---

#### `onnx_model_path`

**Definition**:

```python
@pytest.fixture
def onnx_model_path(exports_dir):
    """Get ONNX model path."""
    model_path = exports_dir / "skin_classifier.onnx"
    return str(model_path)
```

**Returns**: `str` with path to ONNX model

**File Path**: `ml/exports/skin_classifier.onnx`

**Important**: Returns path even if file doesn't exist (inference handles gracefully)

**Example Usage**:

```python
def test_onnx_inference(onnx_model_path):
    """Test ONNX model if available."""
    model_path = Path(onnx_model_path)

    if model_path.exists():
        inference = ONNXInference(onnx_model_path)
        result = inference.predict(test_array)
    else:
        pytest.skip("ONNX model not available")
```

---

#### `models_info`

**Definition**:

```python
@pytest.fixture
def models_info():
    """Provide information about available models."""
    return {
        'tflite_available': Path('ml/exports/skin_classifier.tflite').exists(),
        'onnx_available': Path('ml/exports/skin_classifier.onnx').exists(),
    }
```

**Returns**: `dict` with model availability flags

**Structure**:

```python
{
    'tflite_available': bool,  # True if ml/exports/skin_classifier.tflite exists
    'onnx_available': bool     # True if ml/exports/skin_classifier.onnx exists
}
```

**Example Usage**:

```python
def test_model_selection(models_info):
    """Choose model based on availability."""
    if models_info['tflite_available']:
        model = TFLiteInference("ml/exports/skin_classifier.tflite")
        result = model.predict(test_array)
    elif models_info['onnx_available']:
        model = ONNXInference("ml/exports/skin_classifier.onnx")
        result = model.predict(test_array)
    else:
        # Fall back to mock or skip
        pytest.skip("No real models available")
```

**Practical Pattern**:

```python
def test_inference_with_best_available(sample_classification_image, models_info):
    """Use the best available model."""
    image_path = sample_classification_image

    # Inference system will automatically use best available
    result = analyze_image(str(image_path))

    # Verify which one was used
    if models_info['tflite_available']:
        assert result['model_type'] in ['tflite', 'onnx', 'mock']
    else:
        # Could be onnx or mock
        pass
```

---

## Fixture Combinations

Common fixture combinations for different test scenarios:

### Classification Test

```python
def test_classification(sample_classification_image):
    """Needs just one image fixture."""
    result = analyze_image(str(sample_classification_image))
    assert result['skin_type'] is not None
```

### Multi-Format Test

```python
def test_formats(sample_classification_image):
    """Test both file path and bytes."""
    # File path
    result1 = analyze_image(str(sample_classification_image))

    # Bytes
    with open(sample_classification_image, 'rb') as f:
        result2 = analyze_image(f.read())

    assert result1 == result2
```

### Model Selection Test

```python
def test_model_selection(sample_classification_image, models_info):
    """Check which model was used."""
    result = analyze_image(str(sample_classification_image))

    if models_info['tflite_available']:
        assert result['model_type'] in ['tflite', 'onnx', 'mock']
```

### Directory Structure Test

```python
def test_structure(ml_base_dir, test_data_dir, exports_dir):
    """Verify entire directory structure."""
    assert ml_base_dir.exists()
    assert test_data_dir.exists()
    assert exports_dir.exists()
```

---

## Fixture Lifecycle

### Session Lifetime

```
pytest starts
  ↓
ml_base_dir created (session scope)
test_data_dir created (session scope)
exports_dir created (session scope)
  ↓
[All tests run, these fixtures reused]
  ↓
Session ends, fixtures cleaned up
```

### Function Lifetime

```
Each test function
  ↓
sample_classification_image created (or reused from cache)
sample_detection_image created (or reused from cache)
tflite_model_path provided
onnx_model_path provided
models_info computed
  ↓
Test runs
  ↓
Fixtures available for next test
```

---

## Best Practices

### 1. Use Appropriate Scope

```python
# ✅ GOOD: Image path fixture (per-function, lightweight)
def test_something(sample_classification_image):
    pass

# ❌ AVOID: Creating image in every test
def test_something():
    image = create_image()  # Wasteful
    pass
```

### 2. Check Availability Before Use

```python
# ✅ GOOD: Check if available
def test_tflite(models_info):
    if models_info['tflite_available']:
        # Test TFLite
        pass
    else:
        pytest.skip("TFLite not available")

# ❌ AVOID: Assuming model exists
def test_tflite(tflite_model_path):
    # May fail if model missing
    pass
```

### 3. Use Descriptive Assertions

```python
# ✅ GOOD: Clear assertion
assert result['skin_type'] in ["normal", "dry", "oily", "combination", "sensitive"]

# ❌ AVOID: Vague check
assert result.get('skin_type')  # Passes for empty string!
```

### 4. Combine Fixtures Logically

```python
# ✅ GOOD: Related fixtures together
def test_full_pipeline(sample_classification_image, models_info):
    # Test with specific model selection
    pass

# ❌ AVOID: Unused fixtures
def test_something(sample_classification_image, exports_dir, ml_base_dir):
    # Only using image, others unused
    result = analyze_image(str(sample_classification_image))
```

---

## Troubleshooting Fixtures

### Fixture Not Found

**Error**: `fixture 'sample_image' not found`

**Cause**: Typo in fixture name or fixture in wrong scope

**Solution**: Check spelling in conftest.py:

```python
# Make sure fixture is defined
@pytest.fixture
def sample_classification_image(test_data_dir):
    ...
```

### Import Errors in Fixtures

**Error**: `ModuleNotFoundError` in fixture

**Solution**: Fixtures run before tests, ensure imports work:

```python
# In conftest.py
import sys
from pathlib import Path

# Add backend to path
backend_path = Path(__file__).parent.parent.parent / "backend"
sys.path.insert(0, str(backend_path))
```

### Fixture Times Out

**Error**: `Timeout` creating fixture

**Cause**: Fixture trying to download model or create large files

**Solution**:

- Check network connectivity
- Verify disk space
- Increase pytest timeout: `pytest --timeout=300`

---

## Advanced Fixture Patterns

### Parameterized Fixtures

```python
@pytest.fixture(params=['tflite', 'onnx'])
def model_format(request):
    """Test with multiple model formats."""
    return request.param

def test_inference(model_format, sample_classification_image):
    """Runs twice: once for tflite, once for onnx."""
    # Use model_format to select model
    pass
```

### Fixture with Cleanup

```python
@pytest.fixture
def temp_test_file(test_data_dir):
    """Create temporary test file with cleanup."""
    filepath = test_data_dir / "temp.txt"
    filepath.write_text("test")

    yield filepath  # Test uses this

    # Cleanup
    filepath.unlink()
```

### Conditional Fixtures

```python
@pytest.fixture
def optional_model(models_info):
    """Return model if available, else None."""
    if models_info['tflite_available']:
        return TFLiteInference("ml/exports/skin_classifier.tflite")
    return None

def test_optional(optional_model):
    """Test handles None gracefully."""
    if optional_model:
        result = optional_model.predict(array)
    else:
        # Test mock mode
        pass
```

---

## Summary

| Fixture                       | When to Use                 | Returns |
| ----------------------------- | --------------------------- | ------- |
| `ml_base_dir`                 | Need ML directory path      | Path    |
| `test_data_dir`               | Need test data location     | Path    |
| `exports_dir`                 | Need model directory        | Path    |
| `sample_classification_image` | Testing classification      | Path    |
| `sample_detection_image`      | Testing detection           | Path    |
| `tflite_model_path`           | Need TFLite model reference | str     |
| `onnx_model_path`             | Need ONNX model reference   | str     |
| `models_info`                 | Need model availability     | dict    |

All fixtures handle missing files/directories gracefully, allowing tests to pass even with mock inference!
