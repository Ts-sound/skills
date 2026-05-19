#!/usr/bin/env python3
"""Check and pull updates from sources/ submodules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import ensure_dirs, read_csv, SUB_REPO_CSV, SUB_REPO_FIELDS, get_current_commit, get_branch, pull_submodule, add_repo_csv
from datetime import date


def main():
    ensure_dirs()
    repos = read_csv(SUB_REPO_CSV, SUB_REPO_FIELDS)

    if not repos:
        print("No sources registered. Use add_source.py first.")
        return 1

    updated = []
    for repo in repos:
        if repo.get("status") != "active":
            continue

        repo_name = repo["repo_name"]
        source_path = Path(__file__).resolve().parent.parent / "sources" / repo_name

        if not source_path.exists():
            print(f"Missing: {source_path}")
            continue

        old_commit = get_current_commit(source_path)
        has_update = pull_submodule(source_path)
        new_commit = get_current_commit(source_path)
        branch = get_branch(source_path)

        if has_update:
            updated.append(repo_name)
            print(f"Updated: {repo_name} {old_commit} -> {new_commit}")
        else:
            print(f"Up-to-date: {repo_name} ({new_commit})")

        add_repo_csv(repo_name, repo["repo_url"], branch, new_commit, repo["added_date"])

    if updated:
        print(f"\n{len(updated)} repos updated. Run diff.py to analyze changes.")
    else:
        print("\nAll repos up-to-date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
