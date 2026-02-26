"""Order item domain entity."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass(slots=True)
class OrderItem:
    """Immutable snapshot of a purchased product inside an order."""

    product_id: UUID
    quantity: int
    product_name_snapshot: str
    unit_price_cents_snapshot: int
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        self.product_name_snapshot = self.product_name_snapshot.strip()

        if self.quantity <= 0:
            raise ValueError("quantity must be greater than zero")
        if not self.product_name_snapshot:
            raise ValueError("product_name_snapshot is required")
        if self.unit_price_cents_snapshot <= 0:
            raise ValueError("unit_price_cents_snapshot must be greater than zero")

    @property
    def line_total_cents(self) -> int:
        return self.quantity * self.unit_price_cents_snapshot
