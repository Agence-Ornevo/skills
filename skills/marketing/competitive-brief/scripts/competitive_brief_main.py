#!/usr/bin/env python3
"""
Entry point for /competitive-brief slash command.
Loads the competitive-brief skill and outputs its guidance for the agent.
"""
import sys
from pathlib import Path

def main():
    skill_dir = Path(__file__).parent.parent
    skill_md = skill_dir / "SKILL.md"
    
    if not skill_md.exists():
        print("❌ SKILL.md not found")
        sys.exit(1)
    
    content = skill_md.read_text(encoding="utf-8")
    
    # Extract content after frontmatter
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 3:
            content = parts[2].strip()
    
    print(content)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        print(f"\n--- User Arguments:  ---\n")
    main()
