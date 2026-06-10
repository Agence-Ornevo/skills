---
to: "{ClientName} <{ClientEmail}>"
subject: "Re: {OriginalSubject} — Your message from {LastContactDate}"
language: en
variables:
  - ClientName
  - ClientEmail
  - OriginalSubject
  - LastContactDate
  - ResponseDraft
  - SLADeadline
---

Hi {ClientName},

Apologies for the delayed response. Your message from **{LastContactDate}** was received.

{ResponseDraft}

Let me know if you need anything else.

Best,
Hernán Solano — Ornevo