# 04 Payment Strategy Mercado Pago

## Proposito
Definir una estrategia de pago segura y confiable para links/QR/Point con confirmacion robusta por webhook.

## Canales de pago (MVP)
- Link de pago para checkout e-commerce.
- QR/Point para casos de cobro presencial de consulta.
- Unificar el modelo interno de `Payment` para todos los canales.

## external_reference (obligatorio)
- Usar `external_reference` unico por intento de pago.
- Formato recomendado: `<tipo>:<entidad_id>:<intento>`.
- Ejemplos:
  - `order:123:1`
  - `consultation:987:2`
- Debe permitir rastrear de forma directa el pago hacia orden o consulta.

## Idempotencia
- Al crear pagos/preferencias, enviar `X-Idempotency-Key` unico por solicitud.
- Guardar clave de idempotencia y resultado local para evitar duplicados por reintentos.
- Webhooks se procesan de forma idempotente:
  - registrar `event_id` o combinacion `topic + resource_id`.
  - si el evento ya fue procesado, responder 200 sin reprocesar.

## Flujo webhook seguro
1. Recibir webhook y validar estructura minima.
2. Extraer identificador de pago/notificacion.
3. Consultar API de Mercado Pago para estado real del pago.
4. No confiar solo en payload del webhook.
5. Verificar:
   - `external_reference` esperado.
   - monto y moneda esperados.
   - estado real del pago en Mercado Pago.
6. Actualizar `Payment` y `Order` con transicion valida e idempotente.
7. Responder 200 rapido tras persistir resultado.

## Seguridad y datos sensibles
- No guardar datos de tarjeta (PAN, CVV, vencimiento).
- No loggear tokens secretos ni datos personales innecesarios.
- Guardar solo metadata necesaria para conciliacion:
  - `payment_id` de Mercado Pago
  - `external_reference`
  - estado
  - monto
  - timestamps

## Reglas operativas
- Solo `APPROVED` confirmado por API cambia orden a `PAID`.
- `PENDING` no habilita preparacion de pedido.
- Rechazos y cancelaciones deben quedar auditados con razon disponible.

## Ejemplo breve
- Llega webhook de `payment.updated` con id `555`.
- Sistema consulta `GET /v1/payments/555`.
- Si API responde `approved` y `external_reference=order:123:1`, se confirma orden `123` como `PAID`.
