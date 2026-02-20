"""FastAPI application entrypoint."""

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.shared.infrastructure.http.routes import register_routes
from app.contexts.store.products.infrastructure.product_model import ProductModel
from typing import Annotated
from app.shared.config.settings import get_settings
from app.shared.infrastructure.db.base import Base
from app.shared.infrastructure.db.ping import ping_db
from app.shared.infrastructure.db.session import engine, get_db


def create_app() -> FastAPI:
    """Application factory used by runtime and tests."""

    app = FastAPI(title="Ecommerce Backend", version="0.2.0")
    settings = get_settings()

    register_routes(app)

    @app.on_event("startup")
    def startup() -> None:
        # Keep dev/test usable before Alembic is introduced in next step.
        _ = ProductModel
        if settings.env in {"dev", "test"}:
            Base.metadata.create_all(bind=engine)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/db/ping", tags=["system"])
    def db_ping(db: Annotated[Session, Depends(get_db)]):
        ping_db(db)
        return {"db": "ok"}

    return app


app = create_app()
