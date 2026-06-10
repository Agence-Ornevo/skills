# Audit Curl Commands Reference

Verified working commands from 2026-06-09 audit run.

## Prerequisites
```bash
export N8N_API_KEY="<hermes-agent JWT from n8n>"
export N8N_BASE_URL="https://n8n.ornevo.pro"
```

## n8n — Workflow Discovery
```bash
# List all active workflows
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/workflows?active=true&limit=100"

# Find workflows with webhook triggers
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/workflows?active=true&limit=100" | \
  jq -r '.data[] | select(.nodes[]?.type == "n8n-nodes-base.webhook") | "\(.id) | \(.name) | \(.nodes[] | select(.type=="n8n-nodes-base.webhook") | .parameters.path)"'
```

## n8n — Execution Error Analysis
```bash
# All error executions (last 50)
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/executions?status=error&limit=50"

# Errors for specific workflow
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/executions?workflowId=<WORKFLOW_ID>&status=error&limit=20"

# Full execution details with error data
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/executions/<EXECUTION_ID>?includeData=true"

# Successful executions for comparison
curl -s -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/executions?workflowId=<WORKFLOW_ID>&status=success&limit=5"
```

## n8n — Container Health Checks
```bash
# Test Google Sheets API connectivity from n8n container
docker exec n8n curl -I https://sheets.googleapis.com

# Test DNS resolution
docker exec n8n nslookup sheets.googleapis.com

# Check n8n container logs
docker logs n8n --tail 100
```

## Credential Verification (all systems)
```bash
# n8n
curl -s -o /dev/null -w "%{http_code}" -H "X-N8N-API-KEY: $N8N_API_KEY" "$N8N_BASE_URL/api/v1/workflows?active=true&limit=1"
# Expected: 200

# Bitrix24 (requires BITRIX24_WEBHOOK_URL)
curl -s -o /dev/null -w "%{http_code}" "$BITRIX24_WEBHOOK_URL/crm.deal.list?limit=1"
# Expected: 200

# Brevo (requires BREVO_API_KEY)
curl -s -o /dev/null -w "%{http_code}" -H "api-key: $BREVO_API_KEY" "https://api.brevo.com/v3/account"
# Expected: 200

# Linear (requires LINEAR_API_KEY)
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $LINEAR_API_KEY" "https://api.linear.app/graphql"
# Expected: 200

# Notion (requires NOTION_API_KEY)
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $NOTION_API_KEY" "https://api.notion.com/v1/users/me"
# Expected: 200

# Plane (requires PLANE_API_KEY)
curl -s -o /dev/null -w "%{http_code}" -H "Authorization: Bearer $PLANE_API_KEY" "https://pm.ornevo.pro/api/v1/projects/"
# Expected: 200
```

## Key Header Format
| API | Header Format |
|-----|---------------|
| n8n REST | `X-N8N-API-KEY: <JWT>` |
| Brevo | `api-key: <KEY>` |
| Linear | `Authorization: Bearer <KEY>` |
| Notion | `Authorization: Bearer <KEY>` |
| Plane | `Authorization: Bearer <KEY>` |
| Bitrix24 | Query param in webhook URL |

**Note:** n8n MCP server must be configured to use `X-N8N-API-KEY` header, not `Authorization: Bearer`.