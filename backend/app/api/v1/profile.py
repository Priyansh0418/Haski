from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from sqlalchemy.orm import Session

from ...db import get_db
from ...models.db_models import User, Profile

router = APIRouter()


class ProfileIn(BaseModel):
    birth_year: Optional[int] = None
    age: Optional[int] = None
    gender: Optional[str] = None
    location: Optional[str] = None
    allergies: Optional[str] = None
    lifestyle: Optional[str] = None
    skin_type: Optional[str] = None
    hair_type: Optional[str] = None


def get_demo_user(db: Session) -> User:
    """Get or create a demo user placeholder (using demo@example.com)."""
    demo_email = "demo@example.com"
    user = db.query(User).filter(User.email == demo_email).first()
    if not user:
        user = User(username="demo", email=demo_email)
        db.add(user)
        db.commit()
        db.refresh(user)
    return user


@router.get("/me", response_model=dict)
def read_my_profile(db: Session = Depends(get_db)):
    user = get_demo_user(db)
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Profile not found")
    return {
        "id": profile.id,
        "user_id": profile.user_id,
        "age": profile.age,
        "gender": profile.gender,
        "location": profile.location,
        "allergies": profile.allergies,
        "lifestyle": profile.lifestyle,
        "skin_type": profile.skin_type,
        "hair_type": profile.hair_type,
    }


@router.post("/", response_model=dict)
def create_profile(payload: ProfileIn, db: Session = Depends(get_db)):
    user = get_demo_user(db)

    # compute age from birth_year if provided
    age = payload.age
    if payload.birth_year:
        try:
            current_year = datetime.utcnow().year
            age = current_year - int(payload.birth_year)
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid birth_year")

    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if profile:
        raise HTTPException(status_code=400, detail="Profile already exists; use PUT to update")

    profile = Profile(
        user_id=user.id,
        age=age,
        gender=payload.gender,
        location=payload.location,
        allergies=payload.allergies,
        lifestyle=payload.lifestyle,
        skin_type=payload.skin_type,
        hair_type=payload.hair_type,
    )
    db.add(profile)
    db.commit()
    db.refresh(profile)
    return {"id": profile.id, "user_id": profile.user_id}


@router.put("/", response_model=dict)
def update_profile(payload: ProfileIn, db: Session = Depends(get_db)):
    user = get_demo_user(db)
    profile = db.query(Profile).filter(Profile.user_id == user.id).first()
    if not profile:
        raise HTTPException(status_code=404, detail="Profile not found")

    # compute age if birth_year provided
    if payload.birth_year:
        current_year = datetime.utcnow().year
        profile.age = current_year - int(payload.birth_year)
    elif payload.age is not None:
        profile.age = payload.age

    for field in ("gender", "location", "allergies", "lifestyle", "skin_type", "hair_type"):
        val = getattr(payload, field)
        if val is not None:
            setattr(profile, field, val)

    db.add(profile)
    db.commit()
    db.refresh(profile)

    return {"id": profile.id, "user_id": profile.user_id}
