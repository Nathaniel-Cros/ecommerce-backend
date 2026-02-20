# 07 Critical Bug Prevention

## Proposito
Definir reglas operativas para prevenir fallos criticos de negocio: ordenes duplicadas, webhooks repetidos, stock inconsistente y transiciones invalidas.

## Riesgos criticos a prevenir
- Duplicacion de ordenes por reintentos de checkout.
- Doble procesamiento de webhook.
- Desincronizacion de stock por concurrencia.
- Cambios de estado invalidos en `Order` y `Payment`.
- Corrupcion de snapshot de precios.
- Race conditions basicas en operaciones concurrentes.

## Validaciones obligatorias antes de cambiar estado
- Verificar estado actual y transicion permitida.
- Verificar version o lock de registro (control optimista o pesimista).
- Verificar existencia de entidad relacionada (`Order`, `Payment`, `Product`).
- Verificar monto y moneda esperados para pagos.
- Verificar `external_reference` esperado.
- Verificar que el evento webhook no haya sido procesado antes.
- Verificar disponibilidad de stock antes de reservar o confirmar.
- Verificar que snapshot de precio exista y no se reescriba tras crear orden.

## Reglas de transicion permitidas (tabla)
| Entidad | Estado actual | Estado siguiente permitido |
| --- | --- | --- |
| Order | PENDING_PAYMENT | PAID, CANCELLED, EXPIRED |
| Order | PAID | READY_FOR_PICKUP, CANCELLED |
| Order | READY_FOR_PICKUP | PICKED_UP, CANCELLED |
| Order | PICKED_UP | (sin transicion) |
| Order | CANCELLED | (sin transicion) |
| Order | EXPIRED | (sin transicion) |
| Payment | INITIATED | PENDING, APPROVED, REJECTED, CANCELLED |
| Payment | PENDING | APPROVED, REJECTED, CANCELLED |
| Payment | APPROVED | REFUNDED |
| Payment | REJECTED | (sin transicion) |
| Payment | CANCELLED | (sin transicion) |
| Payment | REFUNDED | (sin transicion) |

## Ejemplo conceptual de idempotencia
- Evento webhook recibido: `payment.updated:555`.
- Clave idempotente interna: `topic=payment.updated + resource_id=555`.
- Si la clave no existe: procesar, persistir resultado, guardar clave.
- Si la clave ya existe: responder `200 OK` sin reprocesar.

## Buenas practicas de transacciones
- Usar una sola transaccion atomica para actualizar `Payment`, `Order` y movimiento de stock relacionado.
- Aplicar `SELECT ... FOR UPDATE` o mecanismo equivalente en filas criticas.
- Mantener transacciones cortas (sin llamadas externas dentro).
- Consultar API externa (Mercado Pago) antes de abrir transaccion critica cuando sea posible.
- Hacer commit solo cuando todas las validaciones pasen.
- Hacer rollback explicito ante cualquier error de negocio o persistencia.

## Reglas especificas anti-bugs
- Ordenes: generar `idempotency_key` por intento de checkout y constraint unico.
- Webhooks: almacenar eventos procesados con indice unico.
- Stock: descontar con control transaccional y nunca con lecturas stale fuera de lock.
- Snapshot de precio: congelar precio unitario al crear orden; nunca recalcular historico.
- Estados: centralizar transiciones en dominio/aplicacion, nunca en controller.
