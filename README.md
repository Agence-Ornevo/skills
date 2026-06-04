# Ornevo Skills Hub

Custom skills and workflows for the Ornevo agency. Business-ready skills for data analytics, marketing, sales, operations, engineering, and design — plus Ornevo-specific tooling.

## Structure

```
skills/
├── ornevo-toolkit/          # Ornevo agency tool stack reference
├── ornevo-digest-audit/     # Monthly audit of Daily Digest system
├── honcho-integration-checks/ # Verify Honcho integration
├── kanban-codex-lane/       # Codex CLI as Kanban worker
├── data/                    # Data analysis, SQL, dashboards
├── design/                  # UX, accessibility, design critique
├── engineering/             # Code review, deploy, documentation
├── marketing/               # SEO, content, email, brand
├── operations/              # Process, compliance, risk
├── productivity/            # Task management, memory
├── sales/                   # Outreach, pipeline, research
├── finance/                 # Financial statements, audit
├── legal/                   # Contracts, compliance, NDA
└── human-resources/         # Hiring, onboarding, performance

customized/                  # Orneva-customized skill variants
```

## Installation

```bash
# Add as Hermes tap
hermes skills tap add Agence-Ornevo/skills

# Install individual skills
hermes skills install Agence-Ornevo/skills/data/skills/analyze
hermes skills install Agence-Ornevo/skills/marketing/skills/seo-audit
```

## Upstream

- `data/`, `design/`, `engineering/`, `marketing/`, `operations/`, `productivity/`, `sales/`, `finance/`, `legal/`, `human-resources/` — forked from [anthropics/knowledge-work-plugins](https://github.com/anthropics/knowledge-work-plugins)
- Ornevo-specific skills are original work
- `customized/` contains Ornevo-tuned variants

## Version History

| Date | Change |
|------|--------|
| 2026-06-04 | Initial structure: knowledge-work-plugins + Ornevo custom skills |
