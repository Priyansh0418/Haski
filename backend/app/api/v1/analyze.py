from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

import os
import tempfile
import urllib.request

from ...db import get_db
from ...models.db_models import Photo, Analysis
from .profile import get_demo_user
from ...services.storage import save_image
from ...services.ml_infer import analyze_image_local
from ...core.security import get_current_user

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

router = APIRouter()


@router.post("/image", status_code=status.HTTP_201_CREATED)
def analyze_photo(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Save uploaded image, run local analysis, persist Analysis, and return the analysis JSON.
    
    Uses demo user for unauthenticated requests.
    """
    # Get or create demo user
    user = get_demo_user(db)
    user_id = user.id
    # Validate file type
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    try:
        contents = image.file.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file")

    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

    # Validate file size
    if len(contents) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE / (1024*1024):.1f} MB"
        )

    # Save the image (local or S3 depending on env)
    try:
        meta = save_image(contents, filename=image.filename)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save image: {exc}")

    # Determine a local path to analyze: prefer file:// URLs; otherwise download the presigned URL to a temp file
    url = meta.get("url") or ""
    local_path = None
    downloaded_tmp = None
    try:
        if url.startswith("file://"):
            local_path = url[7:]
        else:
            # download remote URL to a temp file
            fd, tmp_path = tempfile.mkstemp(suffix=os.path.splitext(image.filename or "")[1] or ".jpg")
            os.close(fd)
            try:
                urllib.request.urlretrieve(url, tmp_path)
                local_path = tmp_path
                downloaded_tmp = tmp_path
            except Exception:
                # if download fails, try to use a local tmp file we wrote earlier (some storage implementations keep it)
                # fallback: raise
                raise

        # Run local analysis
        analysis_result = analyze_image_local(local_path)
        
        # Handle model output format
        # New PyTorch model returns: class_id, class_name, confidence, probabilities, model_type
        # Map to analysis schema
        if "error" in analysis_result:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Analysis failed: {analysis_result['error']}"
            )
        
        # Transform model output to analysis schema
        analysis_output = {
            "class_id": analysis_result.get("class_id", 0),
            "class_name": analysis_result.get("class_name", "unknown"),
            "confidence": analysis_result.get("confidence", 0.0),
            "probabilities": analysis_result.get("probabilities", []),
            "model_type": analysis_result.get("model_type", "unknown"),
            "model_version": "v1-pytorch"
        }
    except FileNotFoundError:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Saved image file not found for analysis")
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Analysis failed: {exc}")
    finally:
        # cleanup downloaded tmp if any
        try:
            if downloaded_tmp and os.path.exists(downloaded_tmp):
                os.remove(downloaded_tmp)
        except Exception:
            pass

    # Persist Photo and Analysis records using authenticated user
    photo = Photo(user_id=user_id, filename=(image.filename or meta.get("key") or "upload"), s3_key=meta.get("key"))
    db.add(photo)
    db.commit()
    db.refresh(photo)

    # Map analysis output to Analysis model
    # For now, model outputs single class - in production with multi-class model:
    # skin_type, hair_type, conditions could be separate predictions
    class_name = analysis_output.get("class_name", "unknown")
    confidence = analysis_output.get("confidence", 0.0)
    
    analysis = Analysis(
        user_id=user_id,
        photo_id=photo.id,
        skin_type=class_name,  # PyTorch model outputs class_name
        hair_type=class_name,  # Can be either skin or hair type
        conditions=[class_name] if class_name else [],
        confidence_scores={
            "skin_type": confidence,
            "hair_type": confidence,
            "conditions": [confidence] if class_name else []
        },
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Return business-friendly format
    response = {
        "skin_type": analysis.skin_type,
        "hair_type": analysis.hair_type,
        "conditions_detected": analysis.conditions,
        "confidence_scores": {
            analysis.skin_type: confidence,
            analysis.hair_type: confidence,
        },
        "model_version": "v1-skinhair-classifier",
        # Metadata
        "analysis_id": analysis.id,
        "photo_id": photo.id,
        "status": "success"
    }
    return response

