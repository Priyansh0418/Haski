"""Admin API package"""

from fastapi import APIRouter

router = APIRouter()

# Include sub-routers
from . import recommender  # noqa: E402,F401

router.include_router(recommender.router, prefix="/recommender", tags=["admin-recommender"])

__all__ = ["router"]
