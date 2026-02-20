from fastapi import FastAPI, APIRouter

from app.contexts.store.products.infrastructure.http.router import router as products_router
from app.contexts.store.orders.infrastructure.http.router import router as orders_router

def register_routes(app: FastAPI) -> None:
    version_api_router = APIRouter(prefix="/api/v1")

    version_api_router.include_router(products_router)
    version_api_router.include_router(orders_router)

    app.include_router(version_api_router)