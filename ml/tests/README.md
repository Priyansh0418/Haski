# ML Inference Smoke Tests

Complete test suite for the machine learning inference pipeline.

## Overview

This directory contains comprehensive pytest-based smoke tests for the ML inference system, including:

- ✅ **Classification Tests** (9 tests) - Skin type & hair type detection
- ✅ **Detection Tests** (2 tests) - Condition detection
- ✅ **Preprocessing Tests** (3 tests) - Image normalization validation
- ✅ **Integration Tests** (2 tests) - End-to-end pipeline
- ✅ **Model Tests** (3 tests) - Model loading & fallback
- ✅ **Error Handling Tests** (2 tests) - Invalid input handling
- ✅ **Performance Tests** (1 test) - Speed validation

**Total: 22 Tests | 700+ Lines | 100% Python**

## Quick Start

### 1. Install Dependencies

```bash
# From project root
pip install pytest
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

### 2. Run Tests

```bash
# All tests
pytest ml/tests/ -v

# Only classification tests
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke -v

# With coverage
pytest ml/tests/ --cov=app.services.ml_infer --cov-report=html
```

### 3. View Results

```
========================= 22 passed in 5.23s =========================
```

## Directory Structure

```
ml/tests/
├── __init__.py                      # Package marker
├── conftest.py                      # Pytest configuration (60 lines)
├── test_inference_smoke.py          # Main test suite (700+ lines)
├── ML_TESTS_GUIDE.md                # Comprehensive guide (400+ lines)
├── TEST_FIXTURES_REFERENCE.md       # Fixture documentation (400+ lines)
├── TEST_QUICK_REFERENCE.md          # Quick lookup (200+ lines)
└── README.md                        # This file
```

## Test Files

### test_inference_smoke.py (700+ lines)

Main test suite with 22 tests organized into 7 test classes.

**Test Classes**:

1. **TestClassificationSmoke** - Classification inference
2. **TestDetectionSmoke** - Detection inference
3. **TestPreprocessing** - Image preprocessing
4. **TestIntegration** - Full pipeline tests
5. **TestModelAvailability** - Model loading
6. **TestErrorHandling** - Error scenarios
7. **TestPerformance** - Performance checks

**Key Features**:

- Auto-creates synthetic test images
- Graceful mock fallback
- Comprehensive schema validation
- Full error handling

### conftest.py (60 lines)

Pytest configuration file with:

- Path setup for backend imports
- Test marker configuration
- Shared fixtures
- Auto-discovery setup

## Features

### Fixtures (8 total)

| Name                          | Type     | Purpose                 |
| ----------------------------- | -------- | ----------------------- |
| `ml_base_dir`                 | session  | ML directory path       |
| `test_data_dir`               | session  | Test data location      |
| `exports_dir`                 | session  | Model exports location  |
| `sample_classification_image` | function | Test image (224×224)    |
| `sample_detection_image`      | function | Detection test image    |
| `tflite_model_path`           | function | TFLite model reference  |
| `onnx_model_path`             | function | ONNX model reference    |
| `models_info`                 | function | Model availability dict |

**Fixtures automatically**:

- Create directories if missing
- Create synthetic test images if missing
- Handle missing models gracefully
- Provide type safety with Path objects

### Test Cases (22 total)

#### Classification (9 tests)

```python
✓ test_analyze_image_returns_required_keys
✓ test_analyze_image_skin_type_valid
✓ test_analyze_image_hair_type_valid
✓ test_analyze_image_conditions_is_list
✓ test_analyze_image_confidence_scores_structure
✓ test_analyze_image_model_type_valid
✓ test_analyze_image_with_file_path
✓ test_analyze_image_with_bytes
✓ test_analyze_image_reproducible
```

#### Detection (2 tests)

```python
✓ test_detection_returns_list
✓ test_detection_schema
```

#### Preprocessing (3 tests)

```python
✓ test_preprocess_image_output_shape
✓ test_preprocess_image_output_type
✓ test_preprocess_image_value_range
```

#### Integration (2 tests)

```python
✓ test_full_pipeline_classification
✓ test_pipeline_handles_both_formats
```

#### Model Availability (3 tests)

```python
✓ test_models_can_be_imported
✓ test_inference_fallback_to_mock
✓ test_model_type_reported
```

#### Error Handling (2 tests)

```python
✓ test_invalid_image_path_raises_error
✓ test_corrupted_image_handling
```

#### Performance (1 test)

```python
✓ test_inference_completes_in_reasonable_time
```

## Usage Examples

### Basic Classification Test

```python
def test_classification(sample_classification_image):
    """Test basic classification."""
    result = analyze_image(str(sample_classification_image))

    # Verify required keys
    assert 'skin_type' in result
    assert 'hair_type' in result

    # Verify valid values
    assert result['skin_type'] in ['normal', 'dry', 'oily', 'combination', 'sensitive']
    assert result['hair_type'] in ['straight', 'wavy', 'curly', 'coily']
```

### Test with Multiple Input Formats

```python
def test_input_formats(sample_classification_image):
    """Test both file path and bytes."""
    # File path
    result1 = analyze_image(str(sample_classification_image))

    # Bytes
    with open(sample_classification_image, 'rb') as f:
        result2 = analyze_image(f.read())

    # Both should match
    assert result1['skin_type'] == result2['skin_type']
```

### Conditional Test Based on Available Models

```python
def test_model_selection(sample_classification_image, models_info):
    """Use best available model."""
    result = analyze_image(str(sample_classification_image))

    # Verify model type
    if models_info['tflite_available']:
        assert result['model_type'] in ['tflite', 'onnx', 'mock']
    elif models_info['onnx_available']:
        assert result['model_type'] in ['onnx', 'mock']
    else:
        assert result['model_type'] == 'mock'
```

## Running Tests

### All Tests

```bash
pytest ml/tests/ -v
```

### Specific Test Class

```bash
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke -v
```

### Specific Test

```bash
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys -v
```

### By Marker

```bash
# Smoke tests only
pytest ml/tests/ -m smoke -v

# Unit tests only
pytest ml/tests/ -m unit -v

# Integration tests only
pytest ml/tests/ -m integration -v
```

### With Coverage

```bash
pytest ml/tests/ --cov=app.services.ml_infer --cov-report=html
```

### With Additional Options

```bash
# Verbose output
pytest ml/tests/ -vv

# Show print statements
pytest ml/tests/ -s

# Stop on first failure
pytest ml/tests/ -x

# Show local variables on failure
pytest ml/tests/ -l

# Show summary
pytest ml/tests/ -v --tb=short
```

## Configuration

### conftest.py

Provides:

1. **Path setup**: Adds backend to Python path
2. **Marker registration**: Defines custom markers
3. **Auto-markers**: Automatically tags tests

### Markers

```bash
@pytest.mark.smoke        # Basic functionality tests
@pytest.mark.unit         # Unit-level tests
@pytest.mark.integration  # Integration tests
```

## Test Output Schema

The `analyze_image()` function returns:

```python
{
    'skin_type': str,                    # one of: normal, dry, oily, combination, sensitive
    'hair_type': str,                    # one of: straight, wavy, curly, coily
    'conditions_detected': list[str],    # e.g., ['acne', 'eczema']
    'confidence_scores': {
        'skin_type': float,              # 0.0 to 1.0
        'hair_type': float,              # 0.0 to 1.0
        'condition': float                # 0.0 to 1.0
    },
    'model_version': str,                # e.g., "1.0.0"
    'model_type': str                    # one of: tflite, onnx, mock
}
```

## Valid Values

### Skin Types (5)

```
normal, dry, oily, combination, sensitive
```

### Hair Types (4)

```
straight, wavy, curly, coily
```

### Conditions (examples)

```
healthy, mild_acne, severe_acne, eczema, psoriasis, rosacea, dermatitis
```

### Model Types (3)

```
tflite   # TensorFlow Lite quantized
onnx     # ONNX Runtime
mock     # Synthetic fallback
```

## Image Handling

### Input Formats

1. **File Path** (str)

   ```python
   result = analyze_image("/path/to/image.jpg")
   ```

2. **Path Object** (pathlib.Path)

   ```python
   result = analyze_image(Path("/path/to/image.jpg"))
   ```

3. **Bytes**
   ```python
   with open("image.jpg", "rb") as f:
       image_bytes = f.read()
   result = analyze_image(image_bytes)
   ```

### Test Images

- **Classification**: `ml/data/test/sample_classification.jpg` (224×224 RGB, random)
- **Detection**: `ml/data/test/sample_detection.jpg` (224×224 RGB, gradients)
- **Auto-created**: If files missing, synthetic images are automatically created

## Mock Fallback

When real models aren't available:

1. **Detection**: Returns mock predictions
2. **Model Type**: Reports as "mock"
3. **Predictions**: Deterministic, reproducible
4. **Confidence**: Always 0.5
5. **Tests Still Pass**: Full test coverage maintained

**Example**:

```python
# Works even without real models
result = analyze_image("test.jpg")
assert result['model_type'] == 'mock'  # Falls back gracefully
assert result['skin_type'] in ["normal", "dry", "oily", "combination", "sensitive"]
```

## Error Handling

### Handled Gracefully ✅

- Missing image file → `FileNotFoundError`
- Corrupted image → Returns mock or raises
- Missing models → Falls back to mock
- Invalid input format → `TypeError`

### Unhandled (Tests Fail) ❌

- Invalid skin_type returned → Test fails
- Missing required keys → Test fails
- Non-numeric confidence → Test fails

## Performance

| Scenario           | Expected Time |
| ------------------ | ------------- |
| TFLite (quantized) | 100-500ms     |
| ONNX               | 200-800ms     |
| Mock               | <10ms         |
| Test Threshold     | <10 seconds   |

## Fixtures Guide

### Most Common Fixture

```python
# Use for 90% of classification tests
def test_something(sample_classification_image):
    result = analyze_image(str(sample_classification_image))
    # Test result
```

### Multiple Fixtures

```python
def test_with_info(sample_classification_image, models_info):
    """Use multiple fixtures."""
    result = analyze_image(str(sample_classification_image))
    if models_info['tflite_available']:
        # Test specific behavior
        pass
```

### All Fixtures

```python
def test_full_setup(ml_base_dir, test_data_dir, exports_dir,
                   sample_classification_image, sample_detection_image,
                   tflite_model_path, onnx_model_path, models_info):
    """Access all fixtures."""
    # Full test setup
    pass
```

See [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md) for complete fixture documentation.

## Troubleshooting

### Tests Not Found

**Error**: `No tests ran`

**Solution**:

```bash
# Verify test discovery
pytest ml/tests/ --collect-only

# Check conftest.py is in ml/tests/
ls ml/tests/conftest.py
```

### Import Errors

**Error**: `ModuleNotFoundError: No module named 'app'`

**Solution**:

```bash
# Set Python path
set PYTHONPATH=d:\Haski-main\backend;%PYTHONPATH%

# Or run from project root
cd d:\Haski-main
pytest ml/tests/ -v
```

### Models Not Found

**Expected Behavior**: Tests should pass using mock mode

**If Tests Fail**: Check models exist:

```bash
ls ml/exports/
# Should see: skin_classifier.tflite and/or skin_classifier.onnx
```

### Permission Denied

**Error**: Cannot create test images

**Solution**:

```bash
# Create directory
mkdir ml/data/test

# Or Windows:
New-Item -ItemType Directory -Force -Path ml/data/test
```

### Timeout

**Error**: `Timeout`

**Solution**:

```bash
# Increase timeout
pytest ml/tests/ --timeout=300
```

## Documentation

| File                                                     | Purpose             | Length     |
| -------------------------------------------------------- | ------------------- | ---------- |
| [ML_TESTS_GUIDE.md](ML_TESTS_GUIDE.md)                   | Complete test guide | 400+ lines |
| [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md) | Fixture reference   | 400+ lines |
| [TEST_QUICK_REFERENCE.md](TEST_QUICK_REFERENCE.md)       | Quick lookup        | 200+ lines |
| [README.md](README.md)                                   | This file           | 200+ lines |

## Integration

### CI/CD

```yaml
# GitHub Actions
- run: pytest ml/tests/test_inference_smoke.py -v --tb=short
```

### Pre-commit

```bash
pytest ml/tests/ --co -q
```

## Statistics

| Metric               | Value |
| -------------------- | ----- |
| Test Classes         | 7     |
| Test Functions       | 22    |
| Fixtures             | 8     |
| Documentation Files  | 4     |
| Total Lines of Code  | 1000+ |
| Code Coverage Target | 85%+  |

## Related Systems

- **Representative Data**: [../exports/REPRESENTATIVE_DATA_GUIDE.md](../exports/REPRESENTATIVE_DATA_GUIDE.md)
- **Model Monitoring**: [../monitoring/MODEL_MONITORING_GUIDE.md](../monitoring/MODEL_MONITORING_GUIDE.md)
- **Inference API**: [../../backend/app/services/ml_infer.py](../../backend/app/services/ml_infer.py)

## Next Steps

1. ✅ Run all tests: `pytest ml/tests/ -v`
2. ✅ Check coverage: `pytest ml/tests/ --cov=app.services.ml_infer`
3. ✅ Add to CI/CD pipeline
4. ✅ Extend with model-specific tests as needed

## Support

For detailed information:

1. See [ML_TESTS_GUIDE.md](ML_TESTS_GUIDE.md) for comprehensive guide
2. See [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md) for fixture details
3. See [TEST_QUICK_REFERENCE.md](TEST_QUICK_REFERENCE.md) for quick lookup
4. Check `conftest.py` for configuration

---

**Created**: Smoke test suite for ML inference pipeline  
**Status**: ✅ Ready for testing  
**Coverage**: Classification, Detection, Preprocessing, Integration, Error Handling  
**Python**: 3.8+  
**Framework**: pytest
