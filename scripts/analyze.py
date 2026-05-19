#!/usr/bin/env python3
"""Analyze skills in a source repository and generate a report with confirmation column."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from lib import ensure_dirs, discover_skills, SOURCES_DIR, REPORTS_DIR

CATEGORY_HINTS = {
    "api": "engineering",
    "builder": "engineering",
    "testing": "engineering",
    "frontend": "engineering",
    "mcp": "engineering",
    "debug": "engineering",
    "test": "engineering",
    "doc": "productivity",
    "pdf": "productivity",
    "docx": "productivity",
    "pptx": "productivity",
    "xlsx": "productivity",
    "spreadsheet": "productivity",
    "skill-creator": "core",
    "theme": "productivity",
    "art": "productivity",
    "canvas": "productivity",
    "gif": "productivity",
    "comms": "productivity",
    "brand": "productivity",
}


def guess_category(skill_name: str, description: str) -> str:
    """Guess the best category for a skill."""
    combined = (skill_name + " " + description).lower()
    for keyword, cat in CATEGORY_HINTS.items():
        if keyword in combined:
            return cat
    return "productivity"


def generate_report(source_name: str, skills: list) -> str:
    """Generate a markdown report with confirmation column."""
    lines = [
        f"# {source_name} Skills 调研报告",
        "",
        f"**源仓库**: https://github.com/{source_name}",
        f"**分析日期**: __auto__",
        f"**Skills 总数**: {len(skills)}",
        "",
        "## Skills 清单",
        "",
        "请在**确认**列填入 `✅` 引入，或留空跳过。可修改**分类**列。",
        "",
        "| ID | Skill | 描述 | 推荐度 | 建议分类 | 确认 |",
        "|----|-------|------|--------|----------|------|",
    ]

    for i, s in enumerate(skills, 1):
        cat = guess_category(s["name"], s["description"])
        score = rate_skill(s["name"], s["description"])
        desc = s["description"][:100]
        lines.append(f"| {i} | {s['name']} | {desc} | {score} | {cat} | |")

    lines.append("")
    return "\n".join(lines)


def rate_skill(name: str, description: str) -> int:
    """Rate a skill from 1-5 based on generality and usefulness."""
    general_keywords = ["api", "builder", "testing", "frontend", "doc", "pdf", "xlsx", "pptx", "docx", "mcp"]
    niche_keywords = ["slack", "gif", "art", "brand", "canvas", "theme", "comms", "internal"]

    combined = (name + " " + description).lower()

    if any(k in combined for k in general_keywords):
        return 5
    if any(k in combined for k in ["webapp", "web-artifacts"]):
        return 4
    if "coauthor" in combined or "co-author" in combined:
        return 4
    if any(k in combined for k in niche_keywords):
        return 2
    return 3


def main():
    ensure_dirs()

    if len(sys.argv) < 2:
        # Analyze all sources
        sources = [d for d in SOURCES_DIR.iterdir() if d.is_dir() and (d / ".git").exists()]
    else:
        sources = [SOURCES_DIR / sys.argv[1]]

    for source in sources:
        if not source.exists():
            print(f"Source not found: {source}")
            continue

        skills = discover_skills(source)
        if not skills:
            print(f"No skills found in {source.name}")
            continue

        report = generate_report(source.name, skills)
        report_path = REPORTS_DIR / f"{source.name}.md"
        report_path.write_text(report, encoding="utf-8")
        print(f"Report saved: {report_path}")
        print(f"Found {len(skills)} skills")

    return 0


if __name__ == "__main__":
    sys.exit(main())
