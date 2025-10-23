import os
from datetime import datetime, timedelta
from typing import Optional

from jose import jwt
from passlib.context import CryptContext

from app.core.config import settings


# Password hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """Hash a plaintext password using bcrypt."""
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a plaintext password against the hashed value."""
    return pwd_context.verify(plain_password, hashed_password)


# JWT helpers
def create_access_token(subject: str, expires_minutes: Optional[int] = None) -> str:
    """Create a JWT access token with `sub` set to the subject (usually user id or username).

    The SECRET_KEY, JWT_ALGORITHM and default expiry are read from `app.core.config.settings`.
    """
    if expires_minutes is None:
        expires_minutes = settings.access_token_expire_minutes

    expire = datetime.utcnow() + timedelta(minutes=expires_minutes)
    to_encode = {"sub": str(subject), "exp": expire}

    key = settings.secret_key
    alg = getattr(settings, "jwt_algorithm", "HS256")

    token = jwt.encode(to_encode, key, algorithm=alg)
    return token


def decode_access_token(token: str) -> dict:
    """Decode a JWT and return the claims. Raises jose.JWTError on invalid token."""
    key = settings.secret_key
    alg = getattr(settings, "jwt_algorithm", "HS256")
    return jwt.decode(token, key, algorithms=[alg])

