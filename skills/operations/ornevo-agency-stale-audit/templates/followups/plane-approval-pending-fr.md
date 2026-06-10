---
to: "{ClientName} <{ClientEmail}>"
subject: "Validation attendue : {TicketTitle}"
language: fr
variables:
  - ClientName
  - ClientEmail
  - TicketTitle
  - LastContactDate
  - DirectURL
  - SLADeadline
---

Bonjour {ClientName},

Relance douce pour la validation de **{TicketTitle}** (en attente depuis le **{LastContactDate}**).

Lien direct : {DirectURL}

Sans retour de votre part d'ici le **{SLADeadline}**, nous considérerons la version actuelle comme validée pour respecter le planning.

Cordialement,
Hernán Solano — Ornevo