# 02 Business Rules

## Proposito
Documentar reglas de negocio operativas del e-commerce para mantener consistencia entre API, base de datos y procesos manuales.

## Reglas generales
- Toda compra crea una orden, aunque el pago falle.
- El estado de pago se confirma por webhook + verificacion contra API de Mercado Pago.
- En MVP solo hay pickup, no envios.
- Checkout sin cuenta: solicitar solo datos necesarios para contacto y entrega en pickup.

## Estados permitidos de Order
- `PENDING_PAYMENT`: orden creada, esperando pago.
- `PAID`: pago confirmado.
- `READY_FOR_PICKUP`: pedido preparado y listo para recoger.
- `PICKED_UP`: pedido entregado al cliente.
- `CANCELLED`: orden cancelada por operacion o timeout.
- `EXPIRED`: orden vencida por falta de pago en tiempo definido.

## Transiciones validas de Order
- `PENDING_PAYMENT` -> `PAID`
- `PENDING_PAYMENT` -> `CANCELLED`
- `PENDING_PAYMENT` -> `EXPIRED`
- `PAID` -> `READY_FOR_PICKUP`
- `PAID` -> `CANCELLED` (solo casos excepcionales)
- `READY_FOR_PICKUP` -> `PICKED_UP`
- `READY_FOR_PICKUP` -> `CANCELLED` (caso excepcional documentado)

## Estados permitidos de Payment
- `INITIATED`: intento de pago creado localmente.
- `PENDING`: Mercado Pago reporta pago en proceso.
- `APPROVED`: pago acreditado.
- `REJECTED`: pago rechazado.
- `CANCELLED`: pago cancelado.
- `REFUNDED`: pago devuelto total o parcialmente.

## Transiciones validas de Payment
- `INITIATED` -> `PENDING`
- `INITIATED` -> `APPROVED`
- `INITIATED` -> `REJECTED`
- `PENDING` -> `APPROVED`
- `PENDING` -> `REJECTED`
- `APPROVED` -> `REFUNDED`
- `INITIATED` -> `CANCELLED`
- `PENDING` -> `CANCELLED`

## Reglas de consistencia Order vs Payment
- `Order.PAID` solo si existe `Payment.APPROVED` verificado.
- Si `Payment.REJECTED` o `Payment.CANCELLED`, la orden se mantiene o regresa a `PENDING_PAYMENT` segun politica activa.
- `Order.PICKED_UP` requiere `Order.PAID` previo.

## Ejemplo breve
- Si llega webhook con pago `approved`, se valida en API Mercado Pago y se pasa:
  - `Payment` a `APPROVED`
  - `Order` a `PAID`
