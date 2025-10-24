from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ...db import get_db
from ...models.db_models import Photo
from .profile import get_demo_user
from ...services.storage import save_image
from ...core.security import get_current_user

# File upload constraints
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10 MB
ALLOWED_MIME_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_photo(image: UploadFile = File(...), db: Session = Depends(get_db), user_id: int = Depends(get_current_user)):
    """Accept an uploaded image, save it via storage.save_image(), create a Photo DB record, and return {photo_id, image_url}.
    
    Requires valid JWT token in Authorization header.
    """
    # Validate file type
    if image.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid file type. Allowed types: {', '.join(ALLOWED_MIME_TYPES)}"
        )
    
    # read bytes from upload
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

    try:
        # save image (local or S3 depending on env)
        meta = save_image(contents, filename=image.filename)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save image: {exc}")

    # Use authenticated user instead of demo user
    photo = Photo(user_id=user_id, filename=(image.filename or meta.get("key") or "upload"), s3_key=meta.get("key"))
    db.add(photo)
    db.commit()
    db.refresh(photo)

    return {"photo_id": photo.id, "image_url": meta.get("url")}

