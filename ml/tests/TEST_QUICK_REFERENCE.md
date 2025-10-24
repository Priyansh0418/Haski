# ML Tests Quick Reference

Fast lookup for running and writing tests.

## Run Tests

```bash
# All smoke tests
pytest ml/tests/test_inference_smoke.py -v

# Specific test class
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke -v

# Specific test
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys -v

# Only smoke tests marker
pytest ml/tests/ -m smoke -v

# With coverage
pytest ml/tests/ --cov=app.services.ml_infer --cov-report=html
```

## Test Output Schema

```python
# analyze_image() returns:
{
    'skin_type': 'normal',           # or: dry, oily, combination, sensitive
    'hair_type': 'wavy',             # or: straight, curly, coily
    'conditions_detected': ['acne'],  # list of conditions
    'confidence_scores': {
        'skin_type': 0.95,            # 0.0-1.0
        'hair_type': 0.87,            # 0.0-1.0
        'condition': 0.92              # 0.0-1.0
    },
    'model_version': '1.0.0',         # Version string
    'model_type': 'tflite'            # or: onnx, mock
}
```

## Fixture Quick Reference

```python
def test_example(sample_classification_image):
    """Most common: test classification."""
    result = analyze_image(str(sample_classification_image))
    assert result['skin_type'] is not None

def test_with_bytes(sample_classification_image):
    """Test with bytes input."""
    with open(sample_classification_image, 'rb') as f:
        result = analyze_image(f.read())
    assert result is not None

def test_detection(sample_detection_image):
    """Test with detection image."""
    result = analyze_image(str(sample_detection_image))
    assert result['model_type'] in ['tflite', 'onnx', 'mock']

def test_with_models_info(sample_classification_image, models_info):
    """Check which models available."""
    result = analyze_image(str(sample_classification_image))
    if models_info['tflite_available']:
        # Assert something about TFLite
        pass
```

## Valid Values

```python
# Skin types
['normal', 'dry', 'oily', 'combination', 'sensitive']

# Hair types
['straight', 'wavy', 'curly', 'coily']

# Model types
['tflite', 'onnx', 'mock']

# Common conditions
['healthy', 'mild_acne', 'severe_acne', 'eczema', 'psoriasis']
```

## Test Classes

| Class                   | Tests | Purpose                       |
| ----------------------- | ----- | ----------------------------- |
| TestClassificationSmoke | 9     | Verify classification results |
| TestDetectionSmoke      | 2     | Verify detection output       |
| TestPreprocessing       | 3     | Validate image preprocessing  |
| TestIntegration         | 2     | Full pipeline tests           |
| TestModelAvailability   | 3     | Model loading & fallback      |
| TestErrorHandling       | 2     | Error scenarios               |
| TestPerformance         | 1     | Performance smoke test        |

**Total**: 22 tests

## Key Assertions

```python
# Verify required keys
assert 'skin_type' in result
assert 'hair_type' in result
assert 'confidence_scores' in result

# Validate enum values
assert result['skin_type'] in ['normal', 'dry', 'oily', 'combination', 'sensitive']
assert result['hair_type'] in ['straight', 'wavy', 'curly', 'coily']

# Check confidence structure
assert isinstance(result['confidence_scores'], dict)
assert 0 <= result['confidence_scores']['skin_type'] <= 1

# Verify model type
assert result['model_type'] in ['tflite', 'onnx', 'mock']
```

## Common Patterns

### Test Classification

```python
def test_skin_hair_detection(sample_classification_image):
    result = analyze_image(str(sample_classification_image))

    # Test classifies into one category each
    assert result['skin_type'] in ['normal', 'dry', 'oily', 'combination', 'sensitive']
    assert result['hair_type'] in ['straight', 'wavy', 'curly', 'coily']
```

### Test Error Handling

```python
def test_missing_file():
    with pytest.raises(FileNotFoundError):
        analyze_image("/invalid/path.jpg")
```

### Test Both Input Formats

```python
def test_input_formats(sample_classification_image):
    # File path
    r1 = analyze_image(str(sample_classification_image))

    # Bytes
    with open(sample_classification_image, 'rb') as f:
        r2 = analyze_image(f.read())

    assert r1 == r2
```

## Fixtures Available

| Name                          | Returns                 | Usage                |
| ----------------------------- | ----------------------- | -------------------- |
| `ml_base_dir`                 | Path to ml/             | Getting ML directory |
| `test_data_dir`               | Path to ml/data/test/   | Creating test files  |
| `exports_dir`                 | Path to ml/exports/     | Finding models       |
| `sample_classification_image` | Path to test image      | Classification tests |
| `sample_detection_image`      | Path to detection image | Detection tests      |
| `tflite_model_path`           | str path to TFLite      | Model references     |
| `onnx_model_path`             | str path to ONNX        | Model references     |
| `models_info`                 | dict with availability  | Conditional tests    |

## Debugging

```bash
# Verbose output
pytest ml/tests/test_inference_smoke.py -vv

# Show print statements
pytest ml/tests/test_inference_smoke.py -s

# Stop on first failure
pytest ml/tests/test_inference_smoke.py -x

# Show local variables on failure
pytest ml/tests/test_inference_smoke.py -l

# Show summary
pytest ml/tests/test_inference_smoke.py -v --tb=short
```

## File Locations

- **Tests**: `ml/tests/test_inference_smoke.py`
- **Configuration**: `ml/tests/conftest.py`
- **Guides**: `ml/tests/ML_TESTS_GUIDE.md`
- **Fixtures**: `ml/tests/TEST_FIXTURES_REFERENCE.md`
- **Inference**: `backend/app/services/ml_infer.py`
- **Test Data**: `ml/data/test/` (auto-created)
- **Models**: `ml/exports/` (optional)

## Import Statements (in test files)

```python
import pytest
import json
import tempfile
from pathlib import Path
from typing import Dict, List, Any
import numpy as np
from PIL import Image

from app.services.ml_infer import analyze_image, preprocess_image
from app.services.ml_infer import TFLiteInference, ONNXInference
```

## CI/CD Command

```bash
pytest ml/tests/test_inference_smoke.py -v --tb=short
```

## Expected Test Output

```
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_skin_type_valid PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_hair_type_valid PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_conditions_is_list PASSED
...
========================= 22 passed in 5.23s =========================
```

## Troubleshooting Quick Fixes

| Issue             | Fix                                   |
| ----------------- | ------------------------------------- |
| Import error      | `set PYTHONPATH=backend;%PYTHONPATH%` |
| Module not found  | Run from `d:\Haski-main` root         |
| Missing fixtures  | Check `conftest.py` is in `ml/tests/` |
| Timeout           | Increase pytest timeout               |
| Permission denied | Ensure ml/data/test/ is writable      |

## One-Liners

```bash
# Run all tests
pytest ml/tests/ -v

# Run and stop on first failure
pytest ml/tests/ -x

# Run with coverage
pytest ml/tests/ --cov=app.services.ml_infer

# Run specific test
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys

# Run only smoke marker
pytest ml/tests/ -m smoke
```

## Related Files

- [ML_TESTS_GUIDE.md](ML_TESTS_GUIDE.md) - Full test documentation
- [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md) - Detailed fixture guide
- [../exports/REPRESENTATIVE_DATA_GUIDE.md](../exports/REPRESENTATIVE_DATA_GUIDE.md) - Data generation
- [../monitoring/MODEL_MONITORING_GUIDE.md](../monitoring/MODEL_MONITORING_GUIDE.md) - Monitoring system
