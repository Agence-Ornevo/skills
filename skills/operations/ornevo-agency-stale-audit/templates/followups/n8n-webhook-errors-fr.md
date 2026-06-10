---
to: "{ClientName} <{ClientEmail}>"
subject: "⚠️ Alerte technique : Soumissions de formulaire {FormName}"
language: fr
variables:
  - ClientName
  - ClientEmail
  - FormName
  - ErrorSinceDate
  - FailureCount
  - EstimatedFixHours
  - SLADeadline
---

Bonjour {ClientName},

Nos systèmes détectent des erreurs sur le webhook **{FormName}** depuis le **{ErrorSinceDate}** ({FailureCount} échecs).

Les soumissions clients ne sont pas traitées correctement.

Notre équipe technique investigate et corrige — résolution estimée sous **{EstimatedFixHours}h**.

Nous vous tiendrons informés.

Cordialement,
Hernán Solano — Ornevo