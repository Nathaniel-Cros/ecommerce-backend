from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.shared.infrastructure.db.base import Base
from app.shared.infrastructure.db.session import get_db

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


def test_create_product_returns_created() -> None:
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.post(
        "/api/v1/products",
        json={
            "name": "Omega 3",
            "description": "Aceite de pescado",
            "price_cents": 25900,
            "currency": "mxn",
            "stock": 10,
            "is_active": True,
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["name"] == "Omega 3"
    assert body["currency"] == "MXN"
    assert body["price_cents"] == 25900

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)


def test_list_products_returns_only_active() -> None:
    Base.metadata.create_all(bind=engine)
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    active_payload = {
        "name": "Vitamina C",
        "description": None,
        "price_cents": 19900,
        "currency": "MXN",
        "stock": 30,
        "is_active": True,
    }
    inactive_payload = {
        "name": "Producto oculto",
        "description": None,
        "price_cents": 9900,
        "currency": "MXN",
        "stock": 5,
        "is_active": False,
    }

    assert client.post("/api/v1/products", json=active_payload).status_code == 201
    assert client.post("/api/v1/products", json=inactive_payload).status_code == 201

    response = client.get("/api/v1/products")

    assert response.status_code == 200
    products = response.json()
    assert len(products) == 1
    assert products[0]["name"] == "Vitamina C"
    assert products[0]["is_active"] is True

    app.dependency_overrides.clear()
    Base.metadata.drop_all(bind=engine)
