"""FastAPI application entrypoint."""

from fastapi import Depends, FastAPI
from sqlalchemy.orm import Session

from app.contexts.store.orders.infrastructure.http.router import router as orders_router
from app.contexts.store.products.infrastructure.http.router import router as products_router
from app.shared.infrastructure.db.ping import ping_db
from app.shared.infrastructure.db.session import get_db


def create_app() -> FastAPI:
    """Application factory used by runtime and tests."""

    app = FastAPI(title="Ecommerce Backend", version="0.1.0")

    app.include_router(products_router)
    app.include_router(orders_router)

    @app.get("/health", tags=["system"])
    def health() -> dict[str, str]:
        return {"status": "ok"}

    @app.get("/db/ping", tags=["system"])
    def db_ping(db: Session = Depends(get_db)) -> dict[str, str]:
        ping_db(db)
        return {"db": "ok"}

    return app


app = create_app()
