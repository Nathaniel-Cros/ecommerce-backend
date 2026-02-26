# Ecommerce Backend Scaffold (Step 5)

Base ejecutable del backend con FastAPI + SQLAlchemy 2.0 y arquitectura hexagonal minima.

## Requisitos
- Python 3.12
- Docker y Docker Compose (opcional para Postgres local)

## Correr local (venv + pip)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx "psycopg[binary]"
```

Variables recomendadas:
```bash
export ENV=dev
export LOG_LEVEL=INFO
export DATABASE_URL="sqlite+pysqlite:///./dev.db"
```

Levantar servidor:
```bash
uvicorn app.main:app --reload
```

## Correr con docker-compose (Postgres)
Levantar base de datos:
```bash
docker compose up -d db
```

Usar Postgres desde la app local:
```bash
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ecomerce"
uvicorn app.main:app --reload
```

Detener servicios:
```bash
docker compose down
```

## API Versioning
- Rutas de dominio versionadas bajo `/api/v1`.
- Endpoints tecnicos fuera de versionado:
  - `GET /health`
  - `GET /db/ping`

## Estructura de rutas
- `app/shared/infrastructure/http/routes.py` centraliza el registro de rutas versionadas (`products`, `orders`) para mantener `app/main.py` limpio.

## Endpoints actuales
- `GET /health`
- `GET /db/ping`
- `POST /api/v1/products`
- `GET /api/v1/products`
- `POST /api/v1/orders`

## Ejemplos curl
```bash
curl http://127.0.0.1:8000/health
curl http://127.0.0.1:8000/db/ping
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Magnesio",
    "description": "Suplemento",
    "price_cents": 18900,
    "currency": "MXN",
    "stock": 12,
    "is_active": true
  }'
```

```bash
curl -X POST http://127.0.0.1:8000/api/v1/orders \
  -H "Content-Type: application/json" \
  -d '{
    "customer_name": "Juan Perez",
    "customer_phone": "5512345678",
    "items": [
      {"product_id": "PUT_PRODUCT_ID_HERE", "quantity": 2}
    ]
  }'
```

## Correr tests
```bash
pytest -q
```

## Migraciones
Alembic todavia no existe en este repo.

TODO (siguiente step):
- Crear setup de Alembic.
- Generar migraciones para `products`, `orders`, `order_items` y `payments`.

Nota: no se usa `Base.metadata.create_all` en runtime.
