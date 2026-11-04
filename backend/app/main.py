from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware

from app.api.v1.router import api_router
from app.core.config import get_settings
from app.core.errors import validation_exception_handler
from app.db.base import Base
from app.db.session import engine
from sqlalchemy import inspect, text


def _ensure_local_schema() -> None:
    Base.metadata.create_all(bind=engine)
    if not str(engine.url).startswith("sqlite"):
        return
    existing = {column["name"] for column in inspect(engine).get_columns("requirements")}
    additions = {
        "suggested_status": "VARCHAR(30) NOT NULL DEFAULT 'needs_review'",
        "confirmed_status": "VARCHAR(30)",
        "review_note": "TEXT",
        "rule_reason": "TEXT",
    }
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(text(f"ALTER TABLE requirements ADD COLUMN {name} {definition}"))
        evidence_columns = {
            column["name"] for column in inspect(engine).get_columns("evidence_matches")
        }
        if "rule_reason" not in evidence_columns:
            connection.execute(text("ALTER TABLE evidence_matches ADD COLUMN rule_reason TEXT"))


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(
        title="TenderLens API",
        description="NLP-based tender compliance intelligence for Indian MSMEs.",
        version="0.1.0",
    )
    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[
            settings.frontend_origin,
            "http://localhost:5173",
            "http://127.0.0.1:5173",
        ],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(api_router, prefix=settings.api_v1_prefix)
    _ensure_local_schema()
    return app


app = create_app()
