"""Database helpers exported for convenience.

This module exposes:
- `engine` (SQLAlchemy Engine)
- `SessionLocal` (session factory)
- `Base` (declarative base)
- `get_db` (FastAPI dependency)

Importing `app.db` will make these symbols available for other modules.
"""

from .session import engine, SessionLocal, get_db  # noqa: F401
from .base import Base  # noqa: F401

__all__ = ["engine", "SessionLocal", "Base", "get_db"]
