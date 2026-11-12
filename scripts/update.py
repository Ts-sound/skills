#!/usr/bin/env python3
"""Check and pull updates from sources/ submodules."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import (ensure_dirs, read_csv, SUB_REPO_CSV, SUB_REPO_FIELDS,
                 get_current_commit, get_branch, is_git_repo, pull_submodule, add_repo_csv)
from datetime import date


def main():
    ensure_dirs()
    repos = read_csv(SUB_REPO_CSV, SUB_REPO_FIELDS)

    if not repos:
        print("No sources registered. Use add_source.py first.")
        return 1

    updated = []
    skipped = []
    for repo in repos:
        if repo.get("status") != "active":
            continue

        repo_name = repo["repo_name"]
        source_path = Path(__file__).resolve().parent.parent / "sources" / repo_name

        if not source_path.exists():
            print(f"Missing: {source_path}")
            skipped.append(repo_name)
            continue

        if not is_git_repo(source_path):
            print(f"Not initialized: {source_path} (run: git submodule update --init)")
            skipped.append(repo_name)
            continue

        old_commit = get_current_commit(source_path)
        try:
            has_update = pull_submodule(source_path, repo.get("branch") or "main")
        except RuntimeError as e:
            print(f"Failed: {repo_name}: {e}")
            skipped.append(repo_name)
            continue
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
    elif skipped:
        print(f"\n{len(skipped)} repos skipped (missing/not initialized/error).")
        return 1
    else:
        print("\nAll repos up-to-date.")

    return 0


if __name__ == "__main__":
    sys.exit(main())
