---
name: ornevo-agency-stale-audit
description: Ornevo Agency scheduled stale communications audit — checks Bitrix24, Brevo, Linear/Notion, n8n for SLA breaches, drafts multilingual follow-ups, alerts Hernán via WhatsApp.
version: 1.0.0
author: ornevo-agency
tags:
  - ornevo
  - agency
  - cron
  - stale-communications
  - sla-monitoring
  - client-delivery
---

# Ornevo Agency Stale Communications Audit

**Class-level skill** for the scheduled cron job that audits client communication staleness across Ornevo's agency stack and produces actionable follow-ups.

## Trigger Conditions
- Scheduled cron job (daily 09:00 CEST)
- Manual invocation: "Run stale communications audit"
- Any SLA breach alert from monitoring

## Operating Context
- **Profile**: `novum` (Hermes profile — Ornevo Agency operations)
- **Working directory**: `/Users/hdsolanop/projects/ornevo/`
- **SLA**: 24h business hours response time
- **Stale thresholds**: Bitrix24 >3 days, Email >48h, Approvals >2 days, Webhooks = immediate
- **Languages**: French (Ornevo France clients), English, Spanish (LATAM)
- **Timezone**: Europe/Paris (CEST)

## Required System Access (Configure Before First Run)

| System | Credential Type | Where to Configure | Status |
|--------|-----------------|-------------------|--------|
| Bitrix24 | REST API webhook + auth token | Bitrix24 Admin → Webhooks / REST API | ❌ Missing |
| Brevo | API v3 key | Brevo → Settings → API Keys | ❌ Missing |
| Linear | Personal API key | Linear → Settings → API | ❌ Missing |
| Notion | Integration token | Notion → Settings → Integrations | ❌ Missing |
| n8n | API key (JWT, audience: `public-api`) | n8n → User Menu → API Keys | ⚠️ Wrong key in MCP |
| Plane | Personal API token | Plane → Settings → API | ❌ Missing |
| WhatsApp | Business API or Twilio | Meta Business / Twilio Console | ❌ Missing |

> **Critical**: The n8n MCP server currently uses "MCP Server API Key" (audience: `mcp-server-api`, **no scopes**). Must switch to **"hermes-agent"** key (audience: `public-api`, full scopes). See `references/n8n-auth-fix.md`.
>
> **Critical**: The n8n REST API expects `X-N8N-API-KEY: <JWT>` header, **not** `Authorization: Bearer`. The MCP server config must be updated to send the correct header. Hermes config: `~/.hermes/config.yaml` (mcp_servers.n8n) — this is the global config, not profile-specific.

## Audit Workflow

### 1. Bitrix24 — Deals with No Activity >3 Days
```bash
# Query: GET /rest/1/{webhook}/crm.deal.list?filter[>DATE_MODIFY]={3days_ago}&select[]=ID,TITLE,CONTACT_ID,COMPANY_ID,STAGE_ID,DATE_MODIFY,ASSIGNED_BY_ID
# For each stale deal: fetch contact/company names, last activity, assigned owner
```

### 2. Brevo — Unanswered Client Emails >48h
```bash
# Query: GET /v3/smtp/statistics/aggregatedReport?startDate={2days_ago}&endDate={today}&limit=100
# Cross-reference with inbound email webhook logs (if configured) or IMAP search
# Filter: threads where last outbound < last inbound - 48h
```

### 3. Plane/Notion — Client Approvals Pending >2 Days
```bash
# Plane: GET /api/v1/issues/?project={project_id}&state={in_review_state_id}&updated_at__lt={2days_ago}
# Notion: Query database where Status="Pending Approval" and Last Edited < 2 days ago
```

### 4. n8n — Webhook Errors (Client Form Submissions)
```bash
# List active workflows with webhooks
curl -H "X-N8N-API-KEY: $N8N_API_KEY" "https://n8n.ornevo.pro/api/v1/workflows?active=true&limit=100"

# Find webhook workflows
# jq -r '.data[] | select(.nodes[]?.type == "n8n-nodes-base.webhook") | "\(.id) \(.name)"'

# Check executions for errors (all workflows)
curl -H "X-N8N-API-KEY: $N8N_API_KEY" "https://n8n.ornevo.pro/api/v1/executions?status=error&limit=50"

# Check specific workflow errors
curl -H "X-N8N-API-KEY: $N8N_API_KEY" "https://n8n.ornevo.pro/api/v1/executions?workflowId=<ID>&status=error&limit=20"

# Get execution details with error data
curl -H "X-N8N-API-KEY: $N8N_API_KEY" "https://n8n.ornevo.pro/api/v1/executions/<EXECUTION_ID>?includeData=true"
```

**Key header:** `X-N8N-API-KEY` (not `Authorization: Bearer`)

## Multilingual Follow-up Templates

All templates in `templates/followups/` directory:
- `bitrix-deal-inactivity-{fr,en,es}.md`
- `brevo-unanswered-email-{fr,en,es}.md`
- `plane-approval-pending-{fr,en,es}.md`
- `n8n-webhook-errors-{fr,en,es}.md`

Variables: `{ClientName}`, `{DealName}`, `{LastContactDate}`, `{DaysStale}`, `{DirectURL}`, `{SLADeadline}`

## WhatsApp Alert Format

```
🤖 Ornevo Agency — Stale Communications Alert
Run: {timestamp}
Status: {OK | ⚠️ Partial | ❌ Failed}

Stale Items Found: {count}
{bullet list: Client | System | Type | Days Stale | Language}

Top Priority: {highest SLA breach}
Action: {specific next step}

Templates ready in {language} for all items.
Reply "SEND {item_id}" to dispatch, "CONFIG" for setup help.
```

## Common Pitfalls & Fixes

| Symptom | Root Cause | Fix |
|---------|------------|-----|
| n8n MCP returns 401 | Using "MCP Server API Key" (no scopes) | Switch MCP config to "hermes-agent" JWT key |
| n8n REST API returns 401 | Using `Authorization: Bearer` header | Use `X-N8N-API-KEY: <JWT>` header |
| n8n workflow fails with EHOSTUNREACH to sheets.googleapis.com | n8n container egress blocked (DNS/firewall/proxy) | Test `docker exec n8n curl -I https://sheets.googleapis.com`; fix DNS/egress; verify Google Sheets OAuth token not expired |
| NocoDB returns personal finance data | NocoDB MCP points to wrong base (Personal_finance) | Update NocoDB MCP server URL to agency CRM base |
| Bitrix24 403/401 | Webhook expired or wrong portal | Regenerate webhook in Bitrix24 Admin |
| Brevo rate limit | >300 calls/minute | Batch requests, add delays |
| Linear 404 | Wrong team/organization ID | Verify Linear API key org context |
| No stale items found | Thresholds too strict or data stale | Verify query time windows, check timezone (Europe/Paris) |
| WhatsApp not sending | Business API not verified | Use Twilio fallback or email-to-Hernán |
| SSH extraction fails | No public key on production server | Add SSH key to ubuntu@91.134.67.56 or manually copy JWT |

## Verification Checklist (Post-Run)

- [ ] All 4 systems queried successfully
- [ ] Stale items table populated with real data
- [ ] Follow-ups drafted in correct client language
- [ ] WhatsApp alert delivered to Hernán
- [ ] No false positives (verify each item manually first run)
- [ ] Log saved to `logs/stale-audit-{YYYY-MM-DD}.json`
- [ ] n8n container egress connectivity verified (`docker exec n8n curl -I https://sheets.googleapis.com`)

## References
- `references/n8n-auth-fix.md` — n8n API key configuration details
- `references/audit-curl-commands.md` — Verified curl commands for audit execution
- `references/bitrix24-api.md` — Bitrix24 REST API patterns
- `references/brevo-api.md` — Brevo API v3 endpoints
- `references/plane-api.md` — Plane (self-hosted) REST API for issues/approvals
- `references/notion-api.md` — Notion database query patterns

## Templates
- `templates/followups/bitrix-deal-inactivity-fr.md`
- `templates/followups/bitrix-deal-inactivity-en.md`
- `templates/followups/bitrix-deal-inactivity-es.md`
- `templates/followups/brevo-unanswered-email-fr.md`
- `templates/followups/brevo-unanswered-email-en.md`
- `templates/followups/brevo-unanswered-email-es.md`
- `templates/followups/plane-approval-pending-fr.md`
- `templates/followups/plane-approval-pending-en.md`
- `templates/followups/plane-approval-pending-es.md`
- `templates/followups/n8n-webhook-errors-fr.md`
- `templates/followups/n8n-webhook-errors-en.md`
- `templates/followups/n8n-webhook-errors-es.md`
- `templates/whatsapp-alert.md`

## Scripts
- `scripts/verify-credentials.sh` — checks all API keys respond 200
- `scripts/extract-n8n-jwt.py` — extracts full JWT from n8n DB
- `scripts/run-audit.py` — main audit orchestration (future)