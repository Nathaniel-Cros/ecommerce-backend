"""Order domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from app.contexts.store.orders.domain.order_item import OrderItem

OrderStatus = Literal["pending_payment", "paid", "cancelled", "picked_up"]
ALLOWED_ORDER_STATUS: set[str] = {"pending_payment", "paid", "cancelled", "picked_up"}


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Order:
    """Order aggregate root."""

    order_number: str
    customer_name: str
    customer_phone: str
    items: list[OrderItem]
    status: OrderStatus = "pending_payment"
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)
    total_cents: int = field(init=False)

    def __post_init__(self) -> None:
        self.order_number = self.order_number.strip()
        self.customer_name = self.customer_name.strip()
        self.customer_phone = self.customer_phone.strip()

        if not self.order_number:
            raise ValueError("order_number is required")
        if not self.customer_name:
            raise ValueError("customer_name is required")
        if not self.customer_phone:
            raise ValueError("customer_phone is required")
        if len(self.items) == 0:
            raise ValueError("order must have at least one item")
        if self.status not in ALLOWED_ORDER_STATUS:
            raise ValueError("invalid order status")

        self.total_cents = sum(item.line_total_cents for item in self.items)
