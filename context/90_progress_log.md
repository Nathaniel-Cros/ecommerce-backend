# 90 Progress Log

## [2026-02-19 23:48 CST aprox] Step 3 - Scaffold ejecutable FastAPI + Hexagonal base

### 1) Objetivo del step
Dejar el backend arrancando con FastAPI, configuracion por entorno, conexion DB (SQLAlchemy 2.0 sync), estructura hexagonal minima por contextos y tests base para `GET /health` y `GET /db/ping`.

### 2) Que se implemento
- Se creo la estructura `app/` con `shared` y `contexts/store/{products,orders}` en capas `domain`, `application`, `infrastructure/http`.
- Se implemento `app/main.py` con factory `create_app()`, inclusion de routers de products y orders, y endpoint global `GET /health`.
- Se implemento configuracion con `pydantic-settings` en `app/shared/config/settings.py`:
  - `DATABASE_URL`, `ENV`, `LOG_LEVEL`.
  - `get_settings()` con cache (`lru_cache`).
- Se implemento DB wiring sync en `app/shared/infrastructure/db/session.py`:
  - `engine`, `SessionLocal` y dependencia `get_db()` con cierre seguro de sesion.
- Se implemento ping DB en `app/shared/infrastructure/db/ping.py` con `SELECT 1`.
- Se implemento endpoint global `GET /db/ping` usando `Depends(get_db)` + `ping_db`.
- Se agregaron tests:
  - `tests/test_health.py` valida `200` y `{"status":"ok"}`.
  - `tests/test_db_ping.py` valida `200` y `{"db":"ok"}` con override de dependencia a SQLite in-memory.
- Se agrego `docker-compose.yml` para Postgres de desarrollo.
- Se agrego `README.md` con run local, docker-compose, tests y nota de alcance del step.
- Estado validado: `pytest -q` -> `2 passed`.

### 3) Archivos creados/modificados
- `README.md`
- `docker-compose.yml`
- `app/__init__.py`
- `app/main.py`
- `app/shared/__init__.py`
- `app/shared/config/__init__.py`
- `app/shared/config/settings.py`
- `app/shared/infrastructure/__init__.py`
- `app/shared/infrastructure/db/__init__.py`
- `app/shared/infrastructure/db/session.py`
- `app/shared/infrastructure/db/ping.py`
- `app/contexts/__init__.py`
- `app/contexts/store/__init__.py`
- `app/contexts/store/products/__init__.py`
- `app/contexts/store/products/domain/__init__.py`
- `app/contexts/store/products/application/__init__.py`
- `app/contexts/store/products/infrastructure/__init__.py`
- `app/contexts/store/products/infrastructure/http/__init__.py`
- `app/contexts/store/products/infrastructure/http/router.py`
- `app/contexts/store/orders/__init__.py`
- `app/contexts/store/orders/domain/__init__.py`
- `app/contexts/store/orders/application/__init__.py`
- `app/contexts/store/orders/infrastructure/__init__.py`
- `app/contexts/store/orders/infrastructure/http/__init__.py`
- `app/contexts/store/orders/infrastructure/http/router.py`
- `tests/conftest.py`
- `tests/test_health.py`
- `tests/test_db_ping.py`

### 4) Como correr
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install fastapi "uvicorn[standard]" sqlalchemy pydantic-settings pytest httpx "psycopg[binary]"
```

```bash
export ENV=dev
export LOG_LEVEL=INFO
export DATABASE_URL="sqlite+pysqlite:///./dev.db"
uvicorn app.main:app --reload
```

```bash
pytest -q
```

```bash
docker compose up -d db
export DATABASE_URL="postgresql+psycopg://postgres:postgres@localhost:5432/ecomerce"
uvicorn app.main:app --reload
```

### 5) Que revisar (checklist)
- [ ] `GET /health` responde `200` con `{"status":"ok"}`.
- [ ] `GET /db/ping` responde `200` con `{"db":"ok"}` usando DB configurada.
- [ ] `DATABASE_URL`, `ENV`, `LOG_LEVEL` cargan correctamente desde entorno.
- [ ] `pytest -q` pasa en local.
- [ ] No hay logica de negocio en controllers ni modelos de negocio creados aun.

### 6) Que sigue (next steps claros)
- Iniciar Step 4 con modelos de dominio + persistencia de ordenes/productos de forma minima.
- Preparar base de repositorios por puertos en capa domain/application y adapters SQLAlchemy en infraestructura.
- Implementar primer caso de uso de negocio: crear orden con validaciones base de estructura y snapshot.

### 7) Riesgos/Recomendaciones
- Riesgo: sin pin de dependencias puede haber drift entre ambientes.
- Riesgo: `DATABASE_URL` por default SQLite puede ocultar diferencias con Postgres.
- Recomendacion: agregar `requirements.txt` o lockfile en siguiente step.
- Recomendacion: definir convencion de errores de aplicacion antes de crecer endpoints.
- Recomendacion: mantener `db/ping` solo como healthcheck tecnico, no de negocio.

## Next Step Plan

### Step 4 - Modelos + repositorios + caso de uso create order
- Definir entidades/value objects minimos de `Order` y `OrderItem` (domain).
- Definir puertos de repositorio en domain y caso de uso `CreateOrderUseCase` en application.
- Implementar adaptador SQLAlchemy para repositorio de ordenes (infraestructura).
- Exponer endpoint HTTP minimo para crear orden (guest checkout base, sin pagos aun).
- Agregar pruebas unitarias del caso de uso y prueba de integracion basica del endpoint.

### Step 5 - Integracion Mercado Pago (preference + webhook idempotente)
- Definir puerto de pagos en domain/application y adaptador Mercado Pago en infraestructura.
- Crear preference/link de pago usando `external_reference` trazable por orden.
- Implementar webhook idempotente (clave de evento unica) con verificacion contra API MP.
- Aplicar transiciones de estado `Payment`/`Order` permitidas al confirmar `approved`.
- Agregar pruebas de idempotencia y reconciliacion minima de estado.
