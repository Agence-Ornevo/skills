# Mattermost — chat.ornevo.pro

Ornevo's internal team chat. Mattermost Team Edition 10.11.15 on OVH B2-7.

## Stack

- `mattermost` container — app (binds `127.0.0.1:8065`)
- `mm-db` — Postgres 16 (no published port, internal bridge `mm-internal`)
- Nginx on host terminates TLS at `chat.ornevo.pro` → proxies to `127.0.0.1:8065`

## Server paths

```
~/ornevo/mattermost/
├── docker-compose.yml
├── .env                    ← MM_DB_PASSWORD, MM_SMTP_PASSWORD
├── config/                 ← bind-mounted, owned by UID 2000
├── data/ logs/ plugins/ client-plugins/ bleve-indexes/
└── (named volume: mm_db_data)
```

Config file: `~/ornevo/mattermost/config/config.json` (owned by UID 2000, use `sudo` to edit).

## Channels (ornevo team)

| Channel | Type | Purpose |
|---------|------|---------|
| `town-square` | public | General |
| `projet-ornevofr` | public | Main project channel |
| `ornevo-management` | private | Management |
| `propositions` | private | Proposals |
| Various devis-* | private | Client quotes |

## Bot account: `hermes`

- User ID: `hermesbotid1234567890ab`
- Email: `hermes-bot@ornevo.pro`
- Owner: `bnwg4guo7tygmgr19o1i6jmg8r` (hernan)
- Created via direct DB insert (mmctl --local bot create refuses in local mode)
- Member of: `ornevo` team, `town-square` and `projet-ornevofr` channels

## Creating a bot token (complete guide)

### Critical: PAT enablement requires FULL container restart

The `EnablePersonalAccessTokens` setting is cached in memory at startup. The API `POST /api/v4/config/reload` does NOT pick it up. You MUST do a full container stop/start.

**Correct sequence:**

```bash
# 1. Enable PATs in config.json
sudo python3 -c "
import json
with open('/home/ubuntu/ornevo/mattermost/config/config.json') as f:
    c = json.load(f)
c['ServiceSettings']['EnablePersonalAccessTokens'] = True
with open('/home/ubuntu/ornevo/mattermost/config/config.json', 'w') as f:
    json.dump(c, f, indent=2)
"

# 2. Also insert into Systems table (belt-and-suspenders)
docker exec mm-db psql -U mmuser -d mattermost -c \
  "INSERT INTO Systems (name, value) VALUES ('EnablePersonalAccessTokens', 'true') ON CONFLICT(name) DO UPDATE SET value='true';"

# 3. Full container restart (NOT just 'docker compose restart')
cd ~/ornevo/mattermost
sudo docker compose down && sudo docker compose up -d

# 4. Wait ~30 seconds for Mattermost to fully start
```

Note: `docker compose restart` sends SIGHUP which does NOT reload this setting. Only a full stop/start works. The user must run this manually (blocked by Hermes safety).

### Reset admin password

```bash
# Preferred: mmctl
docker exec mattermost mmctl --local user change-password hernan --password 'NewPass'

# Fallback: bcrypt hash in DB (password column, NOT authdata)
python3 -c "import bcrypt; print(bcrypt.hashpw(b'NewPassword', bcrypt.gensalt(rounds=12)).decode())"
docker exec mm-db psql -U mmuser -d mattermost -c \
  "UPDATE Users SET password='<bcrypt_hash>', authservice='', authdata='' WHERE username='hernan';"
```

### Log in via API

```bash
curl -s -D- -X POST -H 'Content-Type: application/json' \
  -d '{"login_id": "hernan", "password": "NewPass"}' \
  https://chat.ornevo.pro/api/v4/users/login
# Token is in the `Token:` response header (NOT in the body)
```

### Create PAT via API

```bash
curl -s -X POST \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"description": "Hermes AI bot token"}' \
  https://chat.ornevo.pro/api/v4/users/<user_id>/tokens
```

### Create bot via API

```bash
curl -s -X POST \
  -H "Authorization: Bearer *** \
  -H "Content-Type: application/json" \
  -d '{"username": "hermes", "display_name": "Hermes AI", "description": "Ornevo AI assistant"}' \
  https://chat.ornevo.pro/api/v4/bots
```

### Create bot via DB insert (when API/PAT unavailable)

See the bot account section above for the SQL. Key tables: `Users`, `Bots`, `teammembers`, `channelmembers`.

## Hermes gateway integration

Required config in `~/.hermes/config.yaml`:
```yaml
platforms:
  mattermost:
    enabled: true
    extra:
      url: https://chat.ornevo.pro
```

The adapter reads token from `MATTERMOST_TOKEN` env var.
Home channel set via `MATTERMOST_HOME_CHANNEL` env var (use channel ID, not name).

## Running Python on the server (escaping-safe pattern)

**Always use SCP + file execution** instead of inline `python3 -c "..."` over SSH:

```bash
# 1. Write script locally
cat > /tmp/myscript.py << 'PYEOF'
# ... Python code ...
PYEOF

# 2. Copy to server and run
scp -i ~/.ssh/id_ornevo_pro_ed25519 /tmp/myscript.py ubuntu@91.134.67.56:/tmp/myscript.py
ssh -i ~/.ssh/id_ornevo_pro_ed25519 ubuntu@91.134.67.56 'python3 /tmp/myscript.py'
```

**For passwords with special chars** (`%`, `^`, `@`, `!`):
```bash
# Write password to file on server using Python (avoids shell escaping)
ssh ... 'python3 -c "with open(\"/tmp/pass.txt\",\"w\") as f: f.write(\"actual_password\")"'
# Then read in script: open("/tmp/pass.txt").read().strip()
```

**Verify file contents** with `xxd` if strings look wrong — tools can silently corrupt special characters.

## Useful mmctl commands

```bash
docker exec mattermost mmctl --local user list
docker exec mattermost mmctl --local team list
docker exec mattermost mmctl --local channel list ornevo
docker exec mattermost mmctl --local user search <query>
docker exec mattermost mmctl --local user change-password <user> --password <newpass>
```

Note: No `-it` flag (container has no TTY).

## Known issues

- `mmctl --local bot create` → "cannot be run in local mode" — use DB insert or API
- `docker compose restart` does NOT reload `EnablePersonalAccessTokens` — full `down && up -d` required
- `POST /api/v4/config/reload` does NOT pick up PAT enablement — full process restart needed
- Config.json owned by UID 2000 — use `sudo` to edit
- `docker exec -it` does NOT work (no TTY) — use without `-it`
- `printf "%s" "M%9g..."` doubles `%` — use Python to write files with special chars
- Shell escaping with special chars in passwords is error-prone — write to file first
