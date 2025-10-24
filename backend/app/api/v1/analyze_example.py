"""
FastAPI integration example for ML inference service.

Shows how to integrate analyze_image() into backend API endpoints.
Add this to your main FastAPI app or api/v1 router.
"""

from fastapi import APIRouter, File, UploadFile, HTTPException, status
from fastapi.responses import JSONResponse
import logging
from typing import Optional

from services.ml_infer import analyze_image, analyze_image_local

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(
    prefix="/api/v1/analyze",
    tags=["Analysis"]
)


# ============================================================================
# Image Upload Endpoint
# ============================================================================

@router.post("/image", response_model=dict)
async def analyze_uploaded_image(file: UploadFile = File(...)):
    """
    Analyze uploaded image.
    
    Accepts JPEG, PNG, BMP, etc.
    Returns skin type, hair type, and detected conditions.
    
    Args:
        file: Image file upload
    
    Returns:
        {
            "skin_type": str,
            "hair_type": str,
            "conditions_detected": list,
            "confidence_scores": dict,
            "model_version": str,
            "model_type": str
        }
    
    Raises:
        400: Invalid image format
        500: Inference failed
    """
    try:
        # Validate file type
        if file.content_type not in ['image/jpeg', 'image/png', 'image/bmp']:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid image format: {file.content_type}. "
                       "Supported: JPEG, PNG, BMP"
            )
        
        # Read image bytes
        image_bytes = await file.read()
        
        if len(image_bytes) == 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Empty image file"
            )
        
        logger.info(f"Analyzing uploaded image: {file.filename} ({len(image_bytes)} bytes)")
        
        # Run inference
        result = analyze_image(image_bytes)
        
        logger.info(
            f"Analysis complete: skin={result['skin_type']}, "
            f"hair={result['hair_type']}, model={result['model_type']}"
        )
        
        return result
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Image analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Image analysis failed: {str(e)}"
        )


# ============================================================================
# File Path Endpoint (Dev/Testing Only)
# ============================================================================

@router.post("/file", response_model=dict)
async def analyze_local_image(file_path: str):
    """
    Analyze image from local file path (development only).
    
    WARNING: This endpoint is for testing/development only.
    Do not expose in production - use /image endpoint instead.
    
    Args:
        file_path: Absolute path to image file
    
    Returns:
        Analysis results (see /image endpoint)
    
    Raises:
        404: File not found
        500: Inference failed
    """
    try:
        logger.info(f"Analyzing local file: {file_path}")
        
        result = analyze_image_local(file_path)
        
        return result
    
    except FileNotFoundError as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image file not found: {file_path}"
        )
    except Exception as e:
        logger.error(f"Local image analysis failed: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Analysis failed: {str(e)}"
        )


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def inference_health() -> dict:
    """
    Check ML inference service health.
    
    Returns:
        {
            "status": "healthy" | "degraded",
            "models_available": bool,
            "message": str
        }
    """
    from pathlib import Path
    
    base_dir = Path(__file__).parent.parent.parent.parent
    onnx_path = base_dir / "ml" / "exports" / "skin_classifier.onnx"
    tflite_path = base_dir / "ml" / "exports" / "skin_classifier.tflite"
    
    models_available = onnx_path.exists() or tflite_path.exists()
    
    return {
        "status": "healthy" if models_available else "degraded",
        "models_available": models_available,
        "message": (
            "All models available" if models_available
            else "Using mock responses (no models found)"
        ),
        "tflite_available": tflite_path.exists(),
        "onnx_available": onnx_path.exists(),
    }


# ============================================================================
# Usage in Main App
# ============================================================================

"""
Add to your FastAPI main app (main.py):

    from api.v1.analyze import router as analyze_router
    
    app = FastAPI()
    app.include_router(analyze_router)
    
    # OR if you already have an api router:
    api_router = APIRouter(prefix="/api")
    api_router.include_router(analyze_router)
    app.include_router(api_router)

Now available endpoints:

    POST /api/v1/analyze/image              - Upload image for analysis
    POST /api/v1/analyze/file?file_path=... - Analyze local file (dev)
    GET  /api/v1/analyze/health             - Health check

Example curl requests:

    # Upload image
    curl -X POST http://localhost:8000/api/v1/analyze/image \\
      -H "Content-Type: multipart/form-data" \\
      -F "file=@image.jpg"
    
    # Health check
    curl http://localhost:8000/api/v1/analyze/health
"""
