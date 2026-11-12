#!/usr/bin/env python3
"""Sync changes from sources/ to skills/ based on 3rd-skills.csv."""

import sys
from pathlib import Path
from datetime import date

sys.path.insert(0, str(Path(__file__).parent))
from lib import (ensure_dirs, read_csv, write_csv, THIRD_SKILLS_CSV,
                 THIRD_SKILLS_FIELDS, copy_skill, SOURCES_DIR, SKILLS_DIR)


def main():
    ensure_dirs()
    skills = read_csv(THIRD_SKILLS_CSV, THIRD_SKILLS_FIELDS)

    if not skills:
        print("No skills registered. Import skills first.")
        return 1

    today = date.today().isoformat()
    synced = 0
    for skill in skills:
        source_repo = skill.get("source_repo", "")
        skill_name = skill.get("skill_name", "")
        category = skill.get("category", "")
        source_path = SOURCES_DIR / source_repo

        if not source_path.exists():
            print(f"Warning: Source '{source_repo}' not found for skill '{skill_name}'")
            continue

        # source_path in CSV is relative to the source repo root
        rel_path = skill.get("source_path") or f"skills/{skill_name}"
        src_skill = source_path / rel_path
        if not src_skill.is_dir():
            print(f"Warning: Skill '{skill_name}' not found at '{rel_path}' in '{source_repo}'")
            continue

        dst_skill = SKILLS_DIR / category / skill_name
        old_exists = dst_skill.exists()

        copy_skill(source_path, rel_path, category)
        synced += 1
        skill["last_sync"] = today

        if old_exists:
            print(f"Updated: {skill_name} ({category})")
        else:
            print(f"New: {skill_name} -> {category}/")

    write_csv(THIRD_SKILLS_CSV, skills, THIRD_SKILLS_FIELDS)
    print(f"\n{synced} skills synced.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
