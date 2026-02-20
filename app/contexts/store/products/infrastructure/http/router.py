"""HTTP router for products context (scaffold)."""

from fastapi import APIRouter

router = APIRouter(prefix="/products", tags=["products"])
