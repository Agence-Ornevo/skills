---
to: "{ClientName} <{ClientEmail}>"
subject: "Approval needed: {TicketTitle}"
language: en
variables:
  - ClientName
  - ClientEmail
  - TicketTitle
  - LastContactDate
  - DirectURL
  - SLADeadline
---

Hi {ClientName},

Gentle nudge for approval on **{TicketTitle}** (pending since **{LastContactDate}**).

Direct link: {DirectURL}

If no feedback by **{SLADeadline}**, we'll treat current version as approved to keep the schedule on track.

Best,
Hernán Solano — Ornevo