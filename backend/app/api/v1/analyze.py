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

router = APIRouter()


@router.post("/photo", status_code=status.HTTP_201_CREATED)
def analyze_photo(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Save uploaded image, run local analysis, persist Analysis, and return the analysis JSON."""
    try:
        contents = image.file.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file")

    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

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

    # Persist Photo and Analysis records
    user = get_demo_user(db)

    photo = Photo(user_id=user.id, filename=(image.filename or meta.get("key") or "upload"), s3_key=meta.get("key"))
    db.add(photo)
    db.commit()
    db.refresh(photo)

    # Map analysis_result to Analysis model fields
    analysis = Analysis(
        user_id=user.id,
        photo_id=photo.id,
        skin_type=analysis_result.get("skin_type"),
        hair_type=analysis_result.get("hair_type"),
        conditions=analysis_result.get("conditions_detected") or analysis_result.get("conditions"),
        confidence_scores=analysis_result.get("confidence_scores"),
    )

    db.add(analysis)
    db.commit()
    db.refresh(analysis)

    # Return the analysis JSON with identifiers
    out = dict(analysis_result)
    out.update({"id": analysis.id, "photo_id": photo.id})
    return out

