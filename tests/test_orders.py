from collections.abc import Generator
from uuid import uuid4

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.shared.infrastructure.db.session import get_db
from tests.sqlite_schema import reset_sqlite_schema

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
    client = TestClient(app)

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Juan Perez",
            "customer_phone": "5512345678",
            "items": [{"product_id": str(uuid4()), "quantity": 1}],
        },
    )

    assert order_response.status_code == 404

    app.dependency_overrides.clear()


def test_create_order_fails_if_quantity_is_not_positive() -> None:
    reset_sqlite_schema(engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    order_response = client.post(
        "/api/v1/orders",
        json={
            "customer_name": "Juan Perez",
            "customer_phone": "5512345678",
            "items": [{"product_id": str(uuid4()), "quantity": 0}],
        },
    )

    assert order_response.status_code == 422

    app.dependency_overrides.clear()
