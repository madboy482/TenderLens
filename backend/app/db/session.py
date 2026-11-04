from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.core.config import get_settings


def _connect_args(database_url: str) -> dict[str, object]:
    return {"check_same_thread": False} if database_url.startswith("sqlite") else {}


def create_session_factory() -> sessionmaker[Session]:
    settings = get_settings()
    return sessionmaker(
        bind=create_engine(
            settings.database_url,
            connect_args=_connect_args(settings.database_url),
        ),
        autoflush=False,
        autocommit=False,
    )


SessionLocal = create_session_factory()
engine = SessionLocal.kw["bind"]


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
