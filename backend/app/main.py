import os
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

# DB & models
from app.db.session import engine
from app.db.base import Base

# ensure models are imported so they are registered on Base
import app.models.db_models  # noqa: F401

from app.api.v1 import router as api_v1_router


APP_TITLE = "SkinHairAI API"
APP_VERSION = "0.1"

app = FastAPI(title=APP_TITLE, version=APP_VERSION)


@app.get("/")
def read_root():
    return {"status": "ok", "message": f"{APP_TITLE} running"}


# CORS
FRONTEND_URL = os.getenv("FRONTEND_URL", "*")
if FRONTEND_URL == "*":
    allow_origins = ["*"]
else:
    # allow comma-separated list
    allow_origins = [u.strip() for u in FRONTEND_URL.split(",") if u.strip()]

app.add_middleware(
    CORSMiddleware,
    allow_origins=allow_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# include API v1 router (it already includes auth/profile/photos/analyze)
app.include_router(api_v1_router, prefix="/api/v1")


@app.on_event("startup")
def on_startup():
    # create DB tables if they don't exist (dev convenience)
    Base.metadata.create_all(bind=engine)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("app.main:app", host="0.0.0.0", port=int(os.getenv("PORT", 8000)), log_level="info")
