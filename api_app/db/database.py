from __future__ import annotations

from api_app.config import settings
from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker


class Base(DeclarativeBase):
    pass


def get_engine():
    return create_engine(settings.database_url, pool_pre_ping=True)


engine = get_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def create_db_and_tables() -> None:
    from api_app.db import models  # noqa: F401

    try:
        Base.metadata.create_all(bind=engine)
    except Exception:
        import logging

        logging.getLogger("dentalvision.db").warning(
            "Database schema creation was skipped because PostgreSQL is not reachable."
        )
