---
to: "{ClientName} <{ClientEmail}>"
subject: "⚠️ Alerta técnica: Envíos de formulario {FormName}"
language: es
variables:
  - ClientName
  - ClientEmail
  - FormName
  - ErrorSinceDate
  - FailureCount
  - EstimatedFixHours
  - SLADeadline
---

Hola {ClientName},

Nuestros sistemas detectan errores en el webhook **{FormName}** desde el **{ErrorSinceDate}** ({FailureCount} fallos).

Los envíos de clientes no se procesan correctamente.

El equipo técnico investiga — solución estimada en **{EstimatedFixHours}h**.

Os mantendremos informados.

Saludos,
Hernán Solano — Ornevo