---
to: "{ClientName} <{ClientEmail}>"
subject: "Seguimiento: {DealName} — Punto de situación"
language: es
variables:
  - ClientName
  - ClientEmail
  - DealName
  - LastContactDate
  - DaysStale
  - DirectURL
  - SLADeadline
---

Hola {ClientName},

Hago seguimiento de **{DealName}** — último contacto el **{LastContactDate}** (hace {DaysStale} días).

¿Alguna duda o bloqueo por vuestra parte para avanzar?

Disponible para una llamada breve esta semana si ayuda. Enlace directo: {DirectURL}

Sin respuesta para el **{SLADeadline}** (nuestro SLA: 24h hábiles), consideraré el dossier en pausa.

Saludos,
Hernán Solano — Ornevo