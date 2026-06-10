---
name: business-skills-orchestrator
description: "Orchestrate business skills from the Agence-Ornevo/skills hub. Use when Hernan needs data analysis, marketing, sales, operations, design, or engineering business skills. Routes to the right skill from the org knowledge-work-plugins library. Trigger: any business task that maps to data/design/engineering/marketing/operations/sales categories."
---

# Business Skills Orchestrator

Routes business tasks to the right skill from the `Agence-Ornevo/skills` hub (forked from anthropics/knowledge-work-plugins).

## Skill Map

### Data & Analytics
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `analyze` | "analyze this data", "what's driving X", "answer this data question" | Quick lookups to full analyses |
| `build-dashboard` | "build a dashboard", "create KPI report", "visualize this data" | Interactive HTML dashboards |
| `sql-queries` | "write SQL", "query this", "how do I join" | Cross-dialect SQL |
| `data-visualization` | "chart this", "plot X vs Y", "what chart type" | Chart selection and generation |
| `statistical-analysis` | "is this significant", "test this hypothesis", "correlation" | Statistical tests |
| `validate-data` | "check data quality", "find issues in this data", "is this data clean" | Data quality assessment |

### Marketing
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `seo-audit` | "audit SEO", "check our SEO", "SEO health" | Full SEO audit with action plan |
| `content-creation` | "write a blog post", "draft content", "create copy" | Multi-channel content |
| `email-sequence` | "drip campaign", "nurture sequence", "email flow" | Multi-email sequences |
| `competitive-brief` | "competitor analysis", "battlecard", "vs competitor" | Competitive positioning |
| `brand-review` | "check brand consistency", "brand guidelines review" | Brand compliance |
| `campaign-plan` | "plan a campaign", "marketing campaign", "launch plan" | Campaign planning |
| `draft-content` | "draft a post", "write a tweet", "LinkedIn post" | Short-form content |
| `performance-report` | "marketing report", "channel performance", "ROI report" | Marketing analytics |

### Sales
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `draft-outreach` | "draft outreach", "cold email", "reach out to" | Personalized outreach |
| `call-prep` | "prep for call", "meeting prep", "get ready for" | Sales call preparation |
| `account-research` | "research this company", "intel on", "tell me about" | Prospect research |
| `competitive-intelligence` | "competitor intel", "what are they doing", "competitive landscape" | Competitive research |
| `pipeline-review" | "pipeline check", "deal review", "forecast" | Pipeline management |
| `call-summary` | "summarize that call", "meeting notes", "call recap" | Call documentation |
| `create-an-asset` | "create a one-pager", "sales asset", "leave-behind" | Sales collateral |
| `daily-briefing` | "daily brief", "what's happening today", "morning update" | Daily sales briefing |
| `forecast` | "revenue forecast", "pipeline forecast", "quota" | Sales forecasting |

### Design & UX
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `accessibility-review` | "check accessibility", "WCAG audit", "a11y review" | Accessibility audit |
| `design-critique` | "critique this design", "review this UI", "design feedback" | Design review |
| `design-handoff` | "handoff to dev", "design specs", "implementation guide" | Design-to-dev handoff |
| `design-system` | "design system", "component library", "style guide" | Design system work |
| `ux-copy` | "UX writing", "microcopy", "button text" | UX content |
| `user-research` | "user research", "interviews", "usability test" | Research synthesis |
| `research-synthesis` | "synthesize research", "findings", "insights" | Research analysis |

### Engineering
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `code-review` | "review this code", "check this PR", "is this safe" | Code review |
| `debug` | "debug this", "why is this broken", "fix this bug" | Debugging |
| `deploy-checklist` | "pre-deploy check", "deploy checklist", "ready to ship" | Deployment verification |
| `documentation` | "write docs", "document this", "README" | Technical documentation |
| `architecture` | "system design", "architecture review", "how should we build" | Architecture design |
| `system-design` | "design a system", "high-level design", "HLD" | System design |
| `testing-strategy` | "test strategy", "how to test", "test plan" | Testing approach |
| `tech-debt` | "tech debt", "refactor", "cleanup" | Technical debt management |
| `incident-response` | "incident", "outage", "something's broken" | Incident management |
| `standup` | "standup notes", "daily update", "what I did" | Standup preparation |

### Operations
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `process-doc` | "document this process", "SOP", "how do we" | Process documentation |
| `compliance-tracking` | "compliance", "regulatory", "requirements" | Compliance tracking |
| `risk-assessment` | "risk analysis", "what could go wrong", "risks" | Risk assessment |
| `status-report` | "status update", "weekly report", "progress report" | Status reporting |
| `vendor-review` | "evaluate vendor", "tool comparison", "should we use" | Vendor evaluation |
| `process-optimization` | "improve this process", "optimize", "streamline" | Process improvement |
| `capacity-plan` | "capacity planning", "resource planning", "headcount" | Capacity planning |
| `change-request` | "change request", "change management", "approval" | Change management |
| `runbook` | "runbook", "playbook", "operational guide" | Operational runbooks |

### Productivity
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `task-management` | "manage tasks", "prioritize", "what should I do" | Task management |
| `memory-management` | "save this", "remember this", "organize notes" | Knowledge management |
| `start` | "start my day", "morning routine", "what's next" | Daily startup |
| `update` | "update status", "progress check", "where are we" | Progress updates |

### Finance
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `financial-statements` | "financial statements", "P&L", "balance sheet" | Financial analysis |
| `variance-analysis` | "variance", "budget vs actual", "explain the difference" | Budget variance |
| `reconciliation` | "reconcile", "match transactions", "balance" | Reconciliation |
| `audit-support` | "audit", "audit prep", "supporting docs" | Audit preparation |
| `close-management` | "month-end close", "quarter close", "closing" | Period close |
| `journal-entry` | "journal entry", "adjusting entry", "accrual" | Journal entries |

### Legal
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `review-contract` | "review this contract", "contract check", "terms" | Contract review |
| `compliance-check` | "compliance check", "regulatory check", "legal review" | Compliance verification |
| `triage-nda` | "review NDA", "NDA check", "non-disclosure" | NDA triage |
| `legal-risk-assessment` | "legal risk", "exposure", "liability" | Legal risk |
| `brief` | "legal brief", "case summary", "research memo" | Legal research |

### Human Resources
| Skill | Trigger | What It Does |
|-------|---------|--------------|
| `onboarding` | "onboard", "new hire", "first day" | Onboarding |
| `interview-prep` | "interview prep", "prepare for interview", "questions" | Interview preparation |
| `performance-review` | "performance review", "evaluation", "feedback" | Performance reviews |
| `recruiting-pipeline` | "recruiting", "hiring pipeline", "candidates" | Recruiting |
| `draft-offer` | "offer letter", "draft offer", "compensation" | Offer letters |
| `comp-analysis` | "compensation analysis", "salary benchmark", "pay" | Compensation |
| `org-planning` | "org structure", "team planning", "reorg" | Org design |
| `policy-lookup` | "policy", "handbook", "what's the policy" | Policy reference |
| `people-report` | "headcount report", "team metrics", "people analytics" | People analytics |

## Ornevo-Specific Skills (in org repo)

| Skill | Description |
|-------|-------------|
| `ornevo-toolkit` | Agency tool stack reference |
| `ornevo-digest-audit` | Monthly Daily Digest audit |
| `honcho-integration-checks` | Honcho integration verification |
| `kanban-codex-lane` | Codex CLI as Kanban worker |

## Profile & Cron Orchestration (Novum Architecture)

### Three-Profile System

| Profile | Workdir | Purpose | Key Skills | Cron Pattern |
|---------|---------|---------|------------|--------------|
| `novum` | `/Users/hdsolanop` | Master orchestration, daily briefings, weekly retros, memory hub | `communication-preferences`, `plan`, `writing-plans`, `todo` | Daily 7AM briefing, 6PM recap, Fri 5PM retro, Mon-Fri 6PM billable reminder |
| `ornevo-agency` | `/Users/hdsolanop/projects/ornevo` | Agency delivery: WordPress, n8n, Bitrix24, proposals, sprints | `linear`, `notion`, `shopify`, `n8n` MCP, `bitrix24`, `brevo`, `web-accessibility-wcag`, `seo-audit` | Mon 9AM sprint kickoff, Fri 4PM retro/demo, daily 8AM n8n health, Mon 10AM invoice tracking, daily 10AM client follow-ups |
| `freelance-data` | `/Users/hdsolanop/projects/hdsolanop` | External contracts: Power BI, Python, SQL, Shopify, Kings Pastry | `dax-patterns`, `sql-queries`, `analyze`, `jupyter-live-kernel`, `shopify`, `python-debugpy` | Daily 5AM Kings Pastry schema sync, 6AM data refresh monitoring, 8AM deadline alerts, Fri 5PM hours log, Sun 6AM weekly schema diff |

### Cron Job Creation Pattern

```bash
cronjob create \
  --profile <profile-name> \
  --name "<Descriptive Name>" \
  --schedule "<cron-expression>" \
  --prompt "You are <Role>. Run <task>. TASK: 1. ... 2. ... CONTEXT: Working dir: <workdir>. Key data: <context>. OUTPUT: <format>." \
  --deliver origin
```

**Key principles:**
- Each cron runs in its **profile context** (workdir, skills, MCP, Honcho memory)
- Prompts must be **self-contained** — no chat context available
- Use `deliver: origin` for WhatsApp delivery
- Schedule in **Colombia timezone (UTC-5)**

---

## Kings Pastry Data Patterns

### Azure SQL Live Schema Sync (Daily 5AM)

**Tooling**: `query_runner.py` at `/Users/hdsolanop/projects/hdsolanop/Kings-pastry/DataBase/`
- AAD token via `az account get-access-token --resource https://database.windows.net/`
- ODBC Driver 18 for SQL Server
- Server: `kingsbi-sqlsrv-prod.database.windows.net` / Database: `DataWarehousePBI`

**Tables monitored** (9 core):
| Schema | Tables |
|--------|--------|
| `bc` | SalesHeader, SalesLine, SalesHeaderArchive, SalesLineArchive, Item, ItemCategory, Customer |
| `pbi` | DailyInventorySnapshot, KPIConfig |

**Documentation targets**:
- `DataBase/Schemas/*.md` — per-table schema docs
- `DataBase/D02_Relationships.md` — FK relationships
- `DataBase/D02_Validation_Queries.md` — data quality queries
- `DataBase/README.md` — master index with last sync timestamp

**Weekly diff report** (Sun 6AM): compares 7-day git history of schema files, produces impact matrix (table → affected D02-D08 dashboards/KPIs)

---

### ADP ↔ BC Work Center Mapping (ENT-T07 Blocker)

**Current state** (as of 2026-06-08):
| Table | Rows | Key Issue |
|-------|------|-----------|
| `scm.ADPBCWorkCenterMapping` | 60 | Maps ADP Dept Codes → "friendly names" |
| `bc.WorkCenter` | 31 | Uses short codes (`No` = PK) |
| `bc.ProductionOrder` | 20+ | Uses `RoutingNo`, **no `WorkCenterCode` column** |

**Match rate**: Only **5 of 22** mapped values match actual `bc.WorkCenter.No`:
- ✅ GB_JELLO_BIG, GB_JELLO_SM, PUFF, SUPPORT, T DOUGH C
- ❌ CAKE LINE → CAKE, BATTER MIX_HOBART → H_BACK_MIX/D_BACK_MIX, etc.

**Required for D04/D07 Labour KPIs**:
1. Fix mapping table to use actual `bc.WorkCenter.No` codes
2. Get `bc.Routing` + `bc.RoutingLine` tables (WorkCenterCode per operation)
3. Join path: `ProductionOrder.RoutingNo` → `RoutingLine.WorkCenterCode` → `WorkCenter.No` ← `ADPBCWorkCenterMapping.BCWorkCentreNo` → ADP hours

---

### Sure API COP Transaction Entry Pattern

```bash
curl -H "X-Api-Key: <KEY>" -H "Content-Type: application/json" \
  https://sure.hernansolano.com/api/v1/transactions \
  -d '{"transaction":{"name":"<desc>","amount":<COP_amount>,"date":"YYYY-MM-DD","account_id":"2041e43b-e177-4f2f-9a6b-8d996cdb393d","category_id":"d0ffa2e2-9495-422a-9ba8-907ee9e2c190","currency":"COP"}}'
```

**Critical**: `"currency":"COP"` parameter — without it, Sure defaults to EUR and converts incorrectly.

**Account IDs** (from CLAUDE.md):
- Wallet COP: `2041e43b-e177-4f2f-9a6b-8d996cdb393d`
- Category Transportation: `d0ffa2e2-9495-422a-9ba8-907ee9e2c190`

---

## Customization Workflow

When a vanilla skill from the org repo is used and needs Ornevo-specific context:

1. Use the vanilla skill first to test
2. Identify what needs customization (client data, brand voice, trilingual, BC schema, etc.)
3. Create a customized variant: `<skill-name>-ornevo`
4. Push to `Agence-Ornevo/skills/customized/` directory
5. The customized version takes precedence over vanilla

## Installation

Skills are installed from the org tap:
```bash
hermes skills tap add Agence-Ornevo/skills
hermes skills install Agence-Ornevo/skills/data/skills/analyze --force
```

Note: Some skills may be blocked by Hermes security scan (community source). Install from local `~/.hermes/skills/` copy if blocked.
