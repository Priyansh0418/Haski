# 🚀 Quick Start - ML Smoke Tests

Get running in 5 minutes.

## Installation (1 minute)

```bash
# Navigate to project
cd d:\Haski-main

# Install pytest
pip install pytest
```

## Run Tests (1 minute)

```bash
# Run all 22 tests
pytest ml/tests/ -v
```

## Expected Output (within 30 seconds)

```
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_skin_type_valid PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_hair_type_valid PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_conditions_is_list PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_confidence_scores_structure PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_model_type_valid PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_with_file_path PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_with_bytes PASSED
ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_reproducible PASSED
ml/tests/test_inference_smoke.py::TestDetectionSmoke::test_detection_returns_list PASSED
ml/tests/test_inference_smoke.py::TestDetectionSmoke::test_detection_schema PASSED
ml/tests/test_inference_smoke.py::TestPreprocessing::test_preprocess_image_output_shape PASSED
ml/tests/test_inference_smoke.py::TestPreprocessing::test_preprocess_image_output_type PASSED
ml/tests/test_inference_smoke.py::TestPreprocessing::test_preprocess_image_value_range PASSED
ml/tests/test_inference_smoke.py::TestIntegration::test_full_pipeline_classification PASSED
ml/tests/test_inference_smoke.py::TestIntegration::test_pipeline_handles_both_formats PASSED
ml/tests/test_inference_smoke.py::TestModelAvailability::test_models_can_be_imported PASSED
ml/tests/test_inference_smoke.py::TestModelAvailability::test_inference_fallback_to_mock PASSED
ml/tests/test_inference_smoke.py::TestModelAvailability::test_model_type_reported PASSED
ml/tests/test_inference_smoke.py::TestErrorHandling::test_invalid_image_path_raises_error PASSED
ml/tests/test_inference_smoke.py::TestErrorHandling::test_corrupted_image_handling PASSED
ml/tests/test_inference_smoke.py::TestPerformance::test_inference_completes_in_reasonable_time PASSED

========================= 22 passed in ~5s =========================
```

## What Just Happened? ✅

- ✅ All 22 tests passed
- ✅ Classification inference verified
- ✅ Detection inference verified
- ✅ Image preprocessing validated
- ✅ Error handling confirmed
- ✅ Model fallback working
- ✅ Full pipeline tested

## That's It! 🎉

Your ML inference smoke tests are now running!

---

## Common Commands

### Run Only Classification Tests

```bash
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke -v
```

### Run with Coverage

```bash
pytest ml/tests/ --cov=app.services.ml_infer --cov-report=html
```

### Run with Verbose Output

```bash
pytest ml/tests/ -vv
```

### Debug a Specific Test

```bash
pytest ml/tests/test_inference_smoke.py::TestClassificationSmoke::test_analyze_image_returns_required_keys -vv -s
```

---

## Documentation

| Doc                                                      | Purpose      | When to Read        |
| -------------------------------------------------------- | ------------ | ------------------- |
| [README.md](README.md)                                   | Overview     | First time setup    |
| [TEST_QUICK_REFERENCE.md](TEST_QUICK_REFERENCE.md)       | Commands     | Need a command      |
| [ML_TESTS_GUIDE.md](ML_TESTS_GUIDE.md)                   | Deep dive    | Understanding tests |
| [TEST_FIXTURES_REFERENCE.md](TEST_FIXTURES_REFERENCE.md) | Fixtures     | Writing tests       |
| [TESTS_INDEX.md](TESTS_INDEX.md)                         | Master index | Finding something   |

---

## What's Tested?

✅ **Classification** - Skin type & hair type detection (9 tests)
✅ **Detection** - Condition detection (2 tests)
✅ **Preprocessing** - Image normalization (3 tests)
✅ **Integration** - Full pipeline (2 tests)
✅ **Models** - Loading & fallback (3 tests)
✅ **Errors** - Error handling (2 tests)
✅ **Performance** - Speed (1 test)

**Total: 22 Tests ✅**

---

## Need Help?

| Issue              | Solution                                |
| ------------------ | --------------------------------------- |
| "Module not found" | `set PYTHONPATH=backend;%PYTHONPATH%`   |
| Tests not found    | Make sure you're in `d:\Haski-main`     |
| Tests timeout      | Increase: `pytest --timeout=300`        |
| Tests fail         | Run: `pytest ml/tests/ -vv` for details |

---

## Next Steps

1. ✅ Tests running? Great!
2. 📚 Learn more: Read [ML_TESTS_GUIDE.md](ML_TESTS_GUIDE.md)
3. 🧪 Write new tests: See [ML_TESTS_GUIDE.md#extending-tests](ML_TESTS_GUIDE.md#extending-tests)
4. 🔄 Add to CI/CD: Use command: `pytest ml/tests/test_inference_smoke.py -v --tb=short`

---

**Done!** Your ML inference tests are ready. 🚀
