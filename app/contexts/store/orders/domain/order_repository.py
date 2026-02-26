"""Order repository port."""

from dataclasses import dataclass
from typing import Protocol
from uuid import UUID

from app.contexts.store.orders.domain.order import Order
from app.contexts.store.orders.domain.payment import Payment


@dataclass(frozen=True, slots=True)
class ActiveProductSnapshot:
    """Projection used by CreateOrder use case."""

    id: UUID
    name: str
    price_cents: int
    currency: str


class OrderRepository(Protocol):
    """Port used by application layer."""

    def begin(self) -> None:
        ...

    def commit(self) -> None:
        ...

    def rollback(self) -> None:
        ...

    def get_active_products_by_ids(
        self,
        product_ids: set[UUID],
    ) -> dict[UUID, ActiveProductSnapshot]:
        ...

    def add_order(self, order: Order) -> None:
        ...

    def add_payment(self, payment: Payment) -> None:
        ...
