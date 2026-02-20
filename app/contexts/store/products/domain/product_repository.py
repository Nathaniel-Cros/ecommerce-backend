"""Product repository port (hexagonal)."""

from typing import Protocol

from app.contexts.store.products.domain.product import Product


class ProductRepository(Protocol):
    """Port used by application layer to persist and query products."""

    def save(self, product: Product) -> Product:
        ...

    def list_active(self) -> list[Product]:
        ...
