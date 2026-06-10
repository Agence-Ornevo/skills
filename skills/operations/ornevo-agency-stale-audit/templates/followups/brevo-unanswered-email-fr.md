---
to: "{ClientName} <{ClientEmail}>"
subject: "Re: {OriginalSubject} — Votre message du {LastContactDate}"
language: fr
variables:
  - ClientName
  - ClientEmail
  - OriginalSubject
  - LastContactDate
  - ResponseDraft
  - SLADeadline
---

Bonjour {ClientName},

Toutes mes excuses pour le délai de réponse. Votre message du **{LastContactDate}** a bien été reçu.

{ResponseDraft}

Je reste à disposition pour tout complément.

Cordialement,
Hernán Solano — Ornevo