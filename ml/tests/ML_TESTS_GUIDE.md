# ML Inference Smoke Tests

## Overview

Comprehensive pytest-based smoke tests for the ML inference pipeline, covering:

- **Classification inference**: Skin type and hair type detection
- **Detection inference**: Condition and defect detection
- **Image preprocessing**: Validation of image preparation
- **Model availability**: Fallback to mock when real models unavailable
- **Error handling**: Graceful handling of invalid inputs
- **Integration pipeline**: End-to-end functionality

## Test Structure

```
ml/tests/
├── __init__.py                      # Package marker
├── conftest.py                      # Pytest configuration & shared fixtures
├── test_inference_smoke.py          # Main test suite (700+ lines)
├── ML_TESTS_GUIDE.md               # This file
└── TEST_FIXTURES_REFERENCE.md       # Detailed fixture documentation
```

## Quick Start

### Installation

```bash
# Navigate to project root
cd d:\Haski-main

# Install pytest if not already installed
pip install pytest

# Or install from requirements
pip install -r backend/requirements.txt
pip install -r ml/requirements.txt
```

### Running Tests

```bash
# Run all tests
pytest ml/tests/test_inference_smoke.py -v

# Run specific test class
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke -v

# Run specific test
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys -v

# Run only smoke tests
pytest ml/tests/test_inference_smoke.py -m smoke -v

# Run with coverage
pytest ml/tests/test_inference_smoke.py --cov=app.services.ml_infer --cov-report=html

# Run with verbose output
pytest ml/tests/test_inference_smoke.py -vv --tb=short

# Run with output capture disabled (see print statements)
pytest ml/tests/test_inference_smoke.py -s -v
```

## Test Classes

### TestClassificationSmoke (9 tests)

**Purpose**: Verify classification inference functionality

**Tests**:

1. `test_analyze_image_returns_required_keys` - Verifies all required keys present
2. `test_analyze_image_skin_type_valid` - Validates skin_type enum
3. `test_analyze_image_hair_type_valid` - Validates hair_type enum
4. `test_analyze_image_conditions_is_list` - Verifies conditions_detected structure
5. `test_analyze_image_confidence_scores_structure` - Validates confidence dict
6. `test_analyze_image_model_type_valid` - Validates model_type enum
7. `test_analyze_image_with_file_path` - Tests file path input
8. `test_analyze_image_with_bytes` - Tests bytes input
9. `test_analyze_image_reproducible` - Verifies deterministic output

**Expected Return Schema**:

```python
{
    'skin_type': str,                    # normal, dry, oily, combination, sensitive
    'hair_type': str,                    # straight, wavy, curly, coily
    'conditions_detected': list[str],    # [condition1, condition2, ...]
    'confidence_scores': {
        'skin_type': float,              # 0.0-1.0
        'hair_type': float,              # 0.0-1.0
        'condition': float                # 0.0-1.0
    },
    'model_version': str,                # e.g., "1.0.0"
    'model_type': str                    # tflite, onnx, or mock
}
```

### TestDetectionSmoke (2 tests)

**Purpose**: Verify detection inference functionality

**Tests**:

1. `test_detection_returns_list` - Verifies detection output format
2. `test_detection_schema` - Validates detection output schema

**Status**: Currently uses analyze_image as proxy; can be extended with dedicated detection model

### TestPreprocessing (3 tests)

**Purpose**: Validate image preprocessing

**Tests**:

1. `test_preprocess_image_output_shape` - Verifies shape is (1, 3, 224, 224)
2. `test_preprocess_image_output_type` - Verifies float32 numpy array
3. `test_preprocess_image_value_range` - Validates normalized value ranges

### TestIntegration (2 tests)

**Purpose**: Verify end-to-end pipeline

**Tests**:

1. `test_full_pipeline_classification` - Complete preprocessing → analysis pipeline
2. `test_pipeline_handles_both_formats` - Tests bytes and file path inputs

### TestModelAvailability (3 tests)

**Purpose**: Verify model loading and fallback

**Tests**:

1. `test_models_can_be_imported` - Verifies inference classes importable
2. `test_inference_fallback_to_mock` - Verifies graceful fallback
3. `test_model_type_reported` - Verifies model type correctly reported

### TestErrorHandling (2 tests)

**Purpose**: Verify error handling

**Tests**:

1. `test_invalid_image_path_raises_error` - Verifies FileNotFoundError on bad path
2. `test_corrupted_image_handling` - Verifies graceful handling of corrupted images

### TestPerformance (1 test)

**Purpose**: Smoke test for performance

**Tests**:

1. `test_inference_completes_in_reasonable_time` - Verifies <10s completion

## Fixtures

### Session-Scoped Fixtures

These are created once per test session:

#### `ml_base_dir`

**Returns**: Path to `ml/` directory
**Usage**:

```python
def test_something(ml_base_dir):
    assert (ml_base_dir / "exports").exists()
```

#### `exports_dir`

**Returns**: Path to `ml/exports/` directory
**Creates**: Directory if missing
**Usage**:

```python
def test_models(exports_dir):
    model = exports_dir / "skin_classifier.tflite"
```

#### `test_data_dir`

**Returns**: Path to `ml/data/test/` directory
**Creates**: Directory if missing
**Usage**:

```python
def test_data(test_data_dir):
    assert test_data_dir.exists()
```

### Function-Scoped Fixtures

These are created fresh for each test:

#### `sample_classification_image`

**Returns**: Path to test classification image
**Creates**: Synthetic image if not present (224×224 RGB random)
**Location**: `ml/data/test/sample_classification.jpg`
**Usage**:

```python
def test_classification(sample_classification_image):
    result = analyze_image(str(sample_classification_image))
    assert result['skin_type'] is not None
```

#### `sample_detection_image`

**Returns**: Path to test detection image
**Creates**: Synthetic image with gradients if not present (224×224 RGB)
**Location**: `ml/data/test/sample_detection.jpg`
**Usage**:

```python
def test_detection(sample_detection_image):
    result = analyze_image(str(sample_detection_image))
    assert result is not None
```

#### `tflite_model_path`

**Returns**: Path to TFLite model
**Location**: `ml/exports/skin_classifier.tflite`
**Note**: Returns path even if file doesn't exist (inference handles gracefully)

#### `onnx_model_path`

**Returns**: Path to ONNX model
**Location**: `ml/exports/skin_classifier.onnx`
**Note**: Returns path even if file doesn't exist (inference handles gracefully)

#### `models_info`

**Returns**: Dict with availability flags
**Structure**:

```python
{
    'tflite_available': bool,
    'onnx_available': bool
}
```

**Usage**:

```python
def test_model_selection(models_info):
    if models_info['tflite_available']:
        # Test TFLite code
```

## Valid Values Reference

### skin_type (5 valid values)

```python
valid_skin_types = ["normal", "dry", "oily", "combination", "sensitive"]
```

### hair_type (4 valid values)

```python
valid_hair_types = ["straight", "wavy", "curly", "coily"]
```

### conditions_detected (examples)

```python
# Common conditions:
conditions = [
    "healthy",
    "mild_acne",
    "severe_acne",
    "eczema",
    "psoriasis",
    "rosacea",
    "dermatitis"
]
```

### model_type (3 valid values)

```python
valid_model_types = ["tflite", "onnx", "mock"]
```

- `tflite`: TensorFlow Lite quantized model
- `onnx`: ONNX runtime model
- `mock`: Synthetic inference (fallback)

## Configuration (conftest.py)

### Features

1. **Path Setup**: Automatically adds backend to Python path
2. **Marker Assignment**: Automatically tags tests with appropriate markers
3. **Pytest Configuration**: Configures custom markers

### Custom Markers

```bash
# Run only smoke tests
pytest ml/tests/test_inference_smoke.py -m smoke

# Run only unit tests
pytest ml/tests/test_inference_smoke.py -m unit

# Run only integration tests
pytest ml/tests/test_inference_smoke.py -m integration

# Run everything except smoke tests
pytest ml/tests/test_inference_smoke.py -m "not smoke"
```

## Mock Model Fallback

When real models aren't available, the inference system automatically falls back to mock mode:

1. **Detection**: Returns mock predictions with realistic structure
2. **Model Type**: Reports as "mock" in results
3. **Predictions**: Deterministic, reproducible output
4. **Confidence**: Always 0.5 (neutral confidence)

**Example**:

```python
# Even if models missing, this succeeds:
result = analyze_image("test.jpg")
assert result['model_type'] == 'mock'  # Falls back gracefully
assert result['skin_type'] in ["normal", "dry", "oily", "combination", "sensitive"]
```

## Image Handling

### Input Formats Supported

1. **File Path** (str or Path):

```python
result = analyze_image("/path/to/image.jpg")
result = analyze_image(Path("/path/to/image.jpg"))
```

2. **Bytes**:

```python
with open("image.jpg", "rb") as f:
    image_bytes = f.read()
result = analyze_image(image_bytes)
```

### Image Requirements

- **Format**: JPG, PNG, or other PIL-compatible formats
- **Size**: Any size (will be resized to 224×224 internally)
- **Color Space**: RGB expected (or will be converted)
- **Min Resolution**: 32×32 recommended

### Synthetic Test Images

Tests automatically create synthetic images if real ones not present:

```python
# Classification image (random 224×224 RGB)
sample_classification_image  # Auto-created if missing

# Detection image (gradient pattern 224×224 RGB)
sample_detection_image  # Auto-created if missing
```

## Error Scenarios

### Handled Gracefully

✅ **Missing image file**: Raises `FileNotFoundError`
✅ **Corrupted image file**: Returns mock result (or raises)
✅ **Missing models**: Falls back to mock inference
✅ **Invalid input format**: Raises `TypeError`
✅ **Out-of-memory**: Handled by inference system

### Not Caught (Expected Behavior)

❌ **Invalid skin_type returned**: Test fails (indicates bug)
❌ **Missing required keys**: Test fails (indicates incomplete inference)
❌ **Non-numeric confidence**: Test fails (indicates schema violation)

## Performance Expectations

| Model              | CPU Time  | GPU Time  |
| ------------------ | --------- | --------- |
| TFLite (quantized) | 100-500ms | 50-200ms  |
| ONNX               | 200-800ms | 100-300ms |
| Mock               | <10ms     | <10ms     |

**Test Threshold**: 10 seconds (accommodates worst-case CPU inference)

## CI/CD Integration

### GitHub Actions Example

```yaml
name: ML Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - uses: actions/setup-python@v2
        with:
          python-version: "3.10"
      - run: pip install -r ml/requirements.txt
      - run: pip install pytest
      - run: pytest ml/tests/test_inference_smoke.py -v
```

## Troubleshooting

### Tests Fail with "Module not found"

**Problem**: `ModuleNotFoundError: No module named 'app'`

**Solution**:

```bash
# Ensure backend path is in PYTHONPATH
set PYTHONPATH=d:\Haski-main\backend;%PYTHONPATH%

# Or run pytest from project root
cd d:\Haski-main
pytest ml/tests/test_inference_smoke.py
```

### Import Issues

**Problem**: Cannot import ml_infer

**Solution**: Check backend/app/services/ml_infer.py exists:

```bash
ls backend/app/services/ml_infer.py
```

### Model Files Missing

**Problem**: TFLite/ONNX models not found

**Expected Behavior**: Tests should pass using mock mode

**If Tests Fail**: Check ml/exports/ directory:

```bash
ls ml/exports/
```

Should contain:

- `skin_classifier.tflite` (optional, inference handles missing)
- `skin_classifier.onnx` (optional, inference handles missing)

### Synthetic Image Creation Fails

**Problem**: Permission denied creating test images

**Solution**: Ensure ml/data/test/ is writable:

```bash
# Create directory manually
mkdir ml/data/test

# On Windows:
New-Item -ItemType Directory -Force -Path ml/data/test
```

## Extending Tests

### Adding a New Test

```python
class TestNewFeature:
    """Tests for new feature."""

    def test_new_functionality(self, sample_classification_image):
        """Test description."""
        # Arrange
        test_image = sample_classification_image

        # Act
        result = analyze_image(str(test_image))

        # Assert
        assert result['skin_type'] is not None
```

### Adding a New Fixture

```python
@pytest.fixture
def new_test_data():
    """Create new test data."""
    # Setup
    data = create_test_data()

    yield data

    # Teardown (optional)
    cleanup_test_data(data)
```

## Test Statistics

| Metric          | Value |
| --------------- | ----- |
| Total Tests     | 22    |
| Test Classes    | 7     |
| Fixtures        | 6     |
| Lines of Code   | 700+  |
| Coverage Target | 85%+  |

**Breakdown**:

- Classification Tests: 9
- Detection Tests: 2
- Preprocessing Tests: 3
- Integration Tests: 2
- Model Availability Tests: 3
- Error Handling Tests: 2
- Performance Tests: 1

## Related Documentation

- [ML_TESTS_GUIDE.md](ML_TESTS_GUIDE.md) - This file
- [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md) - Detailed fixture docs
- [../monitoring/MODEL_MONITORING_GUIDE.md](../monitoring/MODEL_MONITORING_GUIDE.md) - Monitoring system
- [../exports/REPRESENTATIVE_DATA_GUIDE.md](../exports/REPRESENTATIVE_DATA_GUIDE.md) - Data generation
- [../../backend/app/services/ml_infer.py](../../backend/app/services/ml_infer.py) - Inference implementation

## Support

For issues or questions:

1. Check [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md)
2. Review conftest.py for fixture configuration
3. Run with `-vv` flag for verbose output
4. Use `-s` flag to capture print statements
5. Check test output for specific assertion failures
