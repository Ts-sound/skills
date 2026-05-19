#!/usr/bin/env python3
"""Add a new source repository as a git submodule and register it."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import ensure_dirs, git_clone_submodule, add_repo_csv

CATEGORIES = ["core", "engineering", "planning", "productivity", "project-mgmt", "learning"]


def main():
    if len(sys.argv) < 2:
        print("Usage: add_source.py <git-url> [branch]")
        print("Example: add_source.py https://github.com/anthropics/skills.git")
        return 1

    url = sys.argv[1]
    branch = sys.argv[2] if len(sys.argv) > 2 else "main"

    ensure_dirs()

    # Derive repo name: use owner-repo format to avoid conflicts
    # e.g. https://github.com/anthropics/skills.git -> anthropics-skills
    url_stem = url.rstrip("/").split("/")[-1].replace(".git", "")
    if "/" in url and len(url.split("/")) >= 2:
        owner = url.rstrip("/").split("/")[-2]
        repo_name = f"{owner}-{url_stem}"
    else:
        repo_name = url_stem
    path = Path(__file__).resolve().parent.parent / "sources" / repo_name

    print(f"Adding source: {url}")
    print(f"Path: {path}")

    repo_name, commit = git_clone_submodule(url, path)
    add_repo_csv(repo_name, url, branch, commit, "")
    print(f"Registered {repo_name} in data/sub-repo.csv")

    # Run analyze
    print("\nRunning analyze.py...")
    from subprocess import run
    run([sys.executable, str(Path(__file__).parent / "analyze.py"), repo_name], check=False)

    return 0


if __name__ == "__main__":
    sys.exit(main())
