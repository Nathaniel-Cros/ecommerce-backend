# 03 Coding Guidelines

## Proposito
Definir estandares de codigo para mantener legibilidad, testabilidad y coherencia del proyecto.

## Reglas tecnicas
- Python 3.12 con type hints obligatorios en dominio y aplicacion.
- SQLAlchemy 2.0 solo en infraestructura.
- Pydantic v2 solo en HTTP/config.
- Alembic para todo cambio de esquema.
- Evitar utilitarios globales con estado mutable.

## Estructura y nombrado
- Modulos por contexto de negocio, no por tipo tecnico gigante.
- Casos de uso con nombres de accion: `CreateOrderUseCase`, `ConfirmPaymentUseCase`.
- Puertos con sufijo `Port`.
- Adaptadores con sufijo explicito: `SqlAlchemyOrderRepository`, `MercadoPagoPaymentGateway`.

## Calidad minima
- Cada caso de uso debe tener pruebas unitarias.
- Flujos criticos de pago deben tener pruebas de integracion.
- Validar transiciones de estado con reglas explicitas, no condicionales dispersos.
- Logging estructurado en eventos de negocio clave.

## Do / Don't
- Do: mantener funciones pequenas con una sola responsabilidad.
- Do: capturar errores de infraestructura y mapearlos a errores de aplicacion.
- Do: escribir tests para reglas de estados y idempotencia.
- Don't: mezclar ORM entities con entidades de dominio.
- Don't: duplicar reglas de negocio en varios endpoints.
- Don't: usar constantes magicas; centralizar estados y codigos.

## Ejemplo breve
- Correcto:
  - `ConfirmPaymentUseCase` recibe `payment_id` y usa puertos para consultar gateway y persistir cambios.
- Incorrecto:
  - Endpoint FastAPI cambia estados de orden directamente con SQL y sin validar transiciones.
