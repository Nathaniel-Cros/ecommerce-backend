# 01 Architecture Rules

## Proposito
Acordar reglas no negociables para implementar arquitectura hexagonal (Ports and Adapters) en Python/FastAPI sin mezclar responsabilidades.

## Capas y responsabilidades
- Domain:
  - Entidades, value objects y puertos (interfaces).
  - Reglas de negocio puras.
  - Sin dependencias de FastAPI, SQLAlchemy ni Pydantic.
- Application:
  - Casos de uso (services) que orquestan Domain + puertos.
  - Manejo de transacciones/logica de flujo.
  - Sin detalles de framework o base de datos.
- Infrastructure:
  - Adaptadores: controladores HTTP FastAPI, repositorios SQLAlchemy, cliente Mercado Pago.
  - Mapeo entre modelos externos y objetos del dominio.

## Reglas clave
- Pydantic solo se usa en capa HTTP (request/response) y configuracion.
- SQLAlchemy solo se usa en infraestructura.
- Controllers no contienen logica de negocio; solo validan entrada, invocan caso de uso y formatean salida.
- Casos de uso no dependen de FastAPI ni de objetos ORM.
- Domain no importa nada de infraestructura.
- El versionado (`/api/v1`) se aplica SOLO en el punto de ensamblado (`register_routes`) y nunca dentro de routers de contexto.
- Excepcion tecnica: `GET /health` y `GET /db/ping` se exponen fuera de `/api/v1`.
- Evitar Redis/Celery/colas en MVP.

## Do / Don't
- Do: definir puertos en Domain para repositorios, pagos y clock/id providers.
- Do: inyectar implementaciones concretas desde Infrastructure hacia Application.
- Do: retornar objetos de dominio desde Application y traducir a DTO HTTP al final.
- Do: centralizar prefix de version en el agregador de rutas.
- Do: mantener `health` y `db/ping` sin versionado para monitoreo tecnico.
- Don't: usar `Session` de SQLAlchemy dentro de casos de uso.
- Don't: pasar modelos Pydantic al Domain.
- Don't: meter reglas de estados de orden/pago en routers.
- Don't: repetir `/api/v1` en cada router de contexto.

## Ejemplo breve
- Correcto:
  - `POST /checkout` -> Controller -> `CreateOrderUseCase` -> `OrderRepositoryPort` + `PaymentGatewayPort`.
- Incorrecto:
  - `POST /checkout` hace SQL directo en el router y llama Mercado Pago desde el mismo archivo.
