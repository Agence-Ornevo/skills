---
to: "{ClientName} <{ClientEmail}>"
subject: "Re: {OriginalSubject} — Tu mensaje del {LastContactDate}"
language: es
variables:
  - ClientName
  - ClientEmail
  - OriginalSubject
  - LastContactDate
  - ResponseDraft
  - SLADeadline
---

Hola {ClientName},

Disculpa la demora en responder. Tu mensaje del **{LastContactDate}** ha sido recibido.

{ResponseDraft}

Quedo a disposición para lo que necesites.

Saludos,
Hernán Solano — Ornevo