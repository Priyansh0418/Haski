from fastapi import APIRouter, UploadFile, File, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db import get_db
from app.models.db_models import Photo
from app.api.v1.profile import get_demo_user
from app.services.storage import save_image

router = APIRouter()


@router.post("/upload", status_code=status.HTTP_201_CREATED)
def upload_photo(image: UploadFile = File(...), db: Session = Depends(get_db)):
    """Accept an uploaded image, save it via storage.save_image(), create a Photo DB record, and return {photo_id, image_url}."""
    # read bytes from upload
    try:
        contents = image.file.read()
    except Exception:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Could not read uploaded file")

    if not contents:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file uploaded")

    try:
        # save image (local or S3 depending on env)
        meta = save_image(contents, filename=image.filename)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to save image: {exc}")

    # associate with demo user if no auth yet
    user = get_demo_user(db)

    photo = Photo(user_id=user.id, filename=(image.filename or meta.get("key") or "upload"), s3_key=meta.get("key"))
    db.add(photo)
    db.commit()
    db.refresh(photo)

    return {"photo_id": photo.id, "image_url": meta.get("url")}
from fastapi import APIRouter, UploadFile, File, Depends
from app.services.storage import upload_to_s3
from app.db.session import get_db

