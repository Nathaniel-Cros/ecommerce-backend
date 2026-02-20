# 05 Scope and Roadmap

## Proposito
Definir alcance por fases para entregar valor rapido sin perder base tecnica para evolucion futura.

## Principios de alcance
- Entregar MVP completo extremo a extremo antes de optimizaciones.
- Posponer complejidad que no aporte al objetivo actual.
- Mantener decisiones reversibles cuando sea posible.

## Fase MVP
Objetivo: vender productos y cobrar consultas con flujo estable.

Incluye:
- Catalogo de productos.
- Checkout invitado (sin cuentas).
- Ordenes con pickup.
- Admin basico para ver ordenes y estado.
- Integracion inicial de links de pago Mercado Pago.

No incluye:
- Envio a domicilio.
- Programa de lealtad.
- Automatizaciones complejas.

## Fase V2
Objetivo: robustecer operacion y confiabilidad de pagos.

Incluye:
- Webhook completo Mercado Pago.
- Sincronizacion y reconciliacion de estados de pago/orden.
- Reglas de stock mas estrictas.
- Mejoras de trazabilidad y auditoria.

## Fase V3
Objetivo: expandir capacidades comerciales.

Incluye (opcional/priorizable):
- Cuentas de usuario para historial y recompra.
- Envio a domicilio y gestion de direcciones.
- Metodos de pago adicionales.
- Mejoras de panel admin (reportes, filtros, exportaciones).

## Criterios de avance por fase
- MVP -> V2:
  - tasa de ordenes completadas estable.
  - cero inconsistencias criticas de estado en pagos.
- V2 -> V3:
  - operacion diaria confiable sin intervencion manual excesiva.
  - necesidad comercial valida para nuevas capacidades.

## Ejemplo breve de priorizacion
- Si hay conflicto entre "cuentas de usuario" y "webhook confiable", priorizar webhook confiable (V2).
