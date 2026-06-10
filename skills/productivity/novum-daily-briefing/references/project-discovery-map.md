# Project Discovery Map — Novum Daily Briefing

## Directory Structure Reference

### Ornevo Agency Workstream (`/Users/hdsolanop/projects/ornevo/`)
```
ornevo/
├── ornevo-prod/           # Production infrastructure
│   ├── PENDING.md         # Infra gaps, backups, monitoring, SSH hygiene
│   ├── OPERATIONS.md      # Runbook for all services
│   ├── services/          # Docker compose stacks (mattermost, docmost, plane, n8n, openproject, homer)
│   └── plane/             # Plane instance config (.env.fixed)
├── ornevo-website/        # WordPress theme
│   ├── wp-content/themes/ornevo/    # Custom theme
│   └── docker/            # Local dev stack
├── ornevo-france/         # French market client projects
│   ├── CLAUDE.md          # Project structure, design system, WP theme
│   ├── Ricoh/             # Accessibility audits, BFSG quotes
│   ├── Baija/             # CRO Plan Découverte, Nailmatic custom site
│   ├── Densmore/          # Case mgmt, invoicing exports
│   ├── Centrale Fillers/  # Clinique proposals, lettres de mission
│   ├── Generik/           # Backend audit Fidelité
│   ├── culture_cepage/    # Proposal
│   ├── le_dauphin/        # Proposal
│   ├── propositions/      # Legacy proposals
│   ├── Action_items/      # (check for active items)
│   └── DELIVERABLE_INDEX.md (in ornevo-accessibility-eaa/)
├── ornevo-accessibility-eaa/   # EAA Compliance Service launch
│   ├── DELIVERABLE_INDEX.md      # All 16 deliverables status
│   └── 00-06_*.md              # Legal brief, service design, pricing, tooling, audit templates, comms
└── ornevo-design/         # Design system (DESIGN.md, CONTENT_V3.md)
```

### Freelance Data Workstream (`/Users/hdsolanop/projects/hdsolanop/`)
```
hdsolanop/
├── Kings-pastry/          # Power BI D01–D07 (MAIN CLIENT)
│   ├── CLAUDE.md          # BC API endpoints, KPI definitions, DAX patterns
│   ├── Action_items/      # Blocker emails, data requests
│   │   ├── Action_Required_D06_D07_Data_Blockers_2026-06-05.md
│   │   └── Dashboard_action_Items.xlsx
│   ├── D01_Executive_Overview/ through D07_Warehouse_Operations/
│   ├── DataBase/          # SQL schemas, validation queries
│   ├── Sprint 4 - template development/
│   └── data_extract/      # API extraction scripts
├── gyptech_phase_0/       # CLBP 132600 Data Dictionary
│   ├── PROJECT_STATUS_UPDATE.md    # Phase 2 complete, ready for cross-ref
│   ├── MDL_PD_VISUAL_SUMMARY.txt
│   ├── fab/               # Fab&Exp dictionary
│   ├── mdl/               # MDL dictionary
│   └── pd/                # PD analysis
├── personal-finance/      # NocoDB + Sure financial tracking
│   ├── CLAUDE.md          # Accounts, import rules, categories, exchange rates
│   ├── compute_metrics.py # Dashboard computation
│   ├── finance-health-dashboard.html
│   └── manual_entries/    # Weekly statement CSVs
├── sonia-sanabria-case/   # Legal case (family law)
│   ├── Carta Conciliación v3 FINAL 2026-05-26.docx
│   ├── adjuntos/          # Evidence attachments
│   ├── analisis/          # Legal analysis
│   └── respuestas/        # Responses
├── personal-fitness/      # Workout/nutrition tracking
├── ornevo-content/        # Content calendar, blog posts
└── management/            # Internal ops, admin
```

## Key Status Files to Check Each Run

| Project | Primary Status File | Secondary Files |
|---------|---------------------|-----------------|
| Ornevo Infra | `ornevo-prod/PENDING.md` | `OPERATIONS.md`, git log |
| Ornevo Website | `ornevo-website/wp-content/themes/ornevo/CLAUDE.md` | git log |
| Ricoh | `ornevo-france/Ricoh/*.xlsx` | Quote dates in filenames |
| Baija | `ornevo-france/Baija/*Plan_Decouverte*.xlsx` | Proposal dates |
| Densmore | `ornevo-france/Densmore/invoices*.xlsx` | Export dates |
| Centrale Fillers | `ornevo-france/Centrale Fillers/*Proposition*.xlsx` | Letter dates |
| Generik | `ornevo-france/Generik/Generik_devis.xlsx` | Quote date |
| EAA Compliance | `ornevo-accessibility-eaa/DELIVERABLE_INDEX.md` | 05_service_page_spec_fr.md |
| Kings Pastry | `Kings-pastry/Action_items/Action_Required_D06_D07_Data_Blockers_2026-06-05.md` | CLAUDE.md, git log |
| GypTech | `gyptech_phase_0/PROJECT_STATUS_UPDATE.md` | COMPLETION_SUMMARY.md |
| Personal Finance | `personal-finance/CLAUDE.md` (Import Status table) | manual_entries/ |
| Sonia Sanabria | `sonia-sanabria-case/Carta Conciliación v3 FINAL 2026-05-26.docx` | adjuntos/, analisis/ |

## Git Activity Check Commands
```bash
# Ornevo Agency
cd /Users/hdsolanop/projects/ornevo/ornevo-prod && git log --oneline -5 --since="7 days ago"
cd /Users/hdsolanop/projects/ornevo/ornevo-france && git log --oneline -5 --since="7 days ago"
cd /Users/hdsolanop/projects/ornevo/ornevo-accessibility-eaa && git log --oneline -5 --since="7 days ago"

# Freelance Data
cd /Users/hdsolanop/projects/hdsolanop/Kings-pastry && git log --oneline -5 --since="7 days ago"
cd /Users/hdsolanop/projects/hdsolanop/gyptech_phase_0 && git log --oneline -5 --since="7 days ago"
cd /Users/hdsolanop/projects/hdsolanop/personal-finance && git log --oneline -5 --since="7 days ago"
cd /Users/hdsolanop/projects/hdsolanop/sonia-sanabria-case && git log --oneline -5 --since="7 days ago"
```

## Client Contact Verification
- **Gmail/Outlook search**: `from:client@domain after:YYYY/MM/DD`
- **Plane/CRM**: Check `pm.ornevo.pro` for last activity on project
- **WhatsApp**: Check message threads (manual)

## At-Risk Thresholds
| Criterion | Threshold | Action |
|-----------|-----------|--------|
| Deadline proximity | ≤ 3 calendar days | Flag in 🔴 DEADLINES section |
| No client contact | > 3 business days | Flag in 🟡 COMMUNICATION GAP section |
| Kings Pastry blockers | Any 🔴 critical blocker | Immediate escalation email draft |
| Billable hours gap | Yesterday's commits ≠ Plane entries | Reminder to log |