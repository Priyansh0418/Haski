"""API v1 package"""

from fastapi import APIRouter

router = APIRouter()


@router.get("/health")
def health_check():
    return {"status": "ok", "version": "v1"}


# include sub-routers
from . import auth  # noqa: E402,F401

router.include_router(auth.router, prefix="/auth", tags=["auth"])
from . import profile  # noqa: E402,F401

router.include_router(profile.router, prefix="/profile", tags=["profile"])
from . import photos  # noqa: E402,F401

router.include_router(photos.router, prefix="/photos", tags=["photos"])
from . import analyze  # noqa: E402,F401

router.include_router(analyze.router, prefix="/analyze", tags=["analyze"])

__all__ = ["router"]
