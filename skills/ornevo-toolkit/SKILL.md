---
name: ornevo-toolkit
description: "Ornevo agency and freelance tool stack reference: n8n, Figma, OpenProject, Mattermost, SCM Analytics (Kings Pastry), and project conventions including Power BI data source documentation workflow."
version: 1.3.0
author: Novum
license: MIT
platforms: [macos, web]
metadata:
  hermes:
    tags: [Ornevo, agency, freelance, n8n, mattermost, figma, openproject, scm-analytics]
---

# Ornevo Agency & Freelance Tool Stack

Reference for Hernan Solano's active tool stack across Ornevo agency operations and freelance/SCM Analytics projects.

## Project Folders

```
~/projects/ornevo/          — Agency projects (ornevo-prod/)
~/projects/hdsolanop/       — Personal/freelance (Gyptech, Kings Pastry, etc.)
~/.hermes/TODO-*.md         — Pending setup items
```

## Active Projects (June 2026)

| Project | Repo | Local Path | Status |
|---------|------|------------|--------|
| Gyptech Phase 0 | hdsolanop/gyptech_phase_0 | ~/projects/hdsolanop/gyptech_phase_0 | Phase 2 active |
| Management | hdsolanop/management | ~/projects/hdsolanop/management | Active — CVs (EcomOps + TechPM/Applaudo), LinkedIn banner (4 versions + design prompt), Linkedin audit |
| Sonia Sanabria Case | hdsolanop/sonia-sanabria-case | ~/projects/hdsolanop/sonia-sanabria-case | Active (May 2026) — Child support conciliation letters + strategic revision plan |
| Personal Finance | hdsolanop/personal-finance | ~/projects/hdsolanop/personal-finance | Active — Sure (Maybe fork) + NocoDB multi-currency finance system. See `references/personal-finance.md` |
| Kings Pastry Control Tower | hdsolanop/Kings-pastry | ~/projects/hdsolanop/Kings-pastry | Active — Power BI dashboard suite (8 dashboards, 42 KPIs). See `references/kings-pastry.md` |
| Ornevo Website | ornevo-agence/ornevo-website | ~/projects/ornevo/ornevo-website | Active — Dockerized WordPress, `wp-content/` + design assets |
| Ornevo France | ornevo-agence/ornevo-france | ~/projects/ornevo/ornevo-france | Active — French market ops: competitive analysis, commercial workflows, landing specs. Mixed binary assets — needs `.gitignore` |
| Ornevo Prod Infra | ornevo-agence/ornevo-prod | ~/projects/ornevo/ornevo-prod | Active — Docker services: Mattermost, Docmost, Plane, OpenProject, n8n, Homer |

### Project Folder Organization Convention

**Rule:** When creating project documentation/workspace, always use structured subdirectories — never dump files flat in the project root.

Standard subfolder pattern for dashboard builds:
```
Dashboard_Name/
  Build/           ← Build plans, template analysis
  Data_Sources/    ← Source maps, SQL queries, column verification
  DAX/             ← Measures, date tables, calculation groups
  Documentation/   ← KPI definitions, slicer rules, grain specs
  Validation/      ← Checklists, data quality notes
```

**Trigger:** When Hernan says "keep things organized" or "we should have subfolders", create this structure immediately.

## Kings Pastry Control Tower (hdsolanop/Kings-pastry)

Supply chain visibility & analytics dashboard suite for Kings Pastry (bakery, Hong Kong / Canada). 8 Power BI dashboards covering executive overview, service fulfillment, inventory, production, procurement, cost management, warehouse operations, and alerts. Full project data, data sources, build schedule, per-dashboard specifications, and client-confirmed thresholds at `references/kings-pastry.md`.

**Quick stats:** 8 dashboards, 42 KPIs. HS owns D01/D02/D03/D08 (24 KPIs). MR owns D04/D05/D06/D07 (18 KPIs). Build window: Jun 1-10 in 4 parallel pairs. L3 drill-downs due 1 week after each build.

**D07 data extraction (Jun 3-4, 2026):** 10 of 11 tables available. 7 via BC API (`data_extract/extract_d07_api.py`) + 3 manual exports (Warehouse Entry TXT→CSV, Sales Header Archive Excel→CSV, Sales Line Archive Excel→CSV). Bin (7354) excluded — cannot be exported from BC. Capacity Utilization calculation pending Shine confirmation. Labour KPI uses ADP report from SharePoint. Full documentation in `data_extract/README.md` and `data_extract/D07_Data_Source_Reference.docx` in the Kings Pastry repo.

**BC API patterns:** Authentication quirks (special chars in secrets), line-table access patterns (navigation vs direct), pagination (`@odata.nextLink` omission → `$skip` fallback), `in` operator not supported (use batched `or`), date filtering, and entity availability are all documented in `references/bc-api-patterns.md`. **Always check this before writing BC API extraction code.**

**Key files in repo:**
- `V2_Out_of_Scope_Tracker.md` — D08 deferred, out-of-scope features, post-build trail
- `D07_Data_Source_Reference.md` — D07 data sources, slicer scope, blockers
- `data_source/General_Entry_Filters_COMPLETE.md` — All GL account filter mappings
- `Sprint 4 - template development/D07_Historical_Inventory_Retrospective.sql` — Historical inventory SQL

### Personal Finance System (hdsolanop/personal-finance)

Sophisticated multi-system finance tracking. Full detail at `references/personal-finance.md`.

**Architecture:** NocoDB (nocodb.hernansolano.com) = raw transaction store. Sure (self-hosted Maybe fork, sure.hernansolano.com) = analysis/budgeting/net worth. HTML dashboard with Chart.js + Claude Haiku AI.

**7 accounts:** Davibank Ahorro, Davibank Bolsillo, BlackCard CC (EUR/COP), Addi loan, Nequi, Cash (COP), Wise EUR, Wise USD.

**Key dependency:** Self-hosted Sure instance at `sure.hernansolano.com` — if down, entire dashboard breaks. Set up health monitoring.

**Import status:** 1,406+ transactions as of May 27 2026. Weekly upload cycle (ideally Sunday).

**Note:** Repo was cloned from Windows machine — paths reference `C:\\Users\\herna\\`. `.bat` files for sync_scripts are Windows-only.

## Ornevo Production Server — Full Stack

See `references/server-infra.md` for full container inventory, database map, nginx config, and integration strategies.

| Field | Value |
|-------|-------|
| Provider | OVH Public Cloud B2-7 |
| IP | 91.134.67.56 |
| SSH | `ssh ornevo` (key: ~/.ssh/id_ornevo_pro_ed25519) |

### Running Services

| Service | Domain | Integration |
|---------|--------|-------------|
| **Mattermost** | chat.ornevo.pro | Hermes gateway plugin (bot exists, PAT pending) |
| **Docmost** | docmost.ornevo.pro | REST API |
| **n8n** | n8n.ornevo.pro | ✅ MCP configured |
| **Plane** | pm.ornevo.pro | REST API |
| **OpenProject** | project.ornevo.pro | REST API |
| **Homer** | status.ornevo.pro | Static config |
| **WordPress** | ornevo.fr | mcp-adapter plugin pending |

### PostgreSQL Databases (5 on server)

op-db (OpenProject), n8n-db, mm-db (Mattermost), docmost-db, plane-plane-db-1. See `references/server-infra.md` for access patterns.

## Ornevo Agency Tools — Full Stack

| Tool | Purpose | Access | Integration Strategy |
|------|---------|--------|---------------------|
| **n8n** | Workflow automation | n8n.ornevo.pro | ✅ MCP configured |
| **Figma** | UI/UX design | Desktop app + MCP | 🟡 Figma MCP pending |
| **OpenProject** | Project management | project.ornevo.pro | REST API via curl/n8n |
| **Plane** | PM (Linear-style) | pm.ornevo.pro | REST API via curl/n8n |
| **Mattermost** | Team chat | chat.ornevo.pro | Hermes gateway plugin (bot exists, pending PAT) |
| **Docmost** | Wiki / docs | docmost.ornevo.pro | REST API via curl/n8n |
| **Homer** | Status dashboard | status.ornevo.pro | Static config |
| **WordPress** | Website | ornevo.fr | 🟡 mcp-adapter plugin pending |
| **Brevo** | Email marketing | app.brevo.com | 🟡 MCP (Brevo official, 27 modules) — need API key |
| **Bitrix24** | CRM | bitrix24.com | 🟡 MCP (gunnit/bitrix24-mcp-server) — need webhook URL |

## Brevo Integration

- **Purpose:** Email marketing, campaigns, contacts, deals, analytics, transactional email, SMS, WhatsApp
- **MCP:** Official Brevo MCP server at `https://mcp.brevo.com/v1/brevo/mcp` (27 modules)
- **Alternative:** Community `@houtini/brevo-mcp` via npm (self-hosted, stdio)
- **Auth:** Brevo API key (starts with `xkeysib-`) from Account → SMTP & API → API Keys
- **Claude config:**
```json
{
  "mcpServers": {
    "brevo": {
      "command": "npx",
      "args": ["mcp-remote", "https://mcp.brevo.com/v1/brevo/mcp", "--header", "Authorization: Bearer ${BREVO_API_KEY}"],
      "env": { "BREVO_API_KEY": "xkeysib-..." }
    }
  }
}
```
- **What it enables:** Create/send campaigns, manage contacts/lists, view analytics, manage deals, send transactional emails, SMS, WhatsApp

## Bitrix24 Integration

- **Purpose:** CRM — contacts, deals, leads, companies, tasks, sales monitoring
- **MCP:** `gunnit/bitrix24-mcp-server` (TypeScript, stdio)
- **Auth:** Bitrix24 webhook URL (`https://<domain>.bitrix24.com/rest/<USER_ID>/<WEBHOOK_CODE>/`)
- **Claude config:**
```json
{
  "mcpServers": {
    "bitrix24": {
      "command": "node",
      "args": ["/path/to/bitrix24-mcp-server/build/index.js"],
      "env": { "BITRIX24_WEBHOOK_URL": "https://..." }
    }
  }
}
```
- **What it enables:** Full CRM (CRUD contacts/deals/leads/tasks), sales monitoring, team performance dashboard, deal progression tracking, customer engagement analysis

## Freelance / SCM Analytics Tools

| Tool | Purpose | Status |
|------|---------|--------|
| **Power BI** | Data analytics | Windows only (not on macOS) |
| **Python 3.9** | Data science | System Python (needs upgrade) |
| **Excel/VBA** | ETL (Gyptech) | macOS Excel |
| **SQL** | DB queries | No local DB server |

## GitHub Accounts

| Account | SSH Alias | Email | Projects |
|---------|-----------|-------|----------|
| hdsolanop | github.com-hdsolanop | hdsolanop92@gmail.com | Personal + freelance |
| ornevo-agence | github.com-ornevo-agence | admin@ornevo.fr | Agency |

**gh CLI**: `/opt/homebrew/bin/gh` (v2.93.0), authed as hdsolanop. Note: `which gh` can fail in some shell contexts — use full path if needed.

## n8n Integration

- n8n has webhook-based OAuth with Google Workspace (`n8n-ornevo` GCP project)
- Existing OAuth client is **Web app** type — only works for n8n webhooks, NOT for CLI tools
- For CLI Google access (gws/Novum), a separate **Desktop app** OAuth client is needed

## Output Language Policy

**ALL outputs must be in English only.** Hernan works in English for all project deliverables, client communications, and technical documentation. Never mix Chinese characters or other languages into responses unless explicitly asked. This applies to:
- Email drafts
- Client-facing documents
- Technical documentation
- Status updates and check-ins
- All conversational responses

If the user writes in Spanish or French, match their language for that exchange, but proactively switch back to English for all deliverables and follow-ups.

**Related:** Client email templates, stakeholder list, and cross-dashboard question extraction workflow at `references/kings-pastry-client-workflows.md`.

## Hermes Workflow Skills

| Skill | Purpose | Location |
|---|---|---|
| `agent-skill-framework-porting` | Evaluate + port external agent skill frameworks (gstack, etc.) into Hermes | `~/.hermes/skills/software-development/agent-skill-framework-porting/` |
| `gstack-hermes` *(planned)* | Ornevo-specific plan/review/ship workflow ported from gstack | Not yet created — see `.hermes/plans/2026-06-17_gstack-hermes-integration.md` |

**SSH cloning with multiple GitHub accounts:** The `gh` CLI uses HTTPS/token internally but `git clone git@github.com:...` uses SSH. When `~/.ssh/config` only defines host aliases (`github.com-hdsolanop`, `github.com-ornevo-agence`) without a plain `github.com` host, `gh repo fork` creates the fork via API but the clone step fails with `Permission denied (publickey)`. Fix: use `gh repo fork --clone=false` then clone with the alias (`git clone git@github.com-hdsolanop:<owner>/<repo>.git`). See `github-auth` skill for details.

To connect Hermes to Mattermost as a chat gateway (so Hernan can chat with Novum via Mattermost):

1. Create a bot account + PAT on Mattermost (see `references/mattermost.md`)
2. Enable the platform in `~/.hermes/config.yaml`:
   ```yaml
   platforms:
     mattermost:
       enabled: true
       extra:
         url: https://chat.ornevo.pro
   ```
3. Set `MATTERMOST_TOKEN` env var (the bot's PAT)
4. Optionally set `MATTERMOST_HOME_CHANNEL` to a channel ID for cron/notifications
5. Restart the Hermes gateway

The adapter is at `~/.hermes/hermes-agent/plugins/platforms/mattermost/adapter.py`.
It uses WebSocket for real-time events + REST API for sending.

**Status (June 2026):** Bot account `hermes` created on Mattermost. PAT not yet generated (waiting for Mattermost restart to enable PATs). Hermes gateway not yet enabled.

## Ornevo Daily Digest System

Automated news digest + blog content pipeline. Full operational detail at `references/digest-pipeline.md`.

**Quick reference:**
- **Digest cron:** daily 9 AM Colombia → WhatsApp (job: `fa6d61274627`)
- **Source bank:** `~/.hermes/digest-sources.txt` (108 sources, 8 topics, ranked)
- **Generator:** `~/.hermes/scripts/digest-generator.py` (Python RSS fetcher, tested)
- **n8n workflow:** `~/.hermes/n8n-workflows/blog-article-generator.json` (importable)
- **Setup guide:** `references/digest-pipeline.md` (webhook URL, AI prompts, WP credentials)

**Topics:** E-Commerce FR | Shopify FR | Agency OSS | WordPress | WebDev | EAA | AI Agents | OpenRouter

**Content pipeline:** Digest article → n8n webhook → FR article → ES/EN translation → WP drafts (ornevo.fr, REST API)

**Related:** Novum Tips (daily tips cron) — see `references/novum-tips.md` for the sibling scheduled-delivery pattern.

## Novum Proactive Delivery

Daily tips and scheduled content delivery to Hernan via WhatsApp. See `references/novum-tips.md` for full details on active cron jobs, content rules, and wordplay bank.

## Ornevo Corporate AI Tool Stack

### Current Recommendation (Updated June 3, 2026 — Autoplan Mode)

**IMPORTANT: Non-technical team members will NOT use CLI/terminal tools.**
Hernan explicitly stated: "Hermes is very technical, other team members would NOT
be open to interact via CLI or terminal. I prefer a UI approach like OpenWork."

This means **GUI-First UX is the #1 priority** (25% weight), followed by **Shared Skills Hub** (20%).

### 10-Option Autoplan Ranking (GUI-First 25%, Skills Hub 20%)

| Rank | Option | Score | Cost/10 users | Best For |
|------|--------|-------|---------------|----------|
| 🥇 1st | **OpenWork + Hermes** | 95/100 | ~$225/mo | Best overall: GUI + skills hub + MCP + open source |
| 🥈 2nd | OpenWork alone | 92/100 | ~$225/mo | Simplest, but loses Hermes automation |
| 🥉 3rd | Hermes Desktop + OpenCode | 88/100 | ~$225/mo | Already deployed, proven, weak GUI |
| 4th | Copilot Enterprise + Hermes | 75/100 | ~$498/mo | GitHub native, expensive |
| 5th | Cursor Business + Hermes | 73/100 | ~$600/mo | Best IDE, expensive, no skills hub |
| 6th | Windsurf + Hermes | 69/100 | ~$free-$? | Good IDE, enterprise pricing TBD |
| 7th | Claude Code CLI + Hermes | 55/100 | ~$750/mo | Tech users only, terminal-only |
| 8th | Kimi Desktop + Hermes | 54/100 | ~$200/mo | Good UI, closed, no MCP |
| 9th | Perplexity Pro + Hermes | 47/100 | ~$200/mo | Search tool, not agent platform |
| 10th | Lindy + Hermes | 42/100 | ~$370/mo | Productivity, not dev agent |

### Key Findings

- **OpenWork** (openworklabs.com) is the standout: open source, free desktop, built on OpenCode, has team skills sharing (share via single link, one-click import), MCP support, browser automation, guardrails
- **Hermes Desktop** (v0.15.2) is CLI/TUI-oriented — not suitable as primary GUI for non-tech team members
- **Kimi** has nice desktop apps but closed ecosystem — no MCP, no skills hub
- **Perplexity** and **Lindy** are not agent platforms — wrong tools for dev/agency work
- **Nebula.ai** domain is for sale — product shut down or rebranded
- **Windsurf** merged with Devin (Cognition) in 2026

### Decision Factors

- **Best overall → OpenWork + Hermes**: GUI-first + skills hub + MCP + $0 license + open source
- **Already deployed → Hermes + OpenCode**: Proven, but desktop UX is weak for non-tech
- **Best IDE → Cursor Business**: $40/user/mo, polished, but no skills hub
- **GitHub-native → Copilot Enterprise**: $39/user/mo, best org integration

### Interactive Decision Dashboard

An interactive HTML dashboard with adjustable weight sliders is available at:
`~/.hermes/plans/2026-06-03_ornevo-ai-autoplan-dashboard.html`

### Full Benchmark Data

Detailed 10-option autoplan analysis with all 4 review lenses (CEO, Eng, Design, DX):
`~/.hermes/plans/2026-06-03_ornevo-ai-autoplan-10-options.md`

AI desktop agent landscape reference:
`references/ai-desktop-agent-landscape-2026.md`

## Pending Setup Items

See `~/.hermes/TODO-google-workspace.md` for Google OAuth multi-account setup steps.

## File Delivery (Remote Access)

When Hernan needs a file from the Mac mini but is remote, use the temporary HTTP server method. Full details at `references/file-delivery-workarounds.md`.

**TL;DR:** Zip the file → `python3 -m http.server 9876` (background) → share Tailscale IP link. WhatsApp doesn't support file attachments; Telegram/Discord/Signal do.

## Hermes Session & Process Model

Understanding the different "sessions" in Hernan's workflow:

| Concept | What it is | Visible to Hermes? | Survives terminal close? |
|---------|-----------|-------------------|------------------------|
| **WhatsApp session** | This conversation with Novum | N/A (it IS the session) | ✅ Yes, always |
| **CLI/TUI session** | Hernan's terminal running Hermes | No (separate process) | ❌ Closes with terminal |
| **Background process** | Long-running task started by Novum via `terminal(background=True)` | ✅ Yes, via `process(action="list")` | ✅ Yes, until done or killed |
| **SSH session** | Hernan SSH'd into a remote machine | ❌ No, completely independent | ✅ Yes, until disconnected |
| **Cron job** | Scheduled task created via `cronjob` tool | ✅ Yes, via `cronjob(action="list")` | ✅ Yes, runs on schedule |

**Key rule:** Only processes that Novum started via `terminal(background=True)` appear in `process(action="list")`. Everything else (SSH, local terminals, manual scripts) is invisible to Novum.

## Cron Job Schedule Format

When creating cron jobs via the `cronjob` tool, the `schedule` field accepts:
- **Duration format:** `30m`, `2h`, `1d`, `every 2h`
- **Cron expressions:** `0 10 * * *` (minute hour day-of-month month day-of-week)
- **ISO timestamps:** `2026-06-01T09:00:00` (one-shot)

It does **NOT** accept natural language like `"every day at 9:00 AM Colombia"`. Use cron expressions and specify the timezone offset in the expression (e.g., `0 10 * * *` for 10 AM UTC-5).

**Tip:** For daily tips or check-ins, use two cron jobs (morning + afternoon) rather than trying to randomize within a single job.
