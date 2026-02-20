"""List active products use case."""

from app.contexts.store.products.domain.product import Product
from app.contexts.store.products.domain.product_repository import ProductRepository


class ListActiveProductsUseCase:
    """Application service that returns active products."""

    def __init__(self, repository: ProductRepository) -> None:
        self._repository = repository

    def execute(self) -> list[Product]:
        return self._repository.list_active()
