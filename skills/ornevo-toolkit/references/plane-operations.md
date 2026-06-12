# Plane CE — Operations Reference (ornevo-prod)

## Critical Gotcha: CERT_ACME_* Variables Must Be Set

**Problem:** Plane's proxy container (Caddy) fails to start with:
```
Error: adapting config using caddyfile: parsing caddyfile tokens for 'acme_ca': wrong argument count or unexpected line ending after 'acme_ca'
```

**Root Cause:** The Caddyfile template references `${CERT_ACME_CA}` and `${CERT_ACME_DNS}`. When these are unset/empty in `.env`, Caddy sees bare `acme_ca` / `acme_dns` directives with no argument → parse error.

**Fix:** Ensure `/home/ubuntu/ornevo/plane/.env` contains:
```bash
CERT_ACME_CA=https://acme-v02.api.letsencrypt.org/directory
CERT_ACME_DNS=
```
(Empty `CERT_ACME_DNS` is fine; empty `CERT_EMAIL=` keeps ACME off — host nginx + certbot handle TLS per architecture invariant #1.)

---

## Plane Compose Command Pattern

**Every** `docker compose` command for Plane **must** include both env files:
```bash
cd /home/ubuntu/ornevo/plane
sudo docker compose --env-file variables.env --env-file .env <cmd>
```
- `variables.env` = upstream defaults (checked into repo)
- `.env` = ornevo overrides (server-only, mode 0600, never committed)
- Without both, stack falls back to upstream defaults and breaks

---

## Update Procedure (OS + Docker Images)

### 1. OS Packages
```bash
ssh ornevo "sudo apt update && sudo apt upgrade -y"
```
- Updates Docker (29.5.0 → 29.5.3), containerd, nginx, systemd, etc.
- Kernel upgrade may be pending (requires reboot)
- **Containers are NOT restarted by apt**

### 2. Docker Images (Per-Service)
```bash
# n8n
ssh ornevo "cd /home/ubuntu/ornevo/n8n && docker compose pull && docker compose up -d"

# Mattermost
ssh ornevo "cd /home/ubuntu/ornevo/mattermost && docker compose pull && docker compose up -d"

# Docmost
ssh ornevo "cd /home/ubuntu/ornevo/docmost && docker compose pull && docker compose up -d"

# OpenProject
ssh ornevo "cd /home/ubuntu/ornevo/openproject && docker compose pull && docker compose up -d"

# Homer
ssh ornevo "cd /home/ubuntu/ornevo/homer && docker compose pull && docker compose up -d"

# Plane (MUST use both env files)
ssh ornevo "cd /home/ubuntu/ornevo/plane && docker compose --env-file variables.env --env-file .env pull && docker compose --env-file variables.env --env-file .env up -d"
```

### 3. Verify
```bash
# All containers healthy
ssh ornevo "docker ps --format 'table {{.Names}}\t{{.Status}}'"

# All domains responding
for d in n8n.ornevo.pro chat.ornevo.pro project.ornevo.pro docmost.ornevo.pro pm.ornevo.pro status.ornevo.pro; do
  curl -s -o /dev/null -w "%{http_code} %{time_total}s" --max-time 10 "https://$d"
done
```

---

## Health Check Endpoints

| Service | Health Endpoint | Expected |
|---------|----------------|----------|
| n8n | `https://n8n.ornevo.pro/healthz` | 200 |
| Mattermost | `https://chat.ornevo.pro` | 200 |
| OpenProject | `https://project.ornevo.pro` | 302 (redirect to login) |
| Docmost | `https://docmost.ornevo.pro` | 200 |
| Plane | `https://pm.ornevo.pro` | 200 |
| Homer | `https://status.ornevo.pro` | 200 |

---

## SSL Certificate Expiry (as of Jun 2026)

| Domain | Expires |
|--------|---------|
| n8n.ornevo.pro | Aug 4, 2026 |
| chat.ornevo.pro | Sep 4, 2026 |
| project.ornevo.pro | Aug 13, 2026 |
| docmost.ornevo.pro | Sep 4, 2026 |
| pm.ornevo.pro | Sep 6, 2026 |
| status.ornevo.pro | Aug 31, 2026 |

Let's Encrypt auto-renewal via certbot snap should handle these. Verify with:
```bash
ssh ornevo "systemctl list-timers | grep certbot"
```

---

## Architectural Invariants (from CLAUDE.md)

1. **Nginx on host only** — terminates TLS, only listener on :80/:443
2. **App ports bind 127.0.0.1 only** — never 0.0.0.0
3. **DB/Redis no published ports** — internal bridge DNS only
4. **One stack per directory, one bridge per stack**
5. **OVH masquerade rule critical** — `iptables -t nat -A POSTROUTING -s 172.16.0.0/12 -o ens3 -j MASQUERADE` (persisted by `docker-routing.service`)
6. **Certs one-per-subdomain** via certbot --nginx

If all endpoints return 502: check masquerade rule first.
```bash
sudo iptables -t nat -L POSTROUTING -n -v | grep 172.16.0.0/12
sudo systemctl status docker-routing.service
```