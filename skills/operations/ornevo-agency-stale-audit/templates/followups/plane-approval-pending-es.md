---
to: "{ClientName} <{ClientEmail}>"
subject: "Aprobación pendiente: {TicketTitle}"
language: es
variables:
  - ClientName
  - ClientEmail
  - TicketTitle
  - LastContactDate
  - DirectURL
  - SLADeadline
---

Hola {ClientName},

Recordatorio suave para la aprobación de **{TicketTitle}** (pendiente desde el **{LastContactDate}**).

Enlace directo: {DirectURL}

Sin respuesta para el **{SLADeadline}**, consideraremos la versión actual aprobada para cumplir el cronograma.

Saludos,
Hernán Solano — Ornevo