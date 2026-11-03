from __future__ import annotations

from collections.abc import Generator

from api_app.db.database import SessionLocal
from sqlalchemy.orm import Session


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
