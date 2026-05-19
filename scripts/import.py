#!/usr/bin/env python3
"""Parse confirmed skills from report, write to 3rd-skills.csv, and copy to skills/<category>/."""

import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import ensure_dirs, add_skill_csv, copy_skill, SOURCES_DIR

VALID_CATEGORIES = {"core", "engineering", "planning", "productivity", "project-mgmt", "learning"}


def parse_confirmed_report(report_path: Path) -> list:
    """Parse a markdown report and extract confirmed skills."""
    content = report_path.read_text(encoding="utf-8")
    confirmed = []

    # Match table rows with ✅ in confirmation column
    # Format: | ID | Skill | Description | Score | Category | ✅ |
    pattern = r"\|\s*(\d+)\s*\|\s*([\w-]+)\s*\|[^|]*\|\s*[\d-]+\s*\|\s*([\w-]+)\s*\|\s*✅\s*\|"

    for match in re.finditer(pattern, content):
        skill_id = int(match.group(1))
        skill_name = match.group(2)
        category = match.group(3)

        if category not in VALID_CATEGORIES:
            print(f"Warning: Invalid category '{category}' for skill '{skill_name}', using 'productivity'")
            category = "productivity"

        confirmed.append({
            "id": skill_id,
            "name": skill_name,
            "category": category,
        })

    return confirmed


def find_source_repo(skill_name: str) -> Path:
    """Find which source repo contains a skill."""
    for source in SOURCES_DIR.iterdir():
        if not source.is_dir():
            continue
        skill_dir = source / "skills" / skill_name
        if skill_dir.exists():
            return source
        for md in source.rglob("SKILL.md"):
            if md.parent.name == skill_name:
                return source
    return None


def main():
    ensure_dirs()

    if len(sys.argv) < 2:
        print("Usage: import.py <report.md>")
        print("Example: import.py docs/reports/anthropics-skills.md")
        return 1

    report_path = Path(sys.argv[1])
    if not report_path.exists():
        print(f"Report not found: {report_path}")
        return 1

    confirmed = parse_confirmed_report(report_path)
    if not confirmed:
        print("No confirmed skills found. Mark skills with ✅ in the report.")
        return 0

    source_name = report_path.stem

    for skill in confirmed:
        source_repo = find_source_repo(skill["name"])
        if not source_repo:
            print(f"Warning: Source repo not found for skill '{skill['name']}'")
            continue

        # Find actual source_path
        actual_path = skill.get("source_path", "")
        if not actual_path:
            for md in source_repo.rglob("SKILL.md"):
                if md.parent.name == skill["name"]:
                    actual_path = str(md.parent.relative_to(source_repo))
                    break
        if not actual_path:
            print(f"Warning: Skill '{skill['name']}' not found in source '{source_name}'")
            continue

        src = source_repo / actual_path
        if not src.exists():
            print(f"Warning: Skill path '{actual_path}' not found in source '{source_name}'")
            continue

        add_skill_csv(skill["name"], skill["category"], source_name, actual_path)
        copy_skill(source_repo, actual_path, skill["category"])
        print(f"Imported: {skill['name']} -> skills/{skill['category']}/")

    print(f"\n{len(confirmed)} skills imported successfully.")
    print(f"Updated: data/3rd-skills.csv")

    return 0


if __name__ == "__main__":
    sys.exit(main())
