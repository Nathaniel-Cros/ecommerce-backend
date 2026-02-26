# 90 Progress Log

## [2026-02-25 21:41 CST aprox] Step 6 - Mercado Pago Checkout Pro (sin webhook)

### Objetivo
- Generar preference de Mercado Pago al crear orden con `payment_method=mercadopago`, persistir datos en `Payment` y devolver `payment_url`.

### Que se implemento
- Domain:
  - puerto `PaymentGateway` (Protocol).
  - `PaymentProviderResponse` (dataclass).
  - `Payment` extendido con `external_payment_id`, `init_point`, `sandbox_init_point`.
- Application:
  - `CreateOrderUseCase` recibe `PaymentGateway`.
  - soporte a `payment_method` (`cash` / `mercadopago`).
  - para `mercadopago`: crea preference, actualiza `Payment` a `pending` y guarda URLs/ID externos.
  - retorna `payment_url` en resultado del caso de uso.
- Infrastructure:
  - adapter `MercadoPagoGateway` en `orders/infrastructure/mercadopago/mercadopago_gateway.py` usando API HTTP sync.
  - `PaymentModel` y repositorio SQL actualizados para campos de provider.
- HTTP:
  - `POST /api/v1/orders` acepta `payment_method` enum y devuelve `payment_url`.
- Settings:
  - `MP_ACCESS_TOKEN`, `MP_PUBLIC_KEY`, `MP_WEBHOOK_URL`, `MP_ENVIRONMENT`.
- Testing:
  - tests de orders mockean `PaymentGateway` (sin llamadas reales a MP).
  - nuevos tests para `mercadopago` (con URL) y `cash` (sin URL).

### Notas
- Webhook de Mercado Pago no se implementa en este step.
- Se mantiene versionado de dominio en `/api/v1` y endpoints tecnicos fuera de versionado.

## [2026-02-25 21:07 CST aprox] Step 5 - Orders + OrderItems snapshot + Payment base

### Objetivo
- Implementar creacion de orden end-to-end con snapshot de items y modelo base de pago, respetando hexagonal.

### Que se implemento
- Dominio de orders:
  - `OrderItem` (snapshot obligatorio y `quantity > 0`)
  - `Order` (al menos 1 item, `total_cents` calculado, estados base)
  - `Payment` base (estados: `created|pending|approved|rejected|cancelled|refunded`)
  - `OrderRepository` como puerto (Protocol).
- Application:
  - `CreateOrderUseCase` con transaccion (`begin/commit/rollback`) y reglas:
    - valida items
    - consulta productos activos
    - construye snapshot de items
    - crea `Payment` en `created`
- Infrastructure:
  - modelos SQLAlchemy: `orders`, `order_items`, `payments`
  - `SQLOrderRepository` con mappers explicitos ORM <-> domain/projection.
- HTTP:
  - `POST /api/v1/orders` con request/response del step.
- Routing:
  - `app/shared/infrastructure/http/routes.py` centraliza import y ensamblado de rutas versionadas para mantener `main.py` limpio.
- Runtime/tests:
  - se removio `Base.metadata.create_all` de `main.py`.
  - tests usan schema SQLite explicito (`tests/sqlite_schema.py`) sin `create_all`.

### Archivos tocados
- Creados:
  - `app/contexts/store/orders/domain/order_item.py`
  - `app/contexts/store/orders/domain/order.py`
  - `app/contexts/store/orders/domain/payment.py`
  - `app/contexts/store/orders/domain/order_repository.py`
  - `app/contexts/store/orders/application/create_order.py`
  - `app/contexts/store/orders/infrastructure/order_models.py`
  - `app/contexts/store/orders/infrastructure/sql_order_repository.py`
  - `tests/sqlite_schema.py`
  - `tests/test_orders.py`
- Modificados:
  - `app/contexts/store/orders/infrastructure/http/router.py`
  - `app/shared/infrastructure/http/routes.py`
  - `app/main.py`
  - `tests/test_products.py`
  - `README.md`
  - `context/01_architecture_rules.md`
  - `context/90_progress_log.md`

### Notas
- Alembic no existe aun: pendiente crear migraciones reales para tablas nuevas.
- Endpoints tecnicos (`/health`, `/db/ping`) quedan fuera de `/api/v1`.

## [2026-02-20 13:26 CST aprox] Nota - Versionado centralizado `/api/v1`

- Qué se hizo:
  - Se centralizo el versionado en `register_routes` usando un router raiz con prefix `/api/v1`.
  - Se movieron `health` y `db/ping` al ensamblado versionado para que queden bajo `/api/v1`.
  - Se actualizaron pruebas y README con las rutas nuevas.
- Archivos tocados:
  - `app/shared/infrastructure/http/routes.py`
  - `app/main.py`
  - `tests/test_health.py`
  - `tests/test_db_ping.py`
  - `tests/test_products.py`
  - `README.md`
  - `context/01_architecture_rules.md`
  - `context/90_progress_log.md`
- Rutas afectadas:
  - `GET /health` -> `GET /api/v1/health`
  - `GET /db/ping` -> `GET /api/v1/db/ping`
  - `POST /products` -> `POST /api/v1/products`
  - `GET /products` -> `GET /api/v1/products`
- Recomendacion:
  - Mantener el versionado exclusivamente en el agregador (`register_routes`) y no repetir `/api/v1` en routers de contexto.

## [2026-02-20 13:26 CST aprox] Step 4 - Products end-to-end (hexagonal)

### Objetivo
- Implementar el primer contexto real (`Products`) en arquitectura hexagonal: dominio, casos de uso, adaptador SQLAlchemy, endpoints HTTP y pruebas.

### Qué se implementó
- Se creo entidad de dominio `Product` como `dataclass` con validaciones (`name`, `price_cents`, `stock`, `currency`).
- Se creo puerto `ProductRepository` como `Protocol`.
- Se crearon casos de uso en application:
  - `CreateProductUseCase` + `CreateProductCommand`
  - `ListActiveProductsUseCase`
- Se creo modelo ORM `ProductModel` (tabla `products`) con SQLAlchemy.
- Se creo adaptador `SQLProductRepository` con mapeo explicito ORM <-> Domain.
- Se implementaron endpoints:
  - `POST /products`
  - `GET /products` (solo activos)
- `app/main.py` se actualizo para incluir bootstrap temporal de schema en `ENV=dev/test` con `Base.metadata.create_all(...)` (mientras no exista Alembic).
- Se agrego `tests/test_products.py` con cobertura de create + list.
- `README.md` se actualizo a Step 4 con endpoints, ejemplos y nota de migraciones pendientes.

### Archivos creados/modificados
- Creados:
  - `app/contexts/store/products/domain/product.py`
  - `app/contexts/store/products/domain/product_repository.py`
  - `app/contexts/store/products/application/create_product.py`
  - `app/contexts/store/products/application/list_active_products.py`
  - `app/contexts/store/products/infrastructure/product_model.py`
  - `app/contexts/store/products/infrastructure/sql_product_repository.py`
  - `app/shared/infrastructure/db/base.py`
  - `tests/test_products.py`
- Modificados:
  - `app/contexts/store/products/infrastructure/http/router.py`
  - `app/main.py`
  - `README.md`

### Cómo probar manualmente
- Ejecutar app en local (SQLite):
```bash
source .venv/bin/activate
export ENV=dev
export LOG_LEVEL=INFO
export DATABASE_URL="sqlite+pysqlite:///./dev.db"
uvicorn app.main:app --reload
```
- Crear producto:
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
```
- Listar activos:
```bash
curl http://127.0.0.1:8000/products
```
- Nota `DATABASE_URL`:
  - Local app sin Docker DB: usar `localhost` o SQLite (`sqlite+pysqlite:///./dev.db`).
  - Si corres DB en `docker compose`: usar `postgresql+psycopg://postgres:postgres@localhost:5432/ecomerce`.
  - `@db:5432` aplica cuando la app corre dentro de la red de Docker, no en host local.

### Cómo correr tests
```bash
source .venv/bin/activate
pytest -q
```

### Qué revisar (checklist)
- [ ] Domain no depende de FastAPI/SQLAlchemy
- [ ] Application no depende de infraestructura
- [ ] Infra implementa puertos y mapea ORM <-> Domain
- [ ] Router no contiene lógica de negocio
- [ ] Tests cubren create + list

### Qué sigue (Next steps)
1) Step 5: Orders + OrderItems (snapshot) + Payment (modelo) + repos + caso de uso CreateOrder
2) Step 6: Mercado Pago preference (link) + persistencia mp_preference_id/init_point
3) Step 7: Webhook Mercado Pago con idempotencia + validación contra API + cambios de estado

### Recomendaciones / Riesgos (máx 5 bullets)
- Aun no hay Alembic; el schema se crea en startup solo para `dev/test`.
- `create_all` temporal puede ocultar drift respecto a migraciones reales futuras.
- `@app.on_event("startup")` muestra warning deprecado (migrar a lifespan mas adelante).
- Mantener `DATABASE_URL` correcto por modo de ejecucion para evitar errores de conexion.
- Agregar pruebas de integracion con Postgres cuando exista flujo de migraciones.

## [2026-02-20 13:17 CST aprox] Step 3 - Scaffold hexagonal + `/health` + `/db/ping`

### 1) Objetivo del step
Levantar la base ejecutable del backend con FastAPI, configuracion por entorno y conexion DB sync, dejando endpoints tecnicos de salud.

### 2) Que se implemento
- Estructura inicial hexagonal en `app/` con `shared` y `contexts/store`.
- `app/main.py` con app factory, routers y endpoint `GET /health`.
- Configuracion central con `pydantic-settings` (`DATABASE_URL`, `ENV`, `LOG_LEVEL`).
- Wiring de SQLAlchemy 2.0 sync (`engine`, `SessionLocal`, `get_db`).
- `ping_db(session)` con `SELECT 1` y endpoint `GET /db/ping`.
- Tests base para `/health` y `/db/ping`.
- `docker-compose.yml` para Postgres en desarrollo.

### 3) Archivos creados/modificados
- `README.md`
- `docker-compose.yml`
- `app/main.py`
- `app/shared/config/settings.py`
- `app/shared/infrastructure/db/session.py`
- `app/shared/infrastructure/db/ping.py`
- `app/contexts/store/products/infrastructure/http/router.py`
- `app/contexts/store/orders/infrastructure/http/router.py`
- `tests/test_health.py`
- `tests/test_db_ping.py`
- `tests/conftest.py`

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
- [ ] `GET /db/ping` responde `200` con `{"db":"ok"}`.
- [ ] `DATABASE_URL`, `ENV` y `LOG_LEVEL` cargan por entorno.
- [ ] `pytest -q` pasa en local.
- [ ] Controllers sin logica de negocio.

### 6) Que sigue (next steps claros)
- Introducir modelos de dominio y puertos de repositorio.
- Implementar primer caso de uso real de negocio.
- Agregar migraciones con Alembic.

### 7) Riesgos/Recomendaciones
- Sin lockfile, hay riesgo de drift de dependencias entre entornos.
- SQLite local puede ocultar diferencias frente a Postgres.
- Definir convencion de errores de aplicacion antes de crecer endpoints.
- Mantener `/db/ping` como healthcheck tecnico, no funcional.
- Priorizar Alembic antes de ampliar entidades.

## Next Step Plan

### Step 4: modelos + repositorios + caso de uso create order
- Definir entidades `Order` y `OrderItem` en dominio.
- Definir puertos de repositorio y `CreateOrderUseCase` en application.
- Implementar adaptador SQLAlchemy para ordenes.
- Exponer endpoint minimo para crear orden (guest checkout base).
- Agregar pruebas unitarias del caso de uso y prueba de integracion.

### Step 5: integracion Mercado Pago (preference + webhook idempotente)
- Definir puerto de pagos y adaptador Mercado Pago.
- Crear preference/link con `external_reference` trazable.
- Implementar webhook idempotente con verificacion contra API de Mercado Pago.
- Aplicar transiciones validas de `Payment` y `Order`.
- Agregar pruebas de idempotencia y reconciliacion de estado.
