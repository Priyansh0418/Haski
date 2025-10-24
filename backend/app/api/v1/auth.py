from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import or_

from ...schemas.pydantic_schemas import UserCreate, Token
from ...core import security
from ...db import get_db
from ...models.db_models import User

router = APIRouter()


class LoginRequest(UserCreate):
    # reuse UserCreate fields but make email optional and accept username+password
    password: str
    username: Optional[str] = None


@router.post("/signup", response_model=Token)
def signup(user_in: UserCreate, db: Session = Depends(get_db)):
    # check existing username/email
    existing = db.query(User).filter(or_(User.username == user_in.username, User.email == user_in.email)).first()
    if existing:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Username or email already registered")

    hashed = security.get_password_hash(user_in.password)
    user = User(username=user_in.username, email=user_in.email, hashed_password=hashed)
    db.add(user)
    db.commit()
    db.refresh(user)

    access_token = security.create_access_token(subject=user.id)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/login", response_model=Token)
def login(form_data: LoginRequest, db: Session = Depends(get_db)):
    identifier = form_data.username or form_data.email
    if not identifier:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="username or email required")

    user = db.query(User).filter(or_(User.username == identifier, User.email == identifier)).first()
    if not user or not user.hashed_password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    if not security.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    token = security.create_access_token(subject=user.id)
    return {"access_token": token, "token_type": "bearer"}
