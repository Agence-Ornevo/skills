# Ornevo Daily Digest & Content Pipeline — Detail Reference

Operational detail for the digest system. Quick reference is in the main SKILL.md.

## Architecture

RSS Feeds (22 priority) → digest-generator.py (cron 9 AM Colombia) → WhatsApp → User selects article → n8n webhook → FR article (OpenRouter) → ES+EN translations → WP drafts (ornevo.fr)

## Source Bank: ~/.hermes/digest-sources.txt

108 sources, 8 topics, ranked Tier 1/2/3 by authority+freshness+relevance+actionability (max 20 pts).

Topics: E-Commerce FR (15) | Shopify FR (14) | Agency OSS (15) | WordPress (14) | WebDev (14) | EAA (14) | AI Agents (12) | OpenRouter (10)

Key Tier 1 sources per topic:
- ECFR: Fevad, Journal du Net, Ecommerce Nation
- SHOP: Shopify Blog/Dev/Status
- ATOO: n8n, GitHub Trending, AlternativeTo, Cal.com, Plausible
- WP: WP News, WP Developer Blog, WPTavern, Wordfence
- WD: web.dev, MDN, Next.js, React
- EAA: EU Commission, Level Access, AudioEye, WCAG
- AIA: OpenAI, Anthropic, Google AI
- OR: OpenRouter Changelog, Models page, Free models

## Cron Jobs

| Job | ID | Schedule | Purpose |
|-----|----|----------|---------|
| Ornevo Daily Digest | fa6d61274627 | 0 9 * * * | Run digest.py, deliver WhatsApp |
| Novum Tip #1 Dium | a735698ac8cb | 0 10 * * * | Morning tip + Hermes update |
| Novum Tip #2 Noctis | 6edf026355fd | 0 17 * * * | Evening tip + Hermes update |

## n8n Blog Article Workflow

Webhook: POST https://n8n.ornevo.pro/webhook/generate-blog-article
Input: { article_url, article_title, topic }

Setup steps:
1. Import blog-article-generator.json into n8n.ornevo.pro
2. Configure OpenRouter credential (API key + base URL https://openrouter.ai/api/v1)
3. Create WP Application Password on ornevo.fr (Users → Profile → Application Passwords)
4. Store WP credentials in n8n as HTTP Basic Auth
5. Activate workflow

AI prompt summary:
- FR: Generate SEO article (H1, meta 150-160 chars, H2/H3, 800-1200 words, CTA Ornevo, source link)
- ES: Faithful translation, maintain SEO format, adapt cultural references
- EN: Faithful translation, maintain SEO format, adapt cultural references

Output: All 3 published as DRAFTS on ornevo.fr

## n8n Workflow Building — Lessons Learned

- delegate_task (600s timeout) is too slow for generating complex n8n workflow JSON. Write JSON directly.
- n8n LangChain AI nodes use credential type "openAiApi" even for OpenRouter — just change the base URL.
- WP Application Passwords are per-user. Consider a dedicated WP user for automation.
- YAML config files with special characters (colons, brackets, pipes) in unquoted strings break YAML parsers. Use flat text or JSON format instead.
- Workflow node connections order: parse input → fetch article → extract text → generate FR → parse FR → translate ES+EN (parallel) → publish all 3 (parallel) → respond.

## GitHub Repo

Repo: hdsolanop/ornevo-content (private)
Local: ~/projects/hdsolanop/ornevo-content/
Structure: sources/ scripts/ n8n-workflows/ docs/

Updating: edit files → test → git add -A && git commit && git push

## Troubleshooting

Digest empty output → Check RSS feed URL (some feeds block bots or require specific User-Agent)
n8n webhook 404 → Workflow not activated in n8n
WP publish fails → Check Application Password, ensure permalink structure allows REST API
OpenRouter rate limit → Use free model fallback or upgrade plan
YAML parse errors in configs → Use flat text format or JSON for configs with special characters

## n8n Workflow Building — Approach

For complex n8n workflow JSON generation:
- delegate_task (600s timeout) is too slow — it timed out trying to generate a 17-node workflow
- Preferred approach: write the workflow JSON directly, test by importing into n8n
- n8n LangChain AI nodes use credential type "openAiApi" even for OpenRouter (just change base URL)
- Build workflow incrementally: start with webhook + 1 node, test, then add more
