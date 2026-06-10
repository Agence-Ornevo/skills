---
to: "{ClientName} <{ClientEmail}>"
subject: "Follow-up: {DealName} — Status Check"
language: en
variables:
  - ClientName
  - ClientEmail
  - DealName
  - LastContactDate
  - DaysStale
  - DirectURL
  - SLADeadline
---

Hi {ClientName},

Checking in on **{DealName}** — last contact was **{LastContactDate}** ({DaysStale} days ago).

Any questions or blockers on your side to move forward?

Happy to hop on a quick call this week if helpful. Direct link: {DirectURL}

If no feedback by **{SLADeadline}** (our SLA: 24h business hours), I'll treat this as paused.

Best,
Hernán Solano — Ornevo