---
to: "{ClientName} <{ClientEmail}>"
subject: "⚠️ Technical Alert: {FormName} Form Submissions"
language: en
variables:
  - ClientName
  - ClientEmail
  - FormName
  - ErrorSinceDate
  - FailureCount
  - EstimatedFixHours
  - SLADeadline
---

Hi {ClientName},

Our systems detect errors on webhook **{FormName}** since **{ErrorSinceDate}** ({FailureCount} failures).

Client submissions are not being processed correctly.

Engineering is investigating — estimated fix within **{EstimatedFixHours}h**.

Will keep you updated.

Best,
Hernán Solano — Ornevo