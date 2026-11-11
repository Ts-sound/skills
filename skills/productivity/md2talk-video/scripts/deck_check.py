#!/usr/bin/env python3
"""Stage 0 deck audit: is this Markdown a standard PPT deck, not an article?

The pipeline only parses. Whether the pages read like slides is a separate
question, and it is cheaper to answer here than after TTS and rendering:

    python scripts/deck_check.py <workspace>/input.md

Rules are deliberately about deck mechanics, not taste:

* a declared deck needs a cover first, an agenda second, a closing last;
* a content page carries one message: 2-5 short bullets, no paragraphs;
* every page has a 40-220 character speech (the video needs narration);
* total 10-24 pages, so it stays a talk rather than a document.

Page kinds come from `<!-- kind: cover|agenda|section|content|cards|data|
closing -->` right after the `###` heading. Legacy decks without markers only
get a warning; marked decks are checked strictly.
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from md_parse import parse

BULLET_SOFT = 26
BULLET_HARD = 32
TITLE_SOFT = 24
TITLE_HARD = 30
SPEECH_MIN = 40
SPEECH_MAX = 220
SECTION_TITLE_MAX = 16
SECTION_SPEECH_MIN = 15
SECTION_SPEECH_MAX = 46


def _issue(level: str, page: dict | None, message: str) -> dict:
    return {
        "level": level,
        "page": page["id"] if page else "",
        "title": page["title"] if page else "",
        "message": message,
    }


def audit(parsed: dict) -> list[dict]:
    pages = parsed["pages"]
    issues: list[dict] = []
    kinded = any(p.get("kind", "content") != "content" for p in pages)

    if not 10 <= len(pages) <= 24:
        issues.append(_issue("error", None, f"页数 {len(pages)}，标准 deck 应在 10-24 页"))
    if not kinded:
        issues.append(_issue(
            "warn", None,
            "没有任何页面声明 kind；建议 cover/agenda/content/closing 成组使用",
        ))
    else:
        if pages[0].get("kind") != "cover":
            issues.append(_issue("error", pages[0], "第一页必须是 cover"))
        if len(pages) > 1 and pages[1].get("kind") != "agenda":
            issues.append(_issue("error", pages[1], "第二页必须是 agenda"))
        if pages[-1].get("kind") != "closing":
            issues.append(_issue("error", pages[-1], "最后一页必须是 closing"))

    seen: dict[str, str] = {}
    for p in pages:
        kind = p.get("kind", "content")
        bullets = [b for b in p.get("outline", []) if b.strip()]
        title = p.get("title", "")
        speech = p.get("speech", "")

        if title in seen:
            issues.append(_issue("warn", p, f"标题与 {seen[title]} 重复"))
        seen[title] = p["id"]

        if len(title) > TITLE_HARD:
            issues.append(_issue("error", p, f"标题 {len(title)} 字，超过 {TITLE_HARD}"))
        elif len(title) > TITLE_SOFT:
            issues.append(_issue("warn", p, f"标题 {len(title)} 字，建议 ≤ {TITLE_SOFT}"))

        if speech and kind != "section" and not SPEECH_MIN <= len(speech) <= SPEECH_MAX:
            issues.append(_issue(
                "warn", p, f"演讲稿 {len(speech)} 字，建议 {SPEECH_MIN}-{SPEECH_MAX}",
            ))

        if kind == "section":
            if len(title) > SECTION_TITLE_MAX:
                issues.append(_issue(
                    "warn", p, f"过渡页标题 {len(title)} 字，建议 ≤ {SECTION_TITLE_MAX}",
                ))
            if bullets:
                issues.append(_issue(
                    "warn", p, "过渡页不放大纲，过渡句写进演讲稿",
                ))
            if not SECTION_SPEECH_MIN <= len(speech) <= SECTION_SPEECH_MAX:
                issues.append(_issue(
                    "warn", p,
                    f"过渡页演讲稿 {len(speech)} 字，建议 "
                    f"{SECTION_SPEECH_MIN}-{SECTION_SPEECH_MAX}",
                ))
        elif kind == "cover":
            if len(bullets) > 2:
                issues.append(_issue("warn", p, "cover 最多 2 行副标题"))
        elif kind == "agenda":
            if not 4 <= len(bullets) <= 8:
                issues.append(_issue("error", p, f"agenda 需要 4-8 条，当前 {len(bullets)}"))
        elif kind == "closing":
            if len(bullets) > 3:
                issues.append(_issue("warn", p, "closing 最多 3 条"))
        else:
            if not bullets:
                issues.append(_issue("error", p, "内容页没有大纲要点"))
            elif len(bullets) > 6:
                issues.append(_issue("error", p, f"要点 {len(bullets)} 条，超过 6"))
            elif len(bullets) == 1:
                issues.append(_issue("warn", p, "只有 1 条要点，页面偏空"))
            for b in bullets:
                if len(b) > BULLET_HARD:
                    issues.append(_issue("error", p, f"要点 {len(b)} 字：{b[:18]}…"))
                elif len(b) > BULLET_SOFT:
                    issues.append(_issue("warn", p, f"要点 {len(b)} 字，建议 ≤ {BULLET_SOFT}"))
                if b.endswith("。") and len(b) > 18:
                    issues.append(_issue("warn", p, f"要点像整句，删句号：{b[:18]}…"))

    return issues


def render(parsed: dict, issues: list[dict]) -> str:
    errors = sum(1 for i in issues if i["level"] == "error")
    warns = sum(1 for i in issues if i["level"] == "warn")
    pages = parsed["pages"]
    lines = [
        f"DECK CHECK  {parsed.get('source', '')}",
        f"章节 {len(parsed['chapters'])} · 页 {len(pages)} · "
        f"演讲稿 {sum(p['speech_chars'] for p in pages)} 字",
    ]
    for i in issues:
        where = f"{i['page']} {i['title']}".strip()
        lines.append(f"[{i['level'].upper()}] {where} — {i['message']}" if where
                     else f"[{i['level'].upper()}] {i['message']}")
    lines.append(f"SUMMARY errors={errors} warnings={warns}")
    return "\n".join(lines)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_md")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    parsed = parse(Path(args.input_md))
    issues = audit(parsed)
    if args.json:
        print(json.dumps({"issues": issues}, ensure_ascii=False, indent=2))
    else:
        print(render(parsed, issues))
    return 1 if any(i["level"] == "error" for i in issues) else 0


if __name__ == "__main__":
    raise SystemExit(main())
