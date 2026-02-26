"""Mercado Pago Checkout Pro adapter."""

import httpx

from app.contexts.store.orders.domain.order import Order
from app.contexts.store.orders.domain.payment_gateway import (
    PaymentGateway,
    PaymentProviderResponse,
)


class MercadoPagoGateway(PaymentGateway):
    """Sync adapter for Mercado Pago preferences API."""

    def __init__(
        self,
        access_token: str | None,
        webhook_url: str | None = None,
        environment: str = "sandbox",
        base_url: str = "https://api.mercadopago.com",
    ) -> None:
        self._access_token = access_token
        self._webhook_url = webhook_url
        self._environment = environment
        self._base_url = base_url.rstrip("/")

    def create_preference(self, order: Order) -> PaymentProviderResponse:
        if not self._access_token:
            raise ValueError("MP_ACCESS_TOKEN is required for Mercado Pago payments")

        items_payload = [
            {
                "title": item.product_name_snapshot,
                "quantity": item.quantity,
                "unit_price": item.unit_price_cents_snapshot / 100,
                "currency_id": "MXN",
            }
            for item in order.items
        ]

        payload: dict[str, object] = {
            "items": items_payload,
            "external_reference": order.order_number,
            "metadata": {"order_id": str(order.id), "environment": self._environment},
        }
        if self._webhook_url:
            payload["notification_url"] = self._webhook_url

        headers = {
            "Authorization": f"Bearer {self._access_token}",
            "Content-Type": "application/json",
        }

        with httpx.Client(timeout=15.0) as client:
            response = client.post(
                f"{self._base_url}/checkout/preferences",
                headers=headers,
                json=payload,
            )
        response.raise_for_status()

        data = response.json()
        provider_payment_id = str(data.get("id", ""))
        init_point = str(data.get("init_point", ""))
        sandbox_init_point_raw = data.get("sandbox_init_point")
        sandbox_init_point = str(sandbox_init_point_raw) if sandbox_init_point_raw else None

        if not provider_payment_id or not init_point:
            raise ValueError("Mercado Pago preference response is missing required fields")

        return PaymentProviderResponse(
            provider_payment_id=provider_payment_id,
            init_point=init_point,
            sandbox_init_point=sandbox_init_point,
        )
