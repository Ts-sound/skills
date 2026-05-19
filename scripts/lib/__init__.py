"""Common utilities for skills management scripts."""

import csv
import os
import subprocess
from datetime import date, datetime
from pathlib import Path
from typing import List, Dict, Optional


ROOT = Path(__file__).resolve().parent.parent.parent
SOURCES_DIR = ROOT / "sources"
SKILLS_DIR = ROOT / "skills"
DATA_DIR = ROOT / "data"
DOCS_DIR = ROOT / "docs"
REPORTS_DIR = DOCS_DIR / "reports"

SUB_REPO_CSV = DATA_DIR / "sub-repo.csv"
THIRD_SKILLS_CSV = DATA_DIR / "3rd-skills.csv"

SUB_REPO_FIELDS = ["repo_name", "repo_url", "branch", "last_commit", "added_date", "status"]
THIRD_SKILLS_FIELDS = [
    "skill_name", "category", "source_repo", "source_path",
    "imported_date", "modified", "last_sync", "priority"
]

VALID_CATEGORIES = {"core", "engineering", "planning", "productivity", "project-mgmt", "learning"}


def ensure_dirs():
    """Ensure all required directories exist."""
    for d in [SOURCES_DIR, SKILLS_DIR, DATA_DIR, DOCS_DIR, REPORTS_DIR]:
        d.mkdir(parents=True, exist_ok=True)
    for cat in VALID_CATEGORIES:
        (SKILLS_DIR / cat).mkdir(parents=True, exist_ok=True)


# --- CSV helpers ---

def read_csv(path: Path, fields: List[str]) -> List[Dict[str, str]]:
    """Read CSV into list of dicts."""
    if not path.exists():
        return []
    with open(path, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        return list(reader)


def write_csv(path: Path, rows: List[Dict[str, str]], fields: List[str]):
    """Write list of dicts to CSV."""
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def add_repo_csv(repo_name: str, repo_url: str, branch: str, commit: str, added_date: str):
    """Add or update a repo entry in sub-repo.csv."""
    rows = read_csv(SUB_REPO_CSV, SUB_REPO_FIELDS)
    entry = {
        "repo_name": repo_name,
        "repo_url": repo_url,
        "branch": branch,
        "last_commit": commit,
        "added_date": added_date,
        "status": "active",
    }
    rows = [r for r in rows if r.get("repo_name") != repo_name]
    rows.append(entry)
    write_csv(SUB_REPO_CSV, rows, SUB_REPO_FIELDS)


def add_skill_csv(skill_name: str, category: str, source_repo: str, source_path: str):
    """Add or update a skill entry in 3rd-skills.csv."""
    rows = read_csv(THIRD_SKILLS_CSV, THIRD_SKILLS_FIELDS)
    today = date.today().isoformat()
    entry = {
        "skill_name": skill_name,
        "category": category,
        "source_repo": source_repo,
        "source_path": source_path,
        "imported_date": today,
        "modified": "false",
        "last_sync": today,
        "priority": "1",
    }
    rows = [r for r in rows if r.get("skill_name") != skill_name]
    rows.append(entry)
    write_csv(THIRD_SKILLS_CSV, rows, THIRD_SKILLS_FIELDS)


# --- Git helpers ---

def git(*args: str, cwd: Optional[Path] = None) -> str:
    """Run a git command and return stdout."""
    cmd = ["git"] + list(args)
    result = subprocess.run(cmd, capture_output=True, text=True, cwd=cwd or ROOT)
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed: {result.stderr.strip()}")
    return result.stdout.strip()


def git_clone_submodule(url: str, path: Path) -> tuple:
    """Add a git submodule and return the repo name and commit."""
    repo_name = path.name
    git("submodule", "add", url, str(path))
    # Get commit
    commit = git("rev-parse", "HEAD", cwd=path)[:8]
    return repo_name, commit


def get_current_commit(path: Path) -> str:
    """Get short commit hash for a submodule."""
    return git("rev-parse", "HEAD", cwd=path)[:8]


def get_branch(path: Path) -> str:
    """Get current branch for a submodule."""
    return git("rev-parse", "--abbrev-ref", "HEAD", cwd=path)


def pull_submodule(path: Path) -> bool:
    """Pull updates for a submodule. Returns True if updated."""
    old_commit = get_current_commit(path)
    git("pull", cwd=path)
    new_commit = get_current_commit(path)
    return old_commit != new_commit


# --- Skill analysis ---

def discover_skills(source_dir: Path) -> List[Dict]:
    """Discover all skills in a source directory."""
    skills = []
    skills_dir = source_dir / "skills"
    if not skills_dir.is_dir():
        return skills
    for entry in sorted(skills_dir.iterdir()):
        if not entry.is_dir():
            continue
        skill_md = entry / "SKILL.md"
        if not skill_md.exists():
            continue
        info = parse_skill_md(skill_md)
        info["source_path"] = str(entry.relative_to(source_dir))
        info["dir_name"] = entry.name
        skills.append(info)
    return skills


def parse_skill_md(path: Path) -> Dict:
    """Parse frontmatter from SKILL.md."""
    with open(path, encoding="utf-8") as f:
        content = f.read()
    name = path.parent.name
    description = ""
    if content.startswith("---"):
        parts = content.split("---", 2)
        if len(parts) >= 2:
            frontmatter = parts[1].strip()
            for line in frontmatter.split("\n"):
                if line.startswith("name:"):
                    name = line.split(":", 1)[1].strip()
                elif line.startswith("description:"):
                    description = line.split(":", 1)[1].strip().strip('"')
    return {"name": name, "description": description[:120]}


def copy_skill(source_dir: Path, skill_dir_name: str, category: str):
    """Copy a skill from source to skills/<category>/."""
    src = source_dir / "skills" / skill_dir_name
    dst = SKILLS_DIR / category / skill_dir_name
    if dst.exists():
        import shutil
        shutil.rmtree(dst)
    import shutil
    shutil.copytree(src, dst)
