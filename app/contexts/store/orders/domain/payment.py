"""Payment domain entity (base model)."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

PaymentStatus = Literal["created", "pending", "approved", "rejected", "cancelled", "refunded"]
ALLOWED_PAYMENT_STATUS: set[str] = {
    "created",
    "pending",
    "approved",
    "rejected",
    "cancelled",
    "refunded",
}


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Payment:
    """Payment linked to one order."""

    order_id: UUID
    amount_cents: int
    status: PaymentStatus = "created"
    currency: str = "MXN"
    external_payment_id: str | None = None
    init_point: str | None = None
    sandbox_init_point: str | None = None
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        currency = self.currency.strip().upper()
        if len(currency) != 3:
            raise ValueError("currency must have 3 characters")
        self.currency = currency

        if self.amount_cents <= 0:
            raise ValueError("amount_cents must be greater than zero")
        if self.status not in ALLOWED_PAYMENT_STATUS:
            raise ValueError("invalid payment status")
