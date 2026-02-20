"""SQLAlchemy adapter implementing ProductRepository port."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.contexts.store.products.domain.product import Product
from app.contexts.store.products.domain.product_repository import ProductRepository
from app.contexts.store.products.infrastructure.product_model import ProductModel


def _to_domain(model: ProductModel) -> Product:
    return Product(
        id=UUID(model.id),
        name=model.name,
        description=model.description,
        price_cents=model.price_cents,
        currency=model.currency,
        stock=model.stock,
        is_active=model.is_active,
        created_at=model.created_at,
    )


class SQLProductRepository(ProductRepository):
    """Product repository backed by SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def save(self, product: Product) -> Product:
        model = ProductModel(
            id=str(product.id),
            name=product.name,
            description=product.description,
            price_cents=product.price_cents,
            currency=product.currency,
            stock=product.stock,
            is_active=product.is_active,
            created_at=product.created_at,
        )
        self._session.add(model)
        self._session.commit()
        self._session.refresh(model)
        return _to_domain(model)

    def list_active(self) -> list[Product]:
        stmt: Select[tuple[ProductModel]] = (
            select(ProductModel)
            .where(ProductModel.is_active.is_(True))
            .order_by(ProductModel.created_at.desc())
        )
        models = self._session.execute(stmt).scalars().all()
        return [_to_domain(model) for model in models]
