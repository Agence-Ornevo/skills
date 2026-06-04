# Ornevo Production Server — Infrastructure Reference

## Server Access

- **SSH:** `ssh ornevo` (ensure alias exists in ~/.ssh/config)
- **IP:** 91.134.67.56 | **User:** ubuntu | **Key:** ~/.ssh/id_ornevo_pro_ed25519
- **OVH B2-7 instance** (2 vCPU, 7GB RAM per README — verify actual specs)

## Running Docker Containers (verified June 2026)

| Container | Image | Status | Internal Port | External Domain |
|-----------|-------|--------|---------------|-----------------|
| homer | b4bz/homer:latest | Healthy | 8084 | status.ornevo.pro |
| openproject | openproject/openproject:15 | Up | 8083 | project.ornevo.pro |
| op-db | postgres:15-alpine | Healthy | 5432 | — |
| n8n | n8nio/n8n:2.20.7 | Up | 5678 | n8n.ornevo.pro |
| n8n-db | postgres:16-alpine | Healthy | 5432 | — |
| docmost | docmost/docmost:latest | Up | 3000 | docmost.ornevo.pro |
| docmost-db | postgres:16-alpine | Healthy | 5432 | — |
| docmost-redis | redis:7-alpine | Up | 6379 | — |
| mattermost | mattermost/mattermost-team-edition:10.11.15 | Healthy | 8065 | chat.ornevo.pro |
| mm-db | postgres:16-alpine | Healthy | 5432 | — |
| plane-api-1 | makeplane/plane-backend:v1.3.0 | Up | 8000 | — |
| plane-web-1 | makeplane/plane-frontend:v1.3.0 | Up | 3000 | pm.ornevo.pro |
| plane-proxy-1 | makeplane/plane-proxy:v1.3.0 | Up | 8082 | — |
| plane-worker-1 | makeplane/plane-backend:v1.3.0 | Up | — | — |
| plane-beat-worker-1 | makeplane/plane-backend:v1.3.0 | Up | — | — |
| plane-admin-1 | makeplane/plane-admin:v1.3.0 | Healthy | — | — |
| plane-space-1 | makeplane/plane-space:v1.3.0 | Up | — | — |
| plane-live-1 | makeplane/plane-live:v1.3.0 | Up | — | — |
| plane-plane-db-1 | postgres:15.7-alpine | Up | 5432 | — |
| plane-plane-mq-1 | rabbitmq:3.13.6-management-alpine | Up | 5672 | — |
| plane-plane-redis-1 | valkey/valkey:7.2.11-alpine | Up | 6379 | — |
| plane-plane-minio-1 | minio/minio:latest | Up | 9000 | — |

## PostgreSQL Databases

All accessible via: `docker exec -it <container> psql -U <user> <db>`

| Container | Likely DB Name | Used By |
|-----------|---------------|---------|
| op-db | openproject | OpenProject PM |
| n8n-db | n8n | n8n workflow store |
| mm-db | mattermost | Mattermost chat |
| docmost-db | docmost | Docmost wiki |
| plane-plane-db-1 | plane | Plane PM tool |

**Common pattern:** username is usually the service name, password in docker-compose env.

## Nginx Configuration

All proxy configs in `/etc/nginx/sites-enabled/`:
- Each domain gets an `upstream` block pointing to `127.0.0.1:<port>`
- SSL via Let's Encrypt at `/etc/letsencrypt/live/<domain>/`
- HTTP → HTTPS redirect for all domains

## Accessing Services from Claude/SSH

```bash
# Quick container status
ssh ornevo "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}'"

# Run a command in a container
ssh ornevo "docker exec -it <container-name> <command>"

# Check logs
ssh ornevo "docker logs --tail 50 <container-name>"

# Postgres query (example)
ssh ornevo "docker exec -it <db-container> psql -U <user> -d <db> -c 'SELECT ...'"
```

## Integration Strategies per Service

| Service | Integration Approach |
|---------|---------------------|
| Mattermost | Hermes gateway plugin (bot `hermes` exists, PAT pending) |
| OpenProject | REST API at https://project.ornevo.pro/api/v3 |
| Plane | REST API (Linear-compatible) |
| Docmost | REST API for wiki/pages |
| n8n | MCP already configured |
| Postgres | MCP (`@modelcontextprotocol/server-postgres`) — 5 DBs accessible |

## Add missing tools/CLIs to server

```bash
ssh ornevo
sudo apt update && sudo apt install -y <package>
# or for Docker containers:
docker exec -it <container> bash -c "apt update && apt install -y <package>"
```

## Brevo & Bitrix24 (Cloud services, not on-prem)

- **Brevo:** Cloud at app.brevo.com — MCP via `https://mcp.brevo.com/v1/brevo/mcp`
- **Bitrix24:** Cloud CRM — MCP via `gunnit/bitrix24-mcp-server` (local node server, needs webhook URL)
- Neither runs on the OVH server; they're SaaS integrated via API/MCP
