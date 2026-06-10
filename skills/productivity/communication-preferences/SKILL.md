---
name: communication-preferences
description: Capture Hernán Solano's communication style and output preferences for consistent assistant behavior.
version: 1.0.0
author: Novum (assistant)
license: MIT
---

# Communication Preferences

## Language
- **English only** for all deliverables. No mixed-language output.
- If a source is in Spanish or French, translate the result into English before returning.

## Tone & Style
- **Direct, action‑oriented** – use bullet points and short sentences.
- Avoid fluff, unnecessary explanations, or filler phrases.
- Use tables for status updates; three‑column layout: *Item*, *Status*, *Notes*.
- **Concrete references**: When citing emails, always include **exact subject line and timestamp** (e.g., "email 53706, asunto 'Transferencia rubros pendientes...', 14:15 hrs").
- **Formal "usted" treatment** by default for legal/formal correspondence.
- **Friendly but firm tone** for legal responses — polite language, clear boundaries.
- **Mirror prior templates exactly** — reuse user's exact prior email structure/language unless instructed otherwise.
- **Remove mediation proposals** when user explicitly requests it.

## Recurring Context
- Code blocks must be fenced with triple backticks and include language identifiers.
- When presenting options, list up to three clear alternatives followed by a recommendation.
- Risks should be expressed as **Red/Yellow/Green** with mitigation steps.

## Recurring Context
- Remember these preferences across sessions; they belong in a persistent skill, not fleeting memory.
- When a user asks for a draft in Spanish or French, **first translate** to English, then provide the English version (the user can request a translation later).

## Usage
Load this skill in any session where output formatting matters:
```
/skill communication-preferences
```
Agents should consult this skill before generating any user‑facing text.
