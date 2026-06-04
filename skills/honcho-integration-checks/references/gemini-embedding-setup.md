# Gemini Embedding Setup for Honcho

## CRITICAL: Key Format Matters

**Only Google AI Studio keys work from Python.** Cloud API keys (`AQ...` format) FAIL with `API_KEY_INVALID` from Python HTTP clients and the `google-genai` SDK. Only AI Studio keys (`AIza...` ~39 chars) work.

| Key Type | Format | Works from Python? | Works from curl? |
|----------|--------|-------------------|------------------|
| Google AI Studio | `AIza...` (~39 chars) | YES | YES |
| Google Cloud API key | `AQ...` (~55 chars) | NO (400 API_KEY_INVALID) | YES |

**Root cause:** Python's `urllib`/`httpx`/`requests` send `X-goog-api-key` header differently than curl. The `google-genai` SDK uses `Authorization: Bearer` which also fails for Cloud keys.

## Setup

1. Get key from https://aistudio.google.com/app/apikey (AI Studio, NOT Cloud Console)
2. Add to `~/honcho/.env`:
   ```
   EMBED_MESSAGES=true
   EMBEDDING_MODEL_CONFIG__TRANSPORT=gemini
   EMBEDDING_MODEL_CONFIG__MODEL=gemini/text-embedding-004
   GEMINI_API_KEY=<your-AIza-key>
   ```
3. Rebuild container: `cd ~/honcho && docker compose up -d --build --force-recreate deriver`
4. Reset failed queue items: `docker exec honcho-database-1 psql -U postgres -c "UPDATE queue SET processed=false, error=NULL WHERE task_type='representation' AND error IS NOT NULL;"`

## Token Truncation Patches Required

Two source patches needed on HOST (`~/honcho/src/`) before rebuilding:

**`representation.py` line ~100** — truncate observations to 8192 tokens:
```python
import tiktoken
_enc = tiktoken.get_encoding("cl100k_base")
_max_tok = min(settings.EMBEDDING.MAX_INPUT_TOKENS, 8192)
observation_texts = [
    _enc.decode(_enc.encode(t)[:_max_tok]) if len(_enc.encode(t)) > _max_tok else t
    for t in observation_texts
]
```

**`embedding_client.py` line ~169** — change Gemini token cap from 2048 to 8192:
```python
self.max_embedding_tokens: int = min(max_input_tokens, 8192)  # was 2048
```

## Docker Patching Workflow

1. Modify source on HOST (`~/honcho/src/`)
2. Rebuild: `docker compose build --force-recreate deriver`
3. Verify: `docker exec honcho-deriver-1 grep -n "your_change" /app/src/file.py`

**NOTE:** `docker compose restart` does NOT pick up env var or source changes. Always use `--force-recreate`. For source changes, use `--build --force-recreate`.

## Common Pitfalls

| Pitfall | Symptom | Fix |
|---------|---------|-----|
| Cloud key (`AQ...`) from Python | 400 API_KEY_INVALID | Use AI Studio key |
| `docker compose restart` | Old env/source persists | Use `--force-recreate` |
| Observations > 8192 tokens | "exceeds maximum token limit" | Patch `representation.py` + `embedding_client.py` |
| Container patches lost | Changes disappear after rebuild | Modify HOST source, then rebuild |
