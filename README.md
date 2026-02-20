# Ecommerce Backend Scaffold (Step 3)

Base ejecutable del backend con FastAPI + SQLAlchemy 2.0 y estructura hexagonal minima (Ports and Adapters).

## Requisitos
- Python 3.12
- Docker y Docker Compose (opcional para Postgres local)

## Correr local (venv + pip)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx psycopg[binary]
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

## Correr tests
```bash
pytest -q
```

Nota de tests: `test_db_ping.py` usa SQLite in-memory por override de dependencia para mantener pruebas rapidas y aisladas.

## Estado del proyecto
Este step solo prepara la base del backend; los modelos de negocio y migraciones vienen en el siguiente step.

## TODO (siguiente step)
- Integrar Alembic para migraciones SQLAlchemy.
- Crear modelos de negocio (products, orders, payments).
