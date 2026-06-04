# Novum Proactive Delivery Patterns

Reference for scheduled, themed content delivery from Novum to Hernan via WhatsApp.

## Daily Tips — "Novum Tips"

Hernan requested 1-2 daily tips on working with Novum/Hermes more effectively, delivered via WhatsApp at random hours between 7 AM and 10 PM Colombia time (UTC-5).

### Active Cron Jobs

| Job | Name | Schedule | Time (UTC-5) |
|-----|------|----------|--------------|
| `a735698ac8cb` | Novum Tip #1 — "Novum Dium" | `0 10 * * *` | 10:00 AM |
| `6edf026355fd` | Novum Tip #2 — "Novum Noctis" | `0 17 * * *` | 5:00 PM |

### Content Rules

- 1-2 short tips max per delivery
- Clever/funny wordplay on "Novum" (Latin: "new thing")
- Every 3-4 days: include a relevant Hermes update or new feature
- Tone: direct, witty, bullet-point style — no fluff
- Sign off with a Novum-themed sign-off (rotate, don't repeat)

### Novum Wordplay Bank

| Pun | Meaning | Usage |
|-----|---------|-------|
| Novum Dium | New Day | Morning tips |
| Novum Noctis | New Night | Evening tips |
| Novum Habits | New Habits | Workflow improvement tips |
| In Novum We Trust | — | Trust/automation tips |
| Novum-mentum | Momentum | Progress/consistency tips |
| No-vum Pain | No Pain | Simplification tips |
| Novum-bers | Numbers | Data/analytics tips |
| Re-novum | Renew | Refactoring/cleanup tips |
| Novum-orandum | Brainstorming | Ideation tips |
| Novum Operandi | Mode of Operating | Process/workflow tips |
| Novum-ficial | Official | Best practices tips |
| Novum-bral | Cerebral/Membranous | Deep thinking tips |
| Novum Planum | New Plan | Planning tips |
| Novum Sum | I am new/renewed | Self-improvement tips |
| Ad Novum | To the New | Migration/upgrade tips |
| Novum-craft | — | Skill-building tips |

### Management

To update tips or schedule, remove old cron jobs and create new ones via the `cronjob` tool. See the main SKILL.md for cron schedule format rules.
