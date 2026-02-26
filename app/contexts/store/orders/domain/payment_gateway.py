"""Payment gateway port and provider response models."""

from dataclasses import dataclass
from typing import Protocol

from app.contexts.store.orders.domain.order import Order


@dataclass(frozen=True, slots=True)
class PaymentProviderResponse:
    """Response returned by an external payment provider."""

    provider_payment_id: str
    init_point: str
    sandbox_init_point: str | None = None


class PaymentGateway(Protocol):
    """Port for payment provider integrations."""

    def create_preference(self, order: Order) -> PaymentProviderResponse:
        ...
