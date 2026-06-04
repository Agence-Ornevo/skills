# OpenCode Team AI Configuration

> Reference for Ornevo's corporate AI tool stack setup (June 2026).

## Architecture

**Recommended stack:** OpenCode + OpenRouter + Hermes (existing)

- **OpenCode**: Team-facing AI coding agent (terminal TUI, desktop app, IDE extension)
- **OpenRouter**: Unified model gateway (same as current Hermes setup)
- **Hermes**: Automation backbone (cron, n8n, digest — keep as-is)

## Why OpenCode

- Open source (Anomaly), 160K GitHub stars, 900 contributors
- Free to use, any model provider (OpenRouter, Anthropic, OpenAI, local, etc.)
- SKILL.md-based shared skills (Hermes-compatible format)
- Desktop app in beta (macOS, Windows, Linux) for non-technical users
- Terminal TUI + VS Code extension for technical users
- Enterprise plan available for SSO/MDM when scaling
- Config cascade: remote (.well-known) -> global -> project -> inline
- No code stored externally (privacy-first)

## Why NOT OpenWork (Claude Cowork)

- $20-30/user/mo adds up fast
- Anthropic-only, no shared skills system
- No GitHub org integration
- Vendor lock-in

## Config Locations

OpenCode loads config from (in precedence order):
1. Remote: `.well-known/opencode` endpoint (org defaults via HTTPS)
2. Global: `~/.config/opencode/opencode.json` (user preferences)
3. Custom: `OPENCODE_CONFIG` env var (overrides)
4. Project: `opencode.json` in project root (project-specific)
5. Inline: `OPENCODE_CONFIG_CONTENT` env var (runtime overrides)
6. Managed: `/Library/Application Support/opencode/` (admin/MDM — highest priority)

Configs are **merged**, not replaced. Later sources override only conflicting keys.

## Key Config File

`~/.config/opencode/opencode.json`:

    {
      "$schema": "https://opencode.ai/config.json",
      "model": "openrouter/owl-alpha",
      "autoupdate": true,
      "server": { "port": 4096 }
    }

## Skill Locations (OpenCode loads from all)

Project-level (highest priority):
- `.opencode/skills/<name>/SKILL.md`
- `.claude/skills/<name>/SKILL.md` (Claude Code compatible)
- `.agents/skills/<name>/SKILL.md` (OpenCode Go compatible)

Global:
- `~/.config/opencode/skills/<name>/SKILL.md`
- `~/.claude/skills/<name>/SKILL.md`
- `~/.agents/skills/<name>/SKILL.md`

Shared skills for the team live in the `ornevo-ai-config` GitHub repo, cloned
and symlinked to the global skill directories. Each project repo can also have
its own `.opencode/skills/` directory for project-specific skills.

## Recommended Shared Skills for Ornevo

| Skill | Purpose | Audience |
|-------|---------|----------|
| `ornevo-agency` | Agency workflows, client comms, SOW templates | All |
| `wordpress-dev` | WP development standards, theme/plugin patterns | Dev |
| `power-bi` | DAX formulas, data modeling, dashboard standards | Data |
| `shopify` | Liquid, Shopify APIs, e-commerce patterns | Dev |
| `client-comms` | Email templates, proposal writing, follow-ups | All |
| `github-workflow` | Branch naming, PR templates, review process | Dev |
| `n8n-automation` | Workflow patterns, webhook setup, integrations | All |
| `data-analytics` | Python/pandas/SQL boilerplate, analysis patterns | Data |

## Onboarding: Technical Users

    # 1. Install OpenCode
    curl -fsSL https://opencode.ai/install | bash

    # 2. Authenticate with GitHub (ornevo-agence org)
    opencode auth login

    # 3. Clone and link shared config
    git clone git@github.com-ornevo-agence:ornevo-agence/ornevo-ai-config.git ~/.ornevo-ai
    mkdir -p ~/.config/opencode
    ln -sf ~/.ornevo-ai/opencode.json ~/.config/opencode/opencode.json
    ln -sf ~/.ornevo-ai/skills ~/.config/opencode/skills

    # 4. Set OpenRouter API key
    export OPENROUTER_API_KEY=*** 5. Use in any project
    cd ~/projects/ornevo/your-project
    opencode

## Onboarding: Non-Technical Users

1. Download OpenCode Desktop from https://opencode.ai/download
2. Sign in with GitHub (ornevo-agence org)
3. Enter OpenRouter API key (provided by admin)
4. Select default model: "OpenRouter / owl-alpha"
5. Open project folder -> use chat interface (no terminal needed)

## OpenRouter Team Key Strategy

| Strategy | Pros | Cons | Best For |
|----------|------|------|----------|
| Single team key | Simple | No per-user tracking | Teams < 10 |
| Individual keys | Cost tracking per user | More keys to manage | Teams > 10 |
| Key pool | Avoids rate limits | Complex config | High-volume usage |

## Cost Estimates (per user/month)

| Model | Est. Cost | Notes |
|-------|-----------|-------|
| owl-alpha (OpenRouter) | $15-30 | Recommended default |
| claude-sonnet-4-5 | $40-80 | Fallback for complex tasks |
| gpt-4o | $30-60 | Alternative |
| gemini-2.5-pro | $15-30 | Budget option |

*Based on ~500K tokens/day usage*

## Implementation Timeline (June 2026)

- **Week 1 (Jun 2-6)**: Create `ornevo-ai-config` repo, write initial config, port skills
- **Week 2 (Jun 9-13)**: Pilot with 2-3 technical users, test shared skills
- **Week 3 (Jun 16-20)**: Expand to non-technical users, individual API keys
- **Week 4 (Jun 23-27)**: Harden — onboarding guide, cost monitoring, skill PR process

## Full Plan

See the detailed plan at:
`/Users/hdsolanop/.hermes/plans/2026-06-03_ornevo-corporate-ai-plan.md`
