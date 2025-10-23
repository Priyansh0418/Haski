import os
from typing import Generator

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session

# Load environment variables from a .env file at project root (if present)
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./dev.db")

# SQLite needs a special connect arg
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args)

# Session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Generator[Session, None, None]:
	"""FastAPI dependency that yields a SQLAlchemy session and ensures it's closed.

	Usage in path operation:
		from app.db.session import get_db
		def endpoint(db: Session = Depends(get_db)):
			...
	"""
	db: Session = SessionLocal()
	try:
		yield db
	finally:
		db.close()
