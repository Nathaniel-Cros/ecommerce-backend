"""Product domain entity."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4


def _utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(slots=True)
class Product:
    """Pure domain entity for products."""

    name: str
    price_cents: int
    stock: int
    description: str | None = None
    currency: str = "MXN"
    is_active: bool = True
    id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=_utc_now)

    def __post_init__(self) -> None:
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("name must not be empty")

        if self.price_cents <= 0:
            raise ValueError("price_cents must be greater than zero")

        if self.stock < 0:
            raise ValueError("stock must be greater than or equal to zero")

        currency = self.currency.strip().upper()
        if len(currency) != 3:
            raise ValueError("currency must have 3 characters")
        self.currency = currency
