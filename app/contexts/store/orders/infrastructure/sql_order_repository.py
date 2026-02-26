"""SQLAlchemy adapter implementing OrderRepository port."""

from uuid import UUID

from sqlalchemy import Select, select
from sqlalchemy.orm import Session

from app.contexts.store.orders.domain.order import Order
from app.contexts.store.orders.domain.order_item import OrderItem
from app.contexts.store.orders.domain.order_repository import (
    ActiveProductSnapshot,
    OrderRepository,
)
from app.contexts.store.orders.domain.payment import Payment
from app.contexts.store.orders.infrastructure.order_models import (
    OrderItemModel,
    OrderModel,
    PaymentModel,
)
from app.contexts.store.products.infrastructure.product_model import ProductModel


def _to_order_model(order: Order) -> OrderModel:
    return OrderModel(
        id=str(order.id),
        order_number=order.order_number,
        customer_name=order.customer_name,
        customer_phone=order.customer_phone,
        status=order.status,
        total_cents=order.total_cents,
        created_at=order.created_at,
    )


def _to_order_item_model(order_id: UUID, item: OrderItem) -> OrderItemModel:
    return OrderItemModel(
        id=str(item.id),
        order_id=str(order_id),
        product_id=str(item.product_id),
        quantity=item.quantity,
        product_name_snapshot=item.product_name_snapshot,
        unit_price_cents_snapshot=item.unit_price_cents_snapshot,
        line_total_cents=item.line_total_cents,
    )


def _to_payment_model(payment: Payment) -> PaymentModel:
    return PaymentModel(
        id=str(payment.id),
        order_id=str(payment.order_id),
        status=payment.status,
        amount_cents=payment.amount_cents,
        currency=payment.currency,
        created_at=payment.created_at,
    )


def _to_active_product_snapshot(model: ProductModel) -> ActiveProductSnapshot:
    return ActiveProductSnapshot(
        id=UUID(model.id),
        name=model.name,
        price_cents=model.price_cents,
        currency=model.currency,
    )


class SQLOrderRepository(OrderRepository):
    """Order repository backed by SQLAlchemy session."""

    def __init__(self, session: Session) -> None:
        self._session = session

    def begin(self) -> None:
        self._session.begin()

    def commit(self) -> None:
        self._session.commit()

    def rollback(self) -> None:
        self._session.rollback()

    def get_active_products_by_ids(
        self,
        product_ids: set[UUID],
    ) -> dict[UUID, ActiveProductSnapshot]:
        if len(product_ids) == 0:
            return {}

        stmt: Select[tuple[ProductModel]] = select(ProductModel).where(
            ProductModel.id.in_([str(product_id) for product_id in product_ids]),
            ProductModel.is_active.is_(True),
        )
        products = self._session.execute(stmt).scalars().all()
        return {
            snapshot.id: snapshot
            for snapshot in (_to_active_product_snapshot(product) for product in products)
        }

    def add_order(self, order: Order) -> None:
        # Ensure parent row exists before inserting dependent order_items.
        self._session.add(_to_order_model(order))
        self._session.flush()

        for item in order.items:
            self._session.add(_to_order_item_model(order.id, item))

    def add_payment(self, payment: Payment) -> None:
        self._session.add(_to_payment_model(payment))
