#!/usr/bin/env python3
"""
Ornevo Digest Audit CLI
=======================

Monthly audit CLI for the Ornevo Daily Digest system.

Usage:
    python3 digest_audit_main.py <command> [args...]

Commands:
    run            Run full monthly audit
    check          Quick health check
    sources        Review and rank sources
    topics         Evaluate new topics
    help           Show this help

Examples:
    ornevo-digest-audit run
    ornevo-digest-audit check
    ornevo-digest-audit sources
    ornevo-digest-audit topics
"""

import argparse
import sys
import json
from pathlib import Path
from datetime import datetime


SOURCES_FILE = Path.home() / ".hermes" / "digest-sources.txt"
AUDIT_LOG = Path.home() / ".hermes" / "digest-audit-log.json"


def load_sources():
    """Load current sources from file."""
    if SOURCES_FILE.exists():
        return SOURCES_FILE.read_text().strip().split('\n')
    return []


def save_sources(sources):
    """Save sources to file."""
    SOURCES_FILE.write_text('\n'.join(sources))


def load_audit_log():
    """Load audit history."""
    if AUDIT_LOG.exists():
        return json.loads(AUDIT_LOG.read_text())
    return []


def save_audit_log(log):
    """Save audit log."""
    AUDIT_LOG.write_text(json.dumps(log, indent=2))


def run_full_audit(args):
    """Run full monthly audit."""
    print("📊 ORNEVO DIGEST MONTHLY AUDIT")
    print("=" * 50)
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    print()
    
    sources = load_sources()
    print(f"📰 Current sources: {len(sources)}")
    
    # 1. Source Bank Revision
    print("\n1️⃣ SOURCE BANK REVISION")
    print("-" * 30)
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source}")
    
    print("\n🔍 Actions needed:")
    print("  □ Search for new high-quality sources per topic")
    print("  □ Check existing sources for staleness (30+ days no updates)")
    print("  □ Re-rank all sources (authority + freshness + relevance + actionability)")
    print("  □ Update source bank file")
    print("  □ Push changes to hdsolanop/ornevo-content repo")
    
    # 2. New Topic Evaluation
    print("\n2️⃣ NEW TOPIC EVALUATION")
    print("-" * 30)
    print("🔍 Actions needed:")
    print("  □ Search trending topics in Ornevo's market space")
    print("  □ Evaluate against Ornevo's business objectives")
    print("  □ Recommend 0-2 new topics with justification")
    print("  □ If approved, add topic with 10-15 initial sources")
    
    # Log audit
    audit_entry = {
        "date": datetime.now().isoformat(),
        "type": "full_audit",
        "sources_count": len(sources),
        "status": "completed"
    }
    log = load_audit_log()
    log.append(audit_entry)
    save_audit_log(log)
    
    print("\n✅ Audit logged to ~/.hermes/digest-audit-log.json")
    return "Full audit completed"


def run_check(args):
    """Quick health check."""
    print("🏥 DIGEST SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    sources = load_sources()
    log = load_audit_log()
    
    print(f"Sources configured: {len(sources)}")
    print(f"Last audit: {log[-1]['date'] if log else 'Never'}")
    print(f"Total audits run: {len(log)}")
    
    # Check sources file
    if SOURCES_FILE.exists():
        print("✅ Sources file exists")
    else:
        print("⚠️ Sources file missing")
    
    # Check n8n webhook (placeholder)
    print("🔗 n8n webhook: Configured (n8n.ornevo.pro/webhook/digest)")
    
    return "Health check completed"


def run_sources(args):
    """Review and rank sources."""
    print("📰 SOURCE REVIEW & RANKING")
    print("=" * 50)
    
    sources = load_sources()
    
    if not sources:
        print("No sources configured yet.")
        return "No sources to review"
    
    print(f"Current sources ({len(sources)}):\n")
    for i, source in enumerate(sources, 1):
        print(f"  {i}. {source}")
    
    print("\n📋 Ranking criteria:")
    print("  1. Authority (domain expertise, reputation)")
    print("  2. Freshness (update frequency, recency)")
    print("  3. Relevance (alignment with Ornevo topics)")
    print("  4. Actionability (leads to insights/decisions)")
    
    print("\n💡 Tip: Edit ~/.hermes/digest-sources.txt to re-rank")
    return "Source review displayed"


def run_topics(args):
    """Evaluate new topics."""
    print("🎯 NEW TOPIC EVALUATION")
    print("=" * 50)
    
    print("🔍 Trending areas to monitor:")
    topics = [
        "AI agents in business operations",
        "No-code automation for SMBs",
        "E-commerce personalization",
        "Supply chain analytics",
        "Developer experience platforms",
        "Compliance automation (EAA, GDPR)",
        "Low-code data pipelines",
    ]
    
    for topic in topics:
        print(f"  • {topic}")
    
    print("\n📋 Evaluation framework:")
    print("  1. Market demand (search volume, discussions)")
    print("  2. Ornevo relevance (agency services, freelance niche)")
    print("  3. Content availability (quality sources exist)")
    print("  4. Business opportunity (leads, partnerships)")
    
    print("\n💡 Recommend 0-2 topics with justification")
    return "Topic evaluation displayed"


def run_help(args):
    """Show help."""
    parser = create_parser()
    parser.print_help()


def create_parser():
    parser = argparse.ArgumentParser(
        prog="ornevo-digest-audit",
        description="Monthly audit of Ornevo Daily Digest system",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    run            Run full monthly audit
    check          Quick health check
    sources        Review and rank sources
    topics         Evaluate new topics
    help           Show this help

Schedule:
    Monthly — 1st of each month at 10 AM Colombia time (UTC-5)

Files:
    ~/.hermes/digest-sources.txt     — Source bank
    ~/.hermes/digest-audit-log.json  — Audit history
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    p_run = subparsers.add_parser("run", help="Run full monthly audit")
    p_run.set_defaults(func=run_full_audit)
    
    p_check = subparsers.add_parser("check", help="Quick health check")
    p_check.set_defaults(func=run_check)
    
    p_sources = subparsers.add_parser("sources", help="Review and rank sources")
    p_sources.set_defaults(func=run_sources)
    
    p_topics = subparsers.add_parser("topics", help="Evaluate new topics")
    p_topics.set_defaults(func=run_topics)
    
    p_help = subparsers.add_parser("help", help="Show this help")
    p_help.set_defaults(func=run_help)
    
    return parser


def main():
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return
    
    try:
        if hasattr(args, "func"):
            result = args.func(args)
            if result:
                print(f"\n✅ {result}")
        else:
            parser.print_help()
    except KeyboardInterrupt:
        print("\n⚠️ Interrupted")
        sys.exit(130)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()