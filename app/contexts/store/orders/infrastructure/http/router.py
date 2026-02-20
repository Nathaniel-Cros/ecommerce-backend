"""HTTP router for orders context (scaffold)."""

from fastapi import APIRouter

router = APIRouter(prefix="/orders", tags=["orders"])
