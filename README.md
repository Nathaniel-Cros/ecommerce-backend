# Ecommerce Backend Scaffold (Step 4)

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
Levantar solo base de datos de desarrollo:
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

## Endpoints actuales
- `GET /health`
- `GET /db/ping`
- `POST /products`
- `GET /products` (solo activos)

Ejemplo rapido:
```bash
curl -X POST http://127.0.0.1:8000/products \
  -H "Content-Type: application/json" \
  -d '{
    "name": "Magnesio",
    "description": "Suplemento",
    "price_cents": 18900,
    "currency": "MXN",
    "stock": 12,
    "is_active": true
  }'

curl http://127.0.0.1:8000/products
```

## Correr tests
```bash
pytest -q
```

## Migraciones
Alembic todavia no existe en este repo.

TODO (step siguiente):
- Crear setup de Alembic.
- Generar primera migracion para la tabla `products`.

Nota temporal: en `ENV=dev` y `ENV=test`, la app crea tablas ORM al arrancar para facilitar pruebas locales.
