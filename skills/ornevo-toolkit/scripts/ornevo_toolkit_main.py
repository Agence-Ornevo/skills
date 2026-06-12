#!/usr/bin/env python3
"""
Ornevo Toolkit CLI
==================

Reference CLI for Ornevo agency & freelance tool stack.

Usage:
    python3 ornevo_toolkit_main.py <command> [args...]

Commands:
    overview     Show tool stack overview
    project      Show project details for a project
    setup        Show setup checklist for a tool
    help         Show this help

Examples:
    ornevo-toolkit overview
    ornevo-toolkit project "Gyptech Phase 0"
    ornevo-toolkit setup n8n
"""

import argparse
import sys
from pathlib import Path


def run_overview(args):
    """Show tool stack overview."""
    print("🏢 ORNEVO TOOL STACK OVERVIEW")
    print("=" * 50)
    print("""
Agency Operations:
  • n8n              — Workflow automation (ornevo.pro)
  • Figma            — Design system & prototyping
  • OpenProject      — Project management
  • Mattermost       — Team communication
  • Bitrix24         — CRM & billing
  • Brevo            — Email marketing
  • Shopify          — E-commerce clients
  • Himalaya         — Email CLI (Gmail)

Freelance / SCM Analytics:
  • Power BI         — Kings Pastry dashboards
  • DAX Patterns     — Service & Fulfillment KPIs
  • n8n              — Digest pipeline
  • Figma            — Client presentations

Project Conventions:
  • ~/projects/ornevo/        — Agency projects
  • ~/projects/hdsolanop/     — Personal/freelance
  • ~/.hermes/TODO-*.md       — Pending setup items
""")
    return "Overview displayed"


def run_project(args):
    """Show project details."""
    project_name = args.project_name
    print(f"📁 PROJECT: {project_name}")
    print("=" * 50)
    
    projects = {
        "Gyptech Phase 0": {
            "repo": "hdsolanop/gyptech_phase_0",
            "path": "~/projects/hdsolanop/gyptech_phase_0",
            "status": "Phase 2 active",
            "focus": "EcomOps + TechPM/Applaudo CVs, LinkedIn banner"
        },
        "Management": {
            "repo": "hdsolanop/management",
            "path": "~/projects/hdsolanop/management",
            "status": "Active",
            "focus": "CVs, LinkedIn banner (4 versions), LinkedIn audit"
        },
        "Kings Pastry D02": {
            "repo": "hdsolanop/Kings-pastry",
            "path": "~/projects/hdsolanop/Kings-pastry/D02_Service_Fulfillment",
            "status": "Base KPIs built, Latest Month measures pending",
            "focus": "Service & Fulfillment KPIs (OTIF, Fill Rate, Stockout)"
        },
        "Gyptech GT Central": {
            "repo": "hdsolanop/gyptech-gt-central",
            "path": "~/projects/hdsolanop/gyptech-gt-central",
            "status": "Active",
            "focus": "Central platform"
        },
        "Ornevo Accessibility": {
            "repo": "hdsolanop/ornevo-accessibility-eaa",
            "path": "~/projects/hdsolanop/ornevo-accessibility-eaa",
            "status": "Active",
            "focus": "EAA compliance"
        },
    }
    
    if project_name in projects:
        p = projects[project_name]
        print(f"Repo:      {p['repo']}")
        print(f"Path:      {p['path']}")
        print(f"Status:    {p['status']}")
        print(f"Focus:     {p['focus']}")
    else:
        print(f"Project '{project_name}' not found.")
        print("\nAvailable projects:")
        for name in projects:
            print(f"  • {name}")
    
    return f"Project '{project_name}' details displayed"


def run_setup(args):
    """Show setup checklist for a tool."""
    tool = args.tool.lower()
    
    setups = {
        "n8n": """
🔧 N8N SETUP CHECKLIST
======================
□ n8n instance running at ornevo.pro
□ Workflows imported from ~/projects/hermes-workflows/skills/ornevo-toolkit/references/n8n-workflows/
□ Credentials configured:
  - Bitrix24 webhook
  - Brevo API
  - Figma PAT
  - Shopify credentials
  - Mattermost bot token
□ Webhook URLs configured in external services
□ Test workflows: digest pipeline, deploy-notify, email processor
        """,
        "figma": """
🎨 FIGMA SETUP CHECKLIST
========================
□ Figma PAT generated (expires Aug 30, 2026)
□ Team library published: Ornevo Design System
□ Components: Buttons, Forms, Tables, Navigation
□ Design tokens synced: colors, spacing, typography
□ File structure: Design System / Components / Client Projects
        """,
        "mattermost": """
💬 MATTERMOST SETUP CHECKLIST
=============================
□ Server running at mattermost.ornevo.pro
□ Bot account created: hermes-gw
□ PAT generated for hermes-gw
□ Channels: #deployments, #alerts, #general
□ Webhooks: deploy-notify, digest-pipeline
□ Integration with n8n for notifications
        """,
        "bitrix24": """
📊 BITRIX24 SETUP CHECKLIST
===========================
□ CRM configured: Deals, Contacts, Companies
□ Webhook for n8n integration
□ Invoice templates
□ Deal stages: Lead → Qualified → Proposal → Negotiation → Won
□ Automation rules for deal progression
        """,
        "brevo": """
📧 BREVO SETUP CHECKLIST
========================
□ API key generated
□ Contact lists: Clients, Leads, Newsletter
□ Email templates: Welcome, Proposal, Invoice, Newsletter
□ Automation: Welcome series, Re-engagement
□ Transactional: Invoice emails, System notifications
        """,
    }
    
    if tool in setups:
        print(setups[tool])
    else:
        print(f"Tool '{tool}' not found.")
        print("\nAvailable tools: n8n, figma, mattermost, bitrix24, brevo")
    
    return f"Setup checklist for {tool} displayed"


def run_help(args):
    """Show help."""
    parser = create_parser()
    parser.print_help()


def create_parser():
    parser = argparse.ArgumentParser(
        prog="ornevo-toolkit",
        description="Ornevo Agency & Freelance Tool Stack CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Commands:
    overview          Show tool stack overview
    project <name>    Show project details
    setup <tool>      Show setup checklist for tool
    help              Show this help

Examples:
    ornevo-toolkit overview
    ornevo-toolkit project "Gyptech Phase 0"
    ornevo-toolkit setup n8n
    ornevo-toolkit setup figma
"""
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command")
    
    p_overview = subparsers.add_parser("overview", help="Show tool stack overview")
    p_overview.set_defaults(func=run_overview)
    
    p_project = subparsers.add_parser("project", help="Show project details")
    p_project.add_argument("project_name", nargs="?", help="Project name")
    p_project.set_defaults(func=run_project)
    
    p_setup = subparsers.add_parser("setup", help="Show setup checklist for a tool")
    p_setup.add_argument("tool", nargs="?", help="Tool name (n8n, figma, mattermost, bitrix24, brevo)")
    p_setup.set_defaults(func=run_setup)
    
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