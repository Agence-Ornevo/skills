## Memory Provider Verification Checklist

After migrating Honcho to a native `.env` configuration, ensure that Hermes is actually using Honcho as its memory backend.

1. **Confirm Hermes config**
   ```bash
   hermes config get memory.provider
   # Expected output: honcho
   ```
2. **Write a test fact** (any short note) via Hermes or directly with the memory tool:
   ```bash
   memory action=add target=memory content="🧪 honcho‑memory‑test‑$(date +%s)"
   ```
3. **Search for the fact** to verify persistence:
   ```bash
   memory action=replace old_text="honcho‑memory‑test" new_string="honchar-test"
   # or use the /search_memory slash command if available
   ```
4. **Check Honcho dashboard** (if you have the UI) for the new entry under the *Memory* section.
5. **Restart Hermes** (`/reset` in chat) and repeat step 3 to ensure the fact survived the restart.

If any step fails, revisit the `.env` file and ensure `HONCHO_API_KEY` is correct and the service is reachable (use `hermes doctor --check memory`).
