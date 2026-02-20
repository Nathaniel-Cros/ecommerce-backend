from collections.abc import Generator

from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.main import app
from app.shared.infrastructure.db.session import get_db


engine = create_engine(
    "sqlite+pysqlite:///:memory:",
    future=True,
    connect_args={"check_same_thread": False},
)
TestingSessionLocal = sessionmaker(bind=engine, class_=Session, autoflush=False, autocommit=False)


def override_get_db() -> Generator[Session, None, None]:
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_db_ping_returns_ok() -> None:
    app.dependency_overrides[get_db] = override_get_db
    client = TestClient(app)

    response = client.get("/db/ping")

    assert response.status_code == 200
    assert response.json() == {"db": "ok"}

    app.dependency_overrides.clear()
