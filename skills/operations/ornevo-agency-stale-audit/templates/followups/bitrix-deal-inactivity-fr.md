---
to: "{ClientName} <{ClientEmail}>"
subject: "Relance : {DealName} — Point d'étape"
language: fr
variables:
  - ClientName
  - ClientEmail
  - DealName
  - LastContactDate
  - DaysStale
  - DirectURL
  - SLADeadline
---

Bonjour {ClientName},

Je fais un point sur **{DealName}** — notre dernier échange date du **{LastContactDate}** ({DaysStale} jours).

Y a-t-il des questions ou blocages côté **{ClientName}** pour avancer ?

Disponible pour un appel court cette semaine si utile. Lien direct vers le dossier : {DirectURL}

Sans retour de votre part d'ici le **{SLADeadline}** (notre SLA : 24h ouvrées), je considérerai que le dossier est en pause.

Cordialement,
Hernán Solano — Ornevo