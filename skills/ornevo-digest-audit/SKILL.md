---
name: ornevo-digest-audit
description: "Monthly audit of the Ornevo Daily Digest system — source review, ranking, new topic evaluation, process improvements."
version: 1.0.0
author: Novum
command: ornevo-digest-audit
entry: scripts/digest_audit_main.py
args_hint: "[run|check|sources|help]"
---

# Ornevo Monthly Digest Audit

## Purpose
Keep the daily digest system sharp by reviewing sources, evaluating new topics, and identifying process improvements.

## Schedule
Monthly — 1st of each month at 10 AM Colombia time (UTC-5)

## Checklist

### 1. Source Bank Revision
- [ ] Read current `~/.hermes/digest-sources.txt`
- [ ] For each topic, search for new high-quality sources
- [ ] Check existing sources for staleness (no updates in 30+ days)
- [ ] Re-rank all sources (authority + freshness + relevance + actionability)
- [ ] Update source bank file
- [ ] Push changes to `hdsolanop/ornevo-content` repo

### 2. New Topic Evaluation
- [ ] Search trending topics in Ornevo's market space
- [ ] Evaluate against Ornevo's business objectives
- [ ] Recommend 0-2 new topics with justification
- [ ] If approved, add topic with 10-15 initial sources

### 3. Process Health Check
- [ ] Run digest script: `python3 ~/.hermes/scripts/digest-generator.py`
- [ ] Check n8n webhook: `curl -s -o /dev/null -w "%{http_code}" https://n8n.ornevo.pro/webhook/generate-blog-article`
- [ ] Review recent Hermes updates for new features
- [ ] Check cron job status: `cronjob(action="list")`

### 4. Deliver Report
- [ ] Sources audit summary (added, removed, re-ranked)
- [ ] New topic recommendations
- [ ] Process improvement suggestions
- [ ] Script + n8n health status

## Target Metrics
- Total sources: 108 → grow toward 200 over time
- Tier 1 sources: maintain 30%+ ratio
- Stale sources: <5% of total
- Digest script: zero errors
- n8n webhook: 200 response

## Files
- Source bank: `~/.hermes/digest-sources.txt`
- Script: `~/.hermes/scripts/digest-generator.py`
- n8n workflow: `~/.hermes/n8n-workflows/blog-article-generator.json`
- Repo: `~/projects/hdsolanop/ornevo-content/`
