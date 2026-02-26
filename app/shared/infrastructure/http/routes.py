"""Central HTTP route registry."""

from fastapi import APIRouter, FastAPI

from app.contexts.store.products.infrastructure.http.router import router as products_router
from app.contexts.store.orders.infrastructure.http.router import router as orders_router

API_V1_PREFIX = "/api/v1"


def register_routes(app: FastAPI) -> None:
    """Register all public API routes under a single versioned prefix."""

    version_api_router = APIRouter(prefix=API_V1_PREFIX)
    version_api_router.include_router(products_router)
    version_api_router.include_router(orders_router)
    app.include_router(version_api_router)
