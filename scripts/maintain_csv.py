#!/usr/bin/env python3
"""Maintain CSV data files under data/."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import ensure_dirs, read_csv, write_csv, SUB_REPO_CSV, SUB_REPO_FIELDS, THIRD_SKILLS_CSV, THIRD_SKILLS_FIELDS


def list_skills():
    """List all registered skills."""
    skills = read_csv(THIRD_SKILLS_CSV, THIRD_SKILLS_FIELDS)
    if not skills:
        print("No skills registered.")
        return
    print(f"{'Skill':<25} {'Category':<15} {'Source':<25} {'Date':<12}")
    print("-" * 77)
    for s in skills:
        print(f"{s['skill_name']:<25} {s['category']:<15} {s['source_repo']:<25} {s['imported_date']:<12}")


def list_sources():
    """List all registered sources."""
    repos = read_csv(SUB_REPO_CSV, SUB_REPO_FIELDS)
    if not repos:
        print("No sources registered.")
        return
    print(f"{'Repo':<25} {'URL':<50} {'Branch':<10} {'Commit':<10} {'Status':<10}")
    print("-" * 105)
    for r in repos:
        print(f"{r['repo_name']:<25} {r['repo_url']:<50} {r['branch']:<10} {r['last_commit']:<10} {r['status']:<10}")


def remove_skill(skill_name: str):
    """Remove a skill from registry."""
    import shutil
    skills = read_csv(THIRD_SKILLS_CSV, THIRD_SKILLS_FIELDS)
    for s in skills:
        if s["skill_name"] == skill_name:
            cat = s["category"]
            skill_dir = Path(__file__).resolve().parent.parent / "skills" / cat / skill_name
            if skill_dir.exists():
                shutil.rmtree(skill_dir)
                print(f"Removed: skills/{cat}/{skill_name}")
    skills = [s for s in skills if s["skill_name"] != skill_name]
    write_csv(THIRD_SKILLS_CSV, skills, THIRD_SKILLS_FIELDS)
    print(f"Unregistered: {skill_name}")


def main():
    ensure_dirs()

    if len(sys.argv) < 2:
        print("Usage: maintain_csv.py <command> [args]")
        print("Commands:")
        print("  list-skills          List registered skills")
        print("  list-sources         List registered sources")
        print("  remove-skill <name>  Remove a skill")
        return 1

    cmd = sys.argv[1]

    if cmd == "list-skills":
        list_skills()
    elif cmd == "list-sources":
        list_sources()
    elif cmd == "remove-skill":
        if len(sys.argv) < 3:
            print("Usage: maintain_csv.py remove-skill <skill-name>")
            return 1
        remove_skill(sys.argv[2])
    else:
        print(f"Unknown command: {cmd}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
