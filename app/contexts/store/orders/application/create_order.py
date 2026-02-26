"""Create order use case."""

from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Literal
from uuid import UUID, uuid4

from app.contexts.store.orders.domain.order import Order
from app.contexts.store.orders.domain.order_item import OrderItem
from app.contexts.store.orders.domain.payment_gateway import PaymentGateway
from app.contexts.store.orders.domain.order_repository import (
    ActiveProductSnapshot,
    OrderRepository,
)
from app.contexts.store.orders.domain.payment import Payment


class CreateOrderError(Exception):
    """Base error for order creation failures."""


class ProductNotFoundError(CreateOrderError):
    """Raised when one or more requested products are missing/inactive."""


class InvalidOrderError(CreateOrderError):
    """Raised for invalid order input."""


class PaymentGatewayError(CreateOrderError):
    """Raised when preference creation with provider fails."""


@dataclass(frozen=True, slots=True)
class CreateOrderItemInput:
    product_id: UUID
    quantity: int


@dataclass(frozen=True, slots=True)
class CreateOrderCommand:
    customer_name: str
    customer_phone: str
    items: list[CreateOrderItemInput]
    payment_method: Literal["mercadopago", "cash"]


@dataclass(frozen=True, slots=True)
class CreateOrderResult:
    order: Order
    payment_url: str | None


def _generate_order_number() -> str:
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    suffix = str(uuid4()).split("-")[0].upper()
    return f"ORD-{timestamp}-{suffix}"


class CreateOrderUseCase:
    """Application service that creates an order and a base payment."""

    def __init__(self, repository: OrderRepository, payment_gateway: PaymentGateway) -> None:
        self._repository = repository
        self._payment_gateway = payment_gateway

    def execute(self, command: CreateOrderCommand) -> CreateOrderResult:
        if len(command.items) == 0:
            raise InvalidOrderError("order must include at least one item")

        product_ids = {item.product_id for item in command.items}

        self._repository.begin()
        try:
            products = self._repository.get_active_products_by_ids(product_ids)
            missing_ids = [str(product_id) for product_id in product_ids if product_id not in products]
            if missing_ids:
                raise ProductNotFoundError(
                    f"products not found or inactive: {', '.join(sorted(missing_ids))}"
                )

            currency = self._resolve_currency(products)
            order_items = self._build_items(command.items, products)

            order = Order(
                order_number=_generate_order_number(),
                customer_name=command.customer_name,
                customer_phone=command.customer_phone,
                items=order_items,
                status="pending_payment",
            )
            payment = Payment(
                order_id=order.id,
                amount_cents=order.total_cents,
                status="created",
                currency=currency,
            )

            self._repository.add_order(order)
            self._repository.add_payment(payment)
            self._repository.commit()
        except Exception:
            self._repository.rollback()
            raise

        payment_url: str | None = None
        if command.payment_method == "mercadopago":
            try:
                provider_response = self._payment_gateway.create_preference(order)
            except Exception as exc:
                raise PaymentGatewayError("failed to create Mercado Pago preference") from exc

            payment.status = "pending"
            payment.external_payment_id = provider_response.provider_payment_id
            payment.init_point = provider_response.init_point
            payment.sandbox_init_point = provider_response.sandbox_init_point

            self._repository.begin()
            try:
                self._repository.update_payment(payment)
                self._repository.commit()
            except Exception:
                self._repository.rollback()
                raise

            payment_url = provider_response.init_point

        return CreateOrderResult(order=order, payment_url=payment_url)

    def _build_items(
        self,
        requested_items: list[CreateOrderItemInput],
        products: dict[UUID, ActiveProductSnapshot],
    ) -> list[OrderItem]:
        items: list[OrderItem] = []

        for requested_item in requested_items:
            if requested_item.quantity <= 0:
                raise InvalidOrderError("quantity must be greater than zero")

            product = products[requested_item.product_id]
            items.append(
                OrderItem(
                    product_id=requested_item.product_id,
                    quantity=requested_item.quantity,
                    product_name_snapshot=product.name,
                    unit_price_cents_snapshot=product.price_cents,
                )
            )

        return items

    def _resolve_currency(self, products: dict[UUID, ActiveProductSnapshot]) -> str:
        currencies = {product.currency.upper() for product in products.values()}
        if len(currencies) != 1:
            raise InvalidOrderError("mixed product currencies are not supported")
        return next(iter(currencies))
