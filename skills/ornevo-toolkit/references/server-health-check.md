# Ornevo Production Server — Health Check Procedure

## Quick Health Check (run from local machine)

```bash
# 1. Container fleet status
ssh ornevo "docker ps --format 'table {{.Names}}\t{{.Image}}\t{{.Status}}\t{{.Ports}}'"

# 2. Unhealthy containers
ssh ornevo "docker ps --filter health=unhealthy --format '{{.Names}}'"

# 3. System resources
ssh ornevo "df -h / && free -h && uptime"

# 4. Recent error logs (all services)
ssh ornevo "for c in n8n mattermost openproject docmost plane-api-1 plane-web-1 homer; do echo \"=== \$c ===\"; docker logs --tail 30 \$c 2>&1 | grep -iE 'error|fail|warn|exception|fatal|panic' | head -10; done"

# 5. External domain accessibility + response time
for domain in n8n.ornevo.pro chat.ornevo.pro project.ornevo.pro docmost.ornevo.pro pm.ornevo.pro status.ornevo.pro; do
  echo "=== \$domain ==="
  curl -s -o /dev/null -w "%{http_code} %{time_total}s" --max-time 10 "https://\$domain" 2>&1 || echo "FAILED"
done

# 6. SSL certificate expiry
for domain in n8n.ornevo.pro chat.ornevo.pro project.ornevo.pro docmost.ornevo.pro pm.ornevo.pro status.ornevo.pro; do
  echo "=== \$domain ==="
  echo | openssl s_client -servername \$domain -connect \$domain:443 2>/dev/null | openssl x509 -noout -dates 2>/dev/null | grep notAfter
done

# 7. n8n health endpoint
curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://n8n.ornevo.pro/healthz"

# 8. Docker disk usage
ssh ornevo "docker system df -v"

# 9. OS package updates
ssh ornevo "apt list --upgradable 2>/dev/null | head -20"
```

## Database Connectivity Verification

```bash
# n8n workflows
ssh ornevo "docker exec n8n-db psql -U n8n -d n8n -c 'SELECT count(*) as workflow_count FROM workflow_entity;'"

# OpenProject projects
ssh ornevo "docker exec op-db psql -U openproject -d openproject -c 'SELECT count(*) FROM projects;'"

# Mattermost users (user: mmuser)
ssh ornevo "docker exec mm-db psql -U mmuser -d mattermost -c 'SELECT count(*) FROM Users;'"

# Docmost pages
ssh ornevo "docker exec docmost-db psql -U docmost -d docmost -c 'SELECT count(*) FROM pages;'"

# Plane (via API since psql auth varies)
curl -s -o /dev/null -w "%{http_code}" --max-time 10 "https://pm.ornevo.pro/api/workspaces"
```

## Key Findings from June 2026 Check

| Check | Result | Notes |
|-------|--------|-------|
| Container fleet | 20/20 healthy | 1 exited migrator (normal) |
| External domains | All 200/302 | Response times 0.68-1.27s |
| SSL certs | Valid | Expire Aug 4 - Sep 6, 2026 |
| System resources | Healthy | 44% disk, 2.1G available RAM |
| Docker logs | Clean | No ERROR/WARN in recent logs |
| Databases | All accessible | Verified via psql queries |
| OS updates | 20+ packages | Docker 29.5.0→29.5.3, systemd, nginx |

## Action Items Template

| Item | Priority | Due | Owner |
|------|----------|-----|-------|
| SSL cert renewal verification | Medium | Before Aug 4, 2026 | — |
| OS/Docker updates | Low | Next maintenance window | — |
| Backup verification | Medium | Monthly | — |
| n8n workflow execution monitoring | Low | Ongoing | — |

## Automation Ideas

- Cron job for daily external domain + SSL check
- n8n workflow to run health check and post to Mattermost
- Prometheus/Grafana for continuous metrics (future)