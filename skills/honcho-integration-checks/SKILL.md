---
name: honcho-integration-checks
description: Verify self-hosted Honcho integration with Hermes end-to-end, not just health.
version: 0.2.0
---

# Honcho Integration Checks

Use this when the user asks whether Honcho is correctly integrated with Hermes, or when an integration needs verification after changes.

## Rule

Never report "integrated" from health alone. Health only proves the service is up. Integration requires proving that Hermes tools actually reach Honcho and return meaningful results.

## Required verification sequence

1. `honcho_profile` for the expected peer. If the service is unreachable, this will fail fast.
2. `honcho_context` for recent messages tied to that peer. If this returns an empty or truncated-only result, that is already a signal.
3. `honcho_search` for a topic known to exist in recent context. Use a concrete query string that should match recent material.
4. `honcho_reasoning` for a synthesis question about known recent material.

## Interpreting results

| Check | Minimum pass condition |
|---|---|
| profile | returns facts or a peer card; if absent on <3.x, note version expectation |
| context | returns recent messages coherently, not only dashed/capitalized fragments |
| search | finds at least one relevant hit on the chosen query |
| reasoning | returns a synthesized answer, not "No result from Honcho." |

If any required layer is empty when content clearly exists, classify the integration as **partial**, not working.

## Partial-integration pattern

When `/health` is `{"status":"ok"}` but `search` and `reasoning` are empty while `context` is populated, the likely cause is embeddings/LLM auth, not transport. Do not report integration as healthy in this state.

Key discriminator: LLM path errors include `Missing Authentication header`; embeddings path errors include `Incorrect API key provided` with retries. Both often point to placeholder/env values instead of real credentials.

## Deriver Embedding Requirement (CRITICAL)

The Honcho deriver's `save_representation()` **always** embeds observations before saving them to the database — it does NOT respect `EMBED_MESSAGES=false`. That setting only controls the background reconciler's message embedding, not the deriver's observation embedding.

**Consequence:** If the embedding provider is not configured with a valid key, `save_representation()` fails silently for every observation batch. The deriver log shows:
- LLM call succeeding (observations generated: N count)
- Then immediately: `Failed to save representation for observer <id>: Error code: 401 - Incorrect API key provided`
- All queue items marked `processed=true` with error, zero documents in DB

**OpenRouter does NOT support embeddings.** This is the #1 pitfall when running Honcho with OpenRouter free models. Confirmed: OpenRouter returns 401 on `/v1/embeddings` for all model names.

**Solutions (pick one):**
1. **Gemini AI Studio key (free tier)** — Set `EMBEDDING_MODEL_CONFIG__TRANSPORT=gemini` and `GEMINI_API_KEY=<key>` in `~/honcho/.env`. See `references/gemini-embedding-setup.md` for full setup.
2. **Real OpenAI key** — Set `OPENAI_API_KEY=<real-openai-key>` (not an OpenRouter key).
3. **Local embedding model** — Install `sentence-transformers` in the deriver container (complex, slow).

**Gemini API Key Format (CRITICAL):** Only Google AI Studio keys (`AIza...`, ~39 chars) work from Python. Cloud API keys (`AQ...`, ~55 chars) FAIL with `API_KEY_INVALID` from Python HTTP clients and the `google-genai` SDK. Get a key at https://aistudio.google.com/app/apikey.

## Token Truncation Patches Required for Gemini

Two source patches are needed on the HOST (`~/honcho/src/`) before rebuilding the deriver container:

1. **`representation.py`** (line ~100): Truncate observation texts to 8192 tokens before embedding
2. **`embedding_client.py`** (line ~169): Change Gemini token cap from 2048 to 8192

See `references/gemini-embedding-setup.md` for the exact code patches.

## Docker Source Patching Workflow

When patching Honcho source files:

1. **Modify source on the HOST** at `~/honcho/src/` (not inside the running container)
2. **Rebuild:** `docker compose build --force-recreate deriver`
3. **Verify:** `docker exec honcho-deriver-1 grep -n "your_change" /app/src/file.py`

**Why:** Container file changes are lost on rebuild. The Docker image is built from `~/honcho/src/`.

**`docker compose restart` does NOT pick up changes.** Always use `--force-recreate`. For source changes, use `--build --force-recreate`.

## Diagnostic Commands

**Check if documents exist:**
```bash
docker exec honcho-database-1 psql -U postgres -c "SELECT COUNT(*) FROM documents;"
# If 0 and messages > 0, the deriver is failing on embeddings
```

**Check for failed queue items:**
```bash
docker exec honcho-database-1 psql -U postgres -c "SELECT COUNT(*) FROM queue WHERE task_type='representation' AND error IS NOT NULL;"
# If > 0 and documents = 0, all saves failed (likely embedding 401)
```

**Distinguish LLM vs embedding 401:**
- `Missing Authentication header` → LLM call (OpenRouter key issue)
- `Incorrect API key provided: sk-...` → Embedding call (embedding key issue)

**Reset failed queue items after fixing config:**
```bash
docker exec honcho-database-1 psql -U postgres -c "UPDATE queue SET processed=false, error=NULL WHERE task_type='representation' AND error IS NOT NULL;"
```

**Verify env vars in container:**
```bash
docker exec honcho-deriver-1 python3 -c "import os; print(os.environ.get('GEMINI_API_KEY','MISSING')[:8])"
```

## Hermes-side reproducer

When treating like a bug, prefer this order:

1. confirm docker service state and port,
2. probe the same cues from a fresh Hermes session,
3. do not make setup changes during verification, do not change `.env` values during verification; report state only.