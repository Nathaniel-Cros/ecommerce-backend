"""HTTP router for orders context."""

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, field_validator
from sqlalchemy.orm import Session

from app.contexts.store.orders.application.create_order import (
    CreateOrderCommand,
    CreateOrderItemInput,
    CreateOrderUseCase,
    InvalidOrderError,
    ProductNotFoundError,
)
from app.contexts.store.orders.domain.order import Order
from app.contexts.store.orders.domain.order_repository import OrderRepository
from app.contexts.store.orders.infrastructure.sql_order_repository import SQLOrderRepository
from app.shared.infrastructure.db.session import get_db

router = APIRouter(prefix="/orders", tags=["orders"])


class CreateOrderItemRequest(BaseModel):
    product_id: UUID
    quantity: int = Field(gt=0)


class CreateOrderRequest(BaseModel):
    customer_name: str = Field(min_length=1, max_length=255)
    customer_phone: str = Field(min_length=3, max_length=40)
    items: list[CreateOrderItemRequest] = Field(min_length=1)

    @field_validator("customer_name")
    @classmethod
    def normalize_customer_name(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("customer_name must not be empty")
        return normalized

    @field_validator("customer_phone")
    @classmethod
    def normalize_customer_phone(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("customer_phone must not be empty")
        return normalized


class CreateOrderResponse(BaseModel):
    order_number: str
    status: str
    total_cents: int


def get_order_repository(db: Session = Depends(get_db)) -> OrderRepository:
    return SQLOrderRepository(db)


def _to_response(order: Order) -> CreateOrderResponse:
    return CreateOrderResponse(
        order_number=order.order_number,
        status=order.status,
        total_cents=order.total_cents,
    )


@router.post("", response_model=CreateOrderResponse, status_code=status.HTTP_201_CREATED)
def create_order(
    payload: CreateOrderRequest,
    repository: OrderRepository = Depends(get_order_repository),
) -> CreateOrderResponse:
    use_case = CreateOrderUseCase(repository)

    try:
        order = use_case.execute(
            CreateOrderCommand(
                customer_name=payload.customer_name,
                customer_phone=payload.customer_phone,
                items=[
                    CreateOrderItemInput(product_id=item.product_id, quantity=item.quantity)
                    for item in payload.items
                ],
            )
        )
    except ProductNotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc)) from exc
    except InvalidOrderError as exc:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=str(exc)) from exc

    return _to_response(order)
