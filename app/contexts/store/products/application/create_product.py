"""Create product use case."""

from dataclasses import dataclass

from app.contexts.store.products.domain.product import Product
from app.contexts.store.products.domain.product_repository import ProductRepository


@dataclass(frozen=True, slots=True)
class CreateProductCommand:
    """Input data for creating a product."""

    name: str
    price_cents: int
    stock: int
    description: str | None = None
    currency: str = "MXN"
    is_active: bool = True


class CreateProductUseCase:
    """Application service that creates a product."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self, command: CreateProductCommand) -> Product:
        product = Product(
            name=command.name,
            description=command.description,
            price_cents=command.price_cents,
            currency=command.currency,
            stock=command.stock,
            is_active=command.is_active,
        )
        return self._repository.save(product)
