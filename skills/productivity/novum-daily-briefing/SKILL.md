---
name: novum-daily-briefing
description: Execute the Novum daily morning briefing workflow for Hernan Solano — project status matrix across Ornevo Agency + Freelance Data workstreams, at-risk identification, priority elicitation, billable hours check, WhatsApp delivery.
version: 1.0.0
author: Novum
license: MIT
---

# Novum Daily Morning Briefing

## Purpose
Execute the standardized daily briefing for Hernan Solano (Founder & Technical Lead, Ornevo) as the `novum` profile — the cross-cutting orchestration layer. Runs every weekday at 7:00 AM Colombia time (UTC-5).

## Workflow Steps

### 1. Project Discovery (Both Workstreams)
Scan active project directories to build the current portfolio:

**Ornevo Agency Workstream** (`/Users/hdsolanop/projects/ornevo/`):
- `ornevo-prod/` — Infrastructure (Mattermost, Docmost, Plane, n8n, OpenProject, Homer)
- `ornevo-website/` — WordPress theme development
- `ornevo-france/` — Client projects (Ricoh, Baija, Densmore, Centrale Fillers, Generik, Culture Cépage, Le Dauphin, EAA Compliance)
- `ornevo-accessibility-eaa/` — EAA Compliance Service launch assets

**Freelance Data Workstream** (`/Users/hdsolanop/projects/hdsolanop/`):
- `Kings-pastry/` — Power BI dashboards D01–D07 (critical client)
- `gyptech_phase_0/` — Data dictionary project (CLBP 132600)
- `personal-finance/` — NocoDB/Sure financial tracking
- `sonia-sanabria-case/` — Legal case management
- `personal-fitness/` — Health tracking
- `ornevo-content/` / `management/` — Internal ops

**Discovery method**: `ls -la <workstream-root>/` → identify subdirectories with recent git activity (last 7 days) or active CLAUDE.md/PENDING.md files.

### 2. Status Matrix Construction
For each active project, extract:
| Field | Source |
|-------|--------|
| Project Name | Directory name / CLAUDE.md header |
| Status | 🟢 Active / 🟡 At Risk / 🔴 Blocked / 🔵 Proposal / ✅ Done |
| Next Milestone | PENDING.md, CLAUDE.md, recent git commits, Action_items/ |
| Due Date | Explicit in docs or inferred from client comms |
| Last Client Contact | Email/CRM check — flag if >3 days |
| Blocker Risk | Red/Yellow/Green + mitigation |

**Format**: Two tables (one per workstream) with columns: Project, Status, Next Milestone, Due Date, Last Contact, Blocker Risk.

### 3. At-Risk Identification
Flag items meeting **either** criterion:
- **Deadline approaching**: Due date within 3 calendar days
- **Communication gap**: No client/stakeholder contact >3 days

Present as two separate lists with recommended actions.

### 4. Billable Hours Check
Remind to log yesterday's hours in Plane (pm.ornevo.pro) or tracking system. Note which projects had recent commits/activity suggesting billable work.

### 5. Priority Elicitation
End with: **"What are your top 3 priorities today?"** — wait for user input.

### 6. Delivery
Format per `communication-preferences` skill:
- English only
- Bullet points + tables
- Direct, action-oriented tone
- Red/Yellow/Green risk indicators
- Deliver via WhatsApp (cron `deliver: origin`)

## Trigger Conditions
- Cron: Daily 7:00 AM Colombia (UTC-5), Mon–Fri
- Manual: User says "morning briefing", "daily brief", "what's happening today", "run novum briefing"

## Key Data Sources
| Source | Path | Purpose |
|--------|------|---------|
| Ornevo prod infra | `projects/ornevo/ornevo-prod/PENDING.md` | Infra gaps, monitoring, backups |
| Ornevo France clients | `projects/ornevo/ornevo-france/<client>/` | Proposals, quotes, deliverables |
| Kings Pastry | `projects/hdsolanop/Kings-pastry/Action_items/` | Blockers, data requests, DAX |
| Kings Pastry | `projects/hdsolanop/Kings-pastry/CLAUDE.md` | API endpoints, schema, KPI defs |
| GypTech | `projects/hdsolanop/gyptech_phase_0/PROJECT_STATUS_UPDATE.md` | Phase status, next steps |
| Personal Finance | `projects/hdsolanop/personal-finance/CLAUDE.md` | Weekly refresh workflow |
| Git activity | `git log --oneline -5 --since="7 days ago"` | Recent work evidence |

## Output Template
```
# 🌅 MORNING BRIEFING — <Day>, <Date>
**Timezone:** Colombia (UTC-5) | **Profile:** `novum`

## 📊 PROJECT STATUS MATRIX — ALL ACTIVE PROJECTS
### 🏢 ORNEVO AGENCY WORKSTREAM
| Project | Status | Next Milestone | Due Date | Last Contact | Blocker Risk |
|---------|--------|----------------|----------|--------------|--------------|

### 📈 FREELANCE DATA WORKSTREAM
| Project | Status | Next Milestone | Due Date | Last Contact | Blocker Risk |
|---------|--------|----------------|----------|--------------|--------------|

## 🚨 AT-RISK ITEMS
### 🔴 DEADLINES WITHIN 3 DAYS
| Project | Item | Deadline | Action Required |

### 🟡 NO CLIENT CONTACT > 3 DAYS
| Project | Last Contact | Days Silent | Recommended Action |

## 💰 BILLABLE HOURS — YESTERDAY
| Project | Hours Logged? | Notes |

## ✅ TOP 3 PRIORITIES TODAY
**What are your top 3 priorities for today?**
1. 
2. 
3. 

## 🔧 QUICK ACTIONS AVAILABLE
- [ ] Draft client emails (ES/FR/EN)
- [ ] Extract DAX/SQL for review sessions
- [ ] Run finance refresh pipeline
- [ ] Check Plane for task assignments
```

## Cron Job Definition
```bash
cronjob create \
  --profile novum \
  --name "Novum Daily Morning Briefing" \
  --schedule "0 12 * * 1-5" \
  --prompt "You are Novum, Hernan Solano's strategic execution partner. Run the morning daily briefing for <Day>, <Date>. TASK: 1. Present Project Status Matrix for ALL active projects across both workstreams. 2. Identify at-risk items: deadlines within 3 days, no client contact >3 days. 3. Ask: 'What are your top 3 priorities today?' 4. Flag any billable hours not logged from previous day. 5. Deliver via WhatsApp to Hernan. CONTEXT: Timezone: Colombia (UTC-5). Workstreams: Ornevo Agency (projects/ornevo/) + Freelance Data (projects/hdsolanop/). Active projects: 4-12 simultaneous. OUTPUT FORMAT: Bullet points, tables for status matrix, direct and actionable. English only." \
  --deliver origin
```
**Note**: Cron schedule uses UTC. 7:00 AM Colombia (UTC-5) = 12:00 UTC. Mon–Fri = `1-5`.

## Related Skills
- `communication-preferences` — formatting rules (English only, tables, Red/Yellow/Green, direct tone)
- `business-skills-orchestrator` — profile/cron architecture, Kings Pastry patterns
- `legal-case-management` — if Sonia Sanabria case has active items
- `analyze` / `sql-queries` / `dax-patterns` — for Kings Pastry data extraction

## Pitfalls & Lessons
- **Don't assume project list is static** — always re-scan directories each run
- **Last contact dates need verification** — check Gmail/Outlook, not just file timestamps
- **Kings Pastry blockers change daily** — always read `Action_items/` fresh
- **Billable hours** — cross-reference git commits with Plane entries
- **WhatsApp delivery** — cron `deliver: origin` handles this; don't use `send_message`
- **Sunday runs** — if cron runs Sunday, note "weekend mode" and adjust (no client follow-ups expected)