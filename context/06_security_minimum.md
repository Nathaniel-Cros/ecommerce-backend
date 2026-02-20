# 06 Security Minimum

## Proposito
Definir reglas minimas de seguridad para el MVP, con foco en evitar fugas de datos, configuraciones inseguras y errores comunes en API y pagos.

## Seccion 1: Configuracion segura
- Nunca hardcodear secrets en codigo, tests o scripts.
- Usar variables de entorno para credenciales, tokens y llaves.
- No subir `.env` ni archivos derivados (`.env.*`) al repositorio.
- Separar configuracion por entorno: `dev`, `test`, `prod`.
- Validar que variables criticas existan al arrancar la app.

## Seccion 2: API Security
- Validar siempre input HTTP con Pydantic (request models).
- No exponer stack traces en produccion.
- Limitar CORS explicitamente a dominios permitidos.
- No permitir `DEBUG=true` en produccion.
- Validar webhook consultando API de Mercado Pago antes de actualizar estados.

## Seccion 3: Base de datos
- No usar raw SQL sin parametros.
- Siempre usar transacciones para operaciones de negocio.
- Controlar integridad referencial con claves foraneas y restricciones.
- Definir constraints para evitar duplicados criticos (ej. external_reference unico por intento).

## Seccion 4: Pagos
- No guardar datos de tarjeta (PAN, CVV, fecha completa, token sensible).
- Verificar estado del pago consultando Mercado Pago (no confiar solo en payload webhook).
- Implementar idempotencia en webhooks para evitar doble procesamiento.
- Comparar monto y `external_reference` contra datos esperados de la orden.
- Solo marcar orden como pagada si el estado en MP es `approved`.

## Seccion 5: Logging
- No loggear tokens, secretos ni headers sensibles.
- No loggear informacion sensible de cliente innecesaria.
- Usar IDs de correlacion para trazabilidad sin exponer datos privados.
- Adoptar logging estructurado en fases futuras.
