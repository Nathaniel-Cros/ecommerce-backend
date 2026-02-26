from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.contexts.store.orders.domain.payment_gateway import PaymentProviderResponse
from app.contexts.store.orders.infrastructure.http.router import get_mercadopago_gateway
from app.main import app
from app.shared.infrastructure.db.session import get_db
from tests.sqlite_schema import reset_sqlite_schema


class FakeMercadoPagoGateway:
    def create_preference(self, order) -> PaymentProviderResponse:  # type: ignore[no-untyped-def]
        return PaymentProviderResponse(
            provider_payment_id="pref_test_123",
            init_point="https://mp.test/init-point",
            sandbox_init_point="https://sandbox.mp.test/init-point",
        )


engine = create_engine(
    "sqlite+pysqlite://",
    future=True,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_create_order_valid() -> None:
    reset_sqlite_schema(engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mercadopago_gateway] = lambda: FakeMercadoPagoGateway()
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Omega 3",
            "description": "Aceite de pescado",
            "price_cents": 25900,
            "currency": "MXN",
            "stock": 10,
            "is_active": True,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Juan Perez",
            "customer_phone": "5512345678",
            "payment_method": "cash",
            "items": [{"product_id": product_id, "quantity": 2}],
        },
    )

    assert order_response.status_code == 201
    body = order_response.json()
    assert body["status"] == "pending_payment"
    assert body["total_cents"] == 51800
    assert body["order_number"].startswith("ORD-")

    app.dependency_overrides.clear()


def test_create_order_fails_if_product_not_found() -> None:
    reset_sqlite_schema(engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mercadopago_gateway] = lambda: FakeMercadoPagoGateway()
    client = TestClient(app)

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Juan Perez",
            "customer_phone": "5512345678",
            "payment_method": "cash",
            "items": [{"product_id": str(uuid4()), "quantity": 1}],
        },
    )

    assert order_response.status_code == 404

    app.dependency_overrides.clear()


def test_create_order_fails_if_quantity_is_not_positive() -> None:
    reset_sqlite_schema(engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mercadopago_gateway] = lambda: FakeMercadoPagoGateway()
    client = TestClient(app)

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Juan Perez",
            "customer_phone": "5512345678",
            "payment_method": "cash",
            "items": [{"product_id": str(uuid4()), "quantity": 0}],
        },
    )

    assert order_response.status_code == 422

    app.dependency_overrides.clear()


def test_create_order_with_mercadopago_returns_payment_url() -> None:
    reset_sqlite_schema(engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mercadopago_gateway] = lambda: FakeMercadoPagoGateway()
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Vitamina D",
            "description": "Suplemento",
            "price_cents": 14900,
            "currency": "MXN",
            "stock": 5,
            "is_active": True,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Ana Lopez",
            "customer_phone": "5587654321",
            "payment_method": "mercadopago",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )

    assert order_response.status_code == 201
    body = order_response.json()
    assert body["payment_url"] == "https://mp.test/init-point"

    app.dependency_overrides.clear()


def test_create_order_with_cash_does_not_return_payment_url() -> None:
    reset_sqlite_schema(engine)
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_mercadopago_gateway] = lambda: FakeMercadoPagoGateway()
    client = TestClient(app)

    product_response = client.post(
        "/api/v1/products",
        json={
            "name": "Zinc",
            "description": None,
            "price_cents": 9900,
            "currency": "MXN",
            "stock": 5,
            "is_active": True,
        },
    )
    assert product_response.status_code == 201
    product_id = product_response.json()["id"]

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Luis Diaz",
            "customer_phone": "5511112222",
            "payment_method": "cash",
            "items": [{"product_id": product_id, "quantity": 1}],
        },
    )

    assert order_response.status_code == 201
    body = order_response.json()
    assert body["payment_url"] is None

    app.dependency_overrides.clear()
