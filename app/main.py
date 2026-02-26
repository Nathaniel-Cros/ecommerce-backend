"""FastAPI application entrypoint."""

from typing import Annotated

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.shared.infrastructure.http.routes import register_routes
from app.shared.config.settings import get_settings
from app.shared.infrastructure.db.ping import ping_db
from app.shared.infrastructure.db.session import get_db


def create_app() -> FastAPI:
    """Application factory used by runtime and tests."""

    app = FastAPI(title="Ecommerce Backend", version="0.2.0")
    _ = get_settings()
    register_routes(app)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/db/ping", tags=["system"])
    def db_ping(db: Annotated[Session, Depends(get_db)]) -> dict[str, str]:
        ping_db(db)
        return {"db": "ok"}

    return app


app = create_app()
