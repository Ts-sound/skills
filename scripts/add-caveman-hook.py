#!/usr/bin/env python3
"""Add SessionStart hook to activate /caveman on Claude Code startup.

Usage:
  python3 add-caveman-hook.py --claude [--global|--project] [--dry-run]

  --claude   : Claude Code mode (required, only Claude Code supported)
  --global   : write to ~/.claude/settings.json (default)
  --project  : write to .claude/settings.local.json
  --dry-run  : print what would be written, don't modify files
"""

import json
import sys
from pathlib import Path


HOOK_ENTRY = {
    "matcher": "startup",
    "hooks": [
        {
            "type": "command",
            "command": "echo '/caveman'",
        }
    ],
}


def main():
    scope = "global"
    dry_run = False
    claude_mode = False

    for arg in sys.argv[1:]:
        if arg == "--claude":
            claude_mode = True
        elif arg == "--global":
            scope = "global"
        elif arg == "--project":
            scope = "project"
        elif arg == "--dry-run":
            dry_run = True
        else:
            print(f"Unknown arg: {arg}")
            sys.exit(1)

    if not claude_mode:
        print("Error: --claude is required. Only Claude Code is supported.")
        print("Usage: python3 add-caveman-hook.py --claude [--global|--project] [--dry-run]")
        sys.exit(1)

    if scope == "global":
        target = Path.home() / ".claude" / "settings.json"
    else:
        target = Path.cwd() / ".claude" / "settings.local.json"

    target.parent.mkdir(parents=True, exist_ok=True)

    # Load or init config
    if target.exists():
        config = json.loads(target.read_text())
    else:
        config = {}

    # Deep-merge hook
    hooks = config.setdefault("hooks", {})
    session_start = hooks.setdefault("SessionStart", [])

    # Deduplicate: skip if identical matcher+command already exists
    existing_keys = set()
    for entry in session_start:
        for h in entry.get("hooks", []):
            existing_keys.add((entry.get("matcher", ""), h.get("command", "")))

    key = (HOOK_ENTRY["matcher"], HOOK_ENTRY["hooks"][0]["command"])
    if key in existing_keys:
        print(f"Hook already exists in {target}, nothing to do.")
        return

    session_start.append(HOOK_ENTRY)

    if dry_run:
        print("=== DRY RUN ===")
        print(f"Target: {target}")
        print(json.dumps(config, indent=2, ensure_ascii=False))
        return

    target.write_text(json.dumps(config, indent=2, ensure_ascii=False) + "\n")
    print(f"Done. SessionStart hook added to {target}")
    print("Restart Claude Code to activate /caveman on startup.")


if __name__ == "__main__":
    main()
