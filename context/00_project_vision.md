# 00 Project Vision

## Proposito
Definir una vision comun para construir un e-commerce simple, robusto y mantenible para productos naturales de consultorio en Mexico.

## Objetivo del proyecto
- Entregar un MVP funcional para portafolio y aprendizaje serio de Python backend.
- Permitir venta de productos y cobro de consultas por link de pago.
- Priorizar claridad de arquitectura sobre velocidad de hacks.

## Alcance inicial
- Venta de productos naturales.
- Checkout como invitado (sin cuentas de cliente).
- Metodo de entrega inicial: solo recoleccion en punto de pickup.
- Pagos con Mercado Pago (links, QR o Point segun caso).
- Confirmacion de pago por webhook (no por redireccion del cliente).

## Principios del producto
- Flujo corto: descubrir, pagar, confirmar, recoger.
- Estado confiable: lo que se muestra al cliente debe venir de estados reales persistidos.
- Trazabilidad: cada orden y pago debe poder auditarse.
- MVP sin sobreingenieria: evitar servicios extra no esenciales.

## Criterios de exito (MVP)
- Se puede crear una orden y generar intento de pago.
- Se puede confirmar pago de forma segura por webhook.
- El admin puede ver ordenes y estado de pago.
- El flujo de pickup queda claro para cliente y operacion.

## Ejemplo breve de flujo
1. Cliente agrega productos al carrito.
2. Cliente confirma datos minimos y selecciona pickup.
3. Sistema crea `Order` en `PENDING_PAYMENT`.
4. Sistema genera link de Mercado Pago.
5. Webhook confirma pago y actualiza a `PAID`.
6. Admin prepara pedido y marca `READY_FOR_PICKUP`.
