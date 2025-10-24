"""
ML Inference Service - Quick Reference Card

Copy this to your project documentation or README.
"""

# ============================================================================
# QUICK SETUP (5 minutes)
# ============================================================================

"""
1. Install dependencies:
   pip install tflite-runtime pillow numpy

2. Export models (if not already done):
   python ml/exports/export_models.py --checkpoint /path/to/pytorch/model.pt
   
3. Test integration:
   cd backend/app/services
   python test_ml_infer.py

4. Add to your FastAPI app (main.py):
   from api.v1 import analyze
   app.include_router(analyze.router)

Done! API is ready at:
   POST /api/v1/analyze/image     - Upload image for analysis
   GET  /api/v1/analyze/health    - Service health check
"""

# ============================================================================
# MINIMAL USAGE EXAMPLE
# ============================================================================

from services.ml_infer import analyze_image

# From file path
result = analyze_image("image.jpg")
print(f"Skin: {result['skin_type']}, Hair: {result['hair_type']}")

# From bytes
with open("image.jpg", "rb") as f:
    result = analyze_image(f.read())

# Response structure
"""
{
    "skin_type": "combination",           # One of 5 types
    "hair_type": "wavy",                  # One of 4 types
    "conditions_detected": ["mild_acne"], # List of detected conditions
    "confidence_scores": {
        "skin_type": 0.84,
        "hair_type": 0.76,
        "condition": 0.67
    },
    "model_version": "v1-exported",       # API version
    "model_type": "tflite"                # Model used: tflite|onnx|mock
}
"""

# ============================================================================
# CLASS MAPPINGS
# ============================================================================

SKIN_TYPES = [
    "normal", "dry", "oily", "combination", "sensitive"
]

HAIR_TYPES = [
    "straight", "wavy", "curly", "coily"
]

CONDITIONS = [
    "healthy", "mild_acne", "severe_acne", "eczema", "psoriasis"
]

# ============================================================================
# FASTAPI INTEGRATION (Copy & Customize)
# ============================================================================

from fastapi import APIRouter, File, UploadFile
from services.ml_infer import analyze_image

router = APIRouter(prefix="/api/v1/analyze", tags=["Analysis"])

@router.post("/image")
async def analyze_uploaded_image(file: UploadFile = File(...)):
    """Upload image for analysis."""
    image_bytes = await file.read()
    return analyze_image(image_bytes)

# Use in main app:
# app.include_router(router)

# ============================================================================
# TEST WITHOUT MODELS (Development)
# ============================================================================

"""
If models are not exported yet, the service automatically uses mock responses:
- Allows testing frontend/API without training models
- Returns consistent test data
- No dependencies needed beyond PIL/numpy

Just start using analyze_image() - it will work!
"""

# ============================================================================
# PERFORMANCE TIPS
# ============================================================================

"""
1. TFLite is 2-4x faster than ONNX
   - Automatically used if both available
   - Int8 quantized is fastest (~5ms)

2. Batch processing:
   results = [analyze_image(img) for img in images]

3. Caching:
   - Results are deterministic for same input
   - Consider caching analysis results

4. Preprocessing is built-in:
   - Automatic image resizing to 224×224
   - ImageNet normalization applied
   - Quantization handled automatically
"""

# ============================================================================
# TROUBLESHOOTING
# ============================================================================

"""
Problem: "No models available" warning
Solution: python ml/exports/export_models.py

Problem: ImportError: No module named 'tflite_runtime'
Solution: pip install tflite-runtime

Problem: Inference is slow (>100ms)
Solution: Check model_type in response - should be "tflite" not "onnx"

Problem: Image not found error
Solution: Verify file path is absolute or relative to working directory

Problem: FileNotFoundError when accessing image
Solution: Check file permissions and path encoding (use Path() for paths)
"""

# ============================================================================
# API CONTRACTS
# ============================================================================

"""
Input:
  - File path (str): "/absolute/or/relative/path/to/image.jpg"
  - Image bytes (bytes): Raw image data (JPEG, PNG, BMP, etc.)
  - Image size: Any size (automatically resized to 224×224)

Output:
  - Dictionary with JSON-serializable values
  - All float values for confidence_scores
  - All strings for categorical predictions
  - No None values - always complete response

Errors:
  - FileNotFoundError: Image file does not exist
  - Other exceptions: Use mock response (with warning)

Model Priority:
  1. TFLite (fastest, ~10-20ms) ← Default
  2. ONNX (cross-platform, ~20-40ms)
  3. Mock (testing, <1ms)
"""

# ============================================================================
# FILES REFERENCE
# ============================================================================

"""
backend/
  app/
    services/
      ml_infer.py                     ← Main API (use this)
      test_ml_infer.py                ← Test suite (6 tests)
      ML_INFERENCE_README.md          ← Full documentation
    api/v1/
      analyze_example.py              ← Copy to analyze.py
      
ml/exports/
  export_models.py                    ← Model export
  skin_classifier.onnx                ← ONNX model (if exported)
  skin_classifier.tflite              ← TFLite model (if exported)
  
INTEGRATION_SUMMARY.md                ← Full integration guide
"""

# ============================================================================
# VERSION INFO
# ============================================================================

"""
API Version: v1-exported
Service Version: 1.0
Model Format: ONNX (fallback) + TFLite (primary)
Model Architecture: EfficientNet-B0 backbone
Input Size: 224×224 RGB
Output Classes: 14 (5 skin + 4 hair + 5 conditions)
Inference Latency: 10-40ms (depending on model/hardware)
Model Size: 5-30 MB (depending on quantization/format)
"""

# ============================================================================
# DEPLOYMENT CHECKLIST
# ============================================================================

"""
□ Export models: python ml/exports/export_models.py
□ Verify files exist:
  - ml/exports/skin_classifier.tflite
  - ml/exports/skin_classifier.onnx (optional)
□ Install dependencies: pip install tflite-runtime pillow numpy
□ Run tests: python backend/app/services/test_ml_infer.py
□ Copy analyze_example.py to analyze.py
□ Update main FastAPI app to include router
□ Test endpoint: POST /api/v1/analyze/image
□ Check health: GET /api/v1/analyze/health
□ Enable logging if needed
□ Deploy!
"""

# ============================================================================
# SUPPORT & TROUBLESHOOTING
# ============================================================================

"""
See full documentation:
  - backend/app/services/ML_INFERENCE_README.md
  - INTEGRATION_SUMMARY.md

Test the service:
  python backend/app/services/test_ml_infer.py

Enable debug logging:
  import logging
  logging.basicConfig(level=logging.DEBUG)
  
Check model availability:
  from pathlib import Path
  base = Path(".")
  print(f"ONNX: {(base/'ml/exports/skin_classifier.onnx').exists()}")
  print(f"TFLite: {(base/'ml/exports/skin_classifier.tflite').exists()}")
"""
