#!/usr/bin/env python3
"""Compare differences between sources/ and skills/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import ensure_dirs, discover_skills, read_csv, THIRD_SKILLS_CSV, THIRD_SKILLS_FIELDS, SKILLS_DIR


def get_installed_skills():
    """Get all installed skills with their categories."""
    skills = {}
    for cat in SKILLS_DIR.iterdir():
        if not cat.is_dir():
            continue
        for skill_dir in cat.iterdir():
            if (skill_dir / "SKILL.md").exists():
                skills[skill_dir.name] = cat.name
    return skills


def main():
    ensure_dirs()

    sources_dir = Path(__file__).resolve().parent.parent / "sources"
    installed = get_installed_skills()

    for source in sorted(sources_dir.iterdir()):
        if not source.is_dir() or not (source / ".git").exists():
            continue

        skills = discover_skills(source)
        if not skills:
            continue

        print(f"\n=== {source.name} ===")
        new = []
        modified = []

        for s in skills:
            name = s["name"]
            if name not in installed:
                new.append(name)
            else:
                # Check if content differs
                src_file = source / "skills" / s["dir_name"] / "SKILL.md"
                dst_file = SKILLS_DIR / installed[name] / name / "SKILL.md"
                if src_file.exists() and dst_file.exists():
                    if src_file.read_text() != dst_file.read_text():
                        modified.append(name)

        if new:
            print(f"  New: {', '.join(new)}")
        if modified:
            print(f"  Modified: {', '.join(modified)}")
        if not new and not modified:
            print("  No changes")

    return 0


if __name__ == "__main__":
    sys.exit(main())
