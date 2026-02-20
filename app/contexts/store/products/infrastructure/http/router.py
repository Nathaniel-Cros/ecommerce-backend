"""HTTP router for products context."""

from datetime import datetime
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.contexts.store.products.application.create_product import (
    CreateProductCommand,
    CreateProductUseCase,
)
from app.contexts.store.products.application.list_active_products import (
    ListActiveProductsUseCase,
)
from app.contexts.store.products.domain.product import Product
from app.contexts.store.products.domain.product_repository import ProductRepository
from app.contexts.store.products.infrastructure.sql_product_repository import (
    SQLProductRepository,
)
from app.shared.infrastructure.db.session import get_db

router = APIRouter(prefix="/products", tags=["products"])


class CreateProductRequest(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    description: str | None = Field(default=None, max_length=2000)
    price_cents: int = Field(gt=0)
    currency: str = Field(default="MXN", min_length=3, max_length=3)
    stock: int = Field(ge=0)
    is_active: bool = True

    @field_validator("name")
    @classmethod
    def normalize_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("name must not be empty")
        return normalized

    @field_validator("currency")
    @classmethod
    def normalize_currency(cls, value: str) -> str:
        return value.strip().upper()


class ProductResponse(BaseModel):
    id: UUID
    name: str
    description: str | None
    price_cents: int
    currency: str
    stock: int
    is_active: bool
    created_at: datetime


def _to_response(product: Product) -> ProductResponse:
    return ProductResponse(
        id=product.id,
        name=product.name,
        description=product.description,
        price_cents=product.price_cents,
        currency=product.currency,
        stock=product.stock,
        is_active=product.is_active,
        created_at=product.created_at,
    )


def get_product_repository(db: Session = Depends(get_db)) -> ProductRepository:
    return SQLProductRepository(db)


@router.post("", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
def create_product(
    payload: CreateProductRequest,
    repository: ProductRepository = Depends(get_product_repository),
) -> ProductResponse:
    use_case = CreateProductUseCase(repository)

    try:
        product = use_case.execute(
            CreateProductCommand(
                name=payload.name,
                description=payload.description,
                price_cents=payload.price_cents,
                currency=payload.currency,
                stock=payload.stock,
                is_active=payload.is_active,
            )
        )
    except ValueError as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(exc),
        ) from exc

    return _to_response(product)


@router.get("", response_model=list[ProductResponse])
def list_products(
    repository: ProductRepository = Depends(get_product_repository),
) -> list[ProductResponse]:
    use_case = ListActiveProductsUseCase(repository)
    products = use_case.execute()
    return [_to_response(product) for product in products]
