"""Markdown -> parsed page model.

Source format:
    ## chapter title
    ### page title
    <!-- kind: cover -->
    > speech line 1
    > speech line 2
    - outline bullet

`##` starts a chapter, `###` starts a page (one page = one PPT = one audio +
subtitle unit). Consecutive `>` lines are the speech for that page; every other
body line is outline text fed to the PPT builder. Fenced code blocks and HTML
comments are ignored: they hold examples, not structure or speech.

One comment form is metadata, not example: `<!-- kind: cover|agenda|section|
content|cards|data|closing -->` on a page declares its slide role. It changes
how the bundled PPT renders the page and what `deck_check.py` enforces.
"""

from __future__ import annotations

import re
from pathlib import Path

from paths import PipelineError

CHAPTER_RE = re.compile(r"^##\s+(?!#)(.+?)\s*$")
PAGE_RE = re.compile(r"^###\s+(?!#)(.+?)\s*$")
QUOTE_RE = re.compile(r"^>\s?(.*)$")
BULLET_RE = re.compile(r"^(?:[-*+]|\d+[.)])\s+")
FENCE_RE = re.compile(r"^\s{0,3}(`{3,}|~{3,})")
META_RE = re.compile(r"^<!--\s*(kind|layout)\s*:\s*([a-z-]+)\s*-->$")
SLIDE_KINDS = ("cover", "agenda", "section", "content", "cards", "data", "closing")


def _is_cjk(ch: str) -> bool:
    return "\u3400" <= ch <= "\u9fff" or "\uf900" <= ch <= "\ufaff"


def join_speech(lines: list[str]) -> str:
    """Join blockquote lines; CJK neighbours glue without a space."""
    out = ""
    for raw in lines:
        piece = raw.strip()
        if not piece:
            continue
        if not out:
            out = piece
            continue
        if _is_cjk(out[-1]) or _is_cjk(piece[0]):
            out += piece
        else:
            out += " " + piece
    return out.strip()


def _clean_outline(line: str) -> str:
    text = line.strip()
    text = BULLET_RE.sub("", text)
    return text.strip()


def parse(md_path: Path) -> dict:
    if not md_path.exists():
        raise PipelineError(f"input markdown not found: {md_path}")
    lines = md_path.read_text(encoding="utf-8").splitlines()

    chapters: list[dict] = []
    chapter: dict | None = None
    page: dict | None = None
    counter = 0

    def new_page(title: str) -> dict:
        nonlocal counter
        counter += 1
        return {
            "id": f"p{counter:03d}",
            "title": title,
            "kind": "content",
            "chapter": chapter["title"] if chapter else "",
            "chapter_index": len(chapters),
            "outline": [],
            "code": "",
            "speech": "",
            "_speech_lines": [],
            "_raw_outline": [],
        }

    def flush_page() -> None:
        nonlocal page
        if page is None:
            return
        page["speech"] = join_speech(page.pop("_speech_lines"))
        page["speech_chars"] = len(page["speech"])
        page["speech_missing"] = not page["speech"]
        chapter["pages"].append(page)
        page = None

    def flush_chapter() -> None:
        nonlocal chapter, page
        if chapter is None:
            return
        flush_page()
        loose = [_clean_outline(x) for x in chapter.pop("_loose", []) if x.strip()]
        if not chapter["pages"] and loose:
            # A chapter with prose but no `###`: keep it as one page so nothing
            # the author wrote silently disappears.
            page = new_page(chapter["title"])
            page["outline"] = loose
            page["_raw_outline"] = []
            flush_page()
        if chapter["pages"]:
            chapters.append(chapter)
        chapter = None

    doc_title = ""
    fence = ""       # open fence marker while inside ``` / ~~~ blocks
    fence_lines: list[str] = []   # body of the current fence, when inside a page
    fence_page: dict | None = None
    in_comment = False
    for raw in lines:
        line = raw.rstrip()
        stripped = line.lstrip()
        if not stripped:
            if fence:
                fence_lines.append("")
            continue
        # Code fences are examples. Before a page they are front matter; inside
        # a page they become that page's code sample (one block per page), and
        # never structure or speech.
        if fence:
            if stripped.startswith(fence):
                if fence_page is not None and fence_lines and not fence_page.get("code"):
                    block = "\n".join(fence_lines).rstrip()
                    if block:
                        fence_page["code"] = block
                fence = ""
                fence_lines = []
                fence_page = None
            elif fence_page is not None:
                fence_lines.append(raw.rstrip())
            continue
        if in_comment:
            if "-->" in line:
                in_comment = False
            continue
        if stripped.startswith("<!--"):
            if "-->" in stripped and page is not None:
                meta = META_RE.match(stripped.strip())
                if meta:
                    key, value = meta.group(1), meta.group(2)
                    if key == "kind" and value in SLIDE_KINDS:
                        page["kind"] = value
                    elif key == "layout":
                        page["layout"] = value
            in_comment = "-->" not in stripped
            continue
        fence_match = FENCE_RE.match(line)
        if fence_match:
            fence = fence_match.group(1)[0] * 3
            fence_lines = []
            fence_page = page
            continue
        m = CHAPTER_RE.match(line)
        if m:
            flush_chapter()
            chapter = {"title": m.group(1), "pages": [], "_loose": []}
            continue
        m = PAGE_RE.match(line)
        if m:
            if chapter is None:
                chapter = {"title": "", "pages": [], "_loose": []}
            flush_page()
            page = new_page(m.group(1))
            continue
        if chapter is None:
            # Preamble before the first `##` is front matter, not a page; keep
            # an H1 as the document title only.
            h1 = re.match(r"^#\s+(.+?)\s*$", line)
            if h1 and not doc_title:
                doc_title = h1.group(1)
            continue
        q = QUOTE_RE.match(line.strip())
        if q:
            target = page if page is not None else None
            if target is None:
                # Quote before any `###`: belongs to the implicit chapter page.
                page = new_page(chapter["title"])
                target = page
            target["_speech_lines"].append(q.group(1))
        else:
            cleaned = _clean_outline(line)
            if not cleaned:
                continue
            if page is not None:
                page["outline"].append(cleaned)
            else:
                chapter["_loose"].append(cleaned)

    flush_chapter()

    if not chapters:
        raise PipelineError(
            "input.md 里没有可用的 `## 章节` / `### 子页`；"
            "按「## 章 / ### 页 / > 演讲稿」的格式写，或先跑 --from 1 检查解析"
        )

    pages = [p for ch in chapters for p in ch["pages"]]
    if not pages:
        raise PipelineError("input.md contains no chapters or pages")

    for idx, p in enumerate(pages, 1):
        if p["id"] != f"p{idx:03d}":  # pragma: no cover - defensive
            p["id"] = f"p{idx:03d}"
        p["index"] = idx

    return {
        "source": str(md_path),
        "title": doc_title,
        "chapters": [
            {
                "title": ch["title"],
                "pages": [
                    {
                        k: v
                        for k, v in p.items()
                        if not k.startswith("_") and k not in ("index",)
                    }
                    for p in ch["pages"]
                ],
            }
            for ch in chapters
        ],
        "pages": [
            {k: v for k, v in p.items() if not k.startswith("_")}
            for p in pages
        ],
    }


def iter_pages(parsed: dict) -> list[dict]:
    return parsed["pages"]


def write_script_md(parsed: dict, path: Path) -> None:
    """Read-through script laid out page by page."""
    blocks = ["# 演讲稿通读\n"]
    for ch in parsed["chapters"]:
        if ch["title"]:
            blocks.append(f"\n## {ch['title']}\n")
        for p in ch["pages"]:
            blocks.append(f"\n### {p['id']} · {p['title']}\n")
            if p.get("kind") and p["kind"] != "content":
                blocks.append(f"<!-- kind: {p['kind']} -->\n")
            speech = p["speech"] or "（缺演讲稿）"
            blocks.append(f"> {speech}\n")
            if p["outline"]:
                blocks.append("")
                blocks.extend(f"- {item}" for item in p["outline"])
    path.write_text("\n".join(blocks).rstrip() + "\n", encoding="utf-8")


def write_review_md(parsed: dict, path: Path) -> str:
    pages = parsed["pages"]
    missing = [p for p in pages if p["speech_missing"]]
    total_chars = sum(p["speech_chars"] for p in pages)
    rows = [
        "# Stage 1 审核 · Markdown 解析\n",
        f"- 章节数：{len(parsed['chapters'])}",
        f"- 页数：{len(pages)}",
        f"- 演讲稿总字数：{total_chars}",
        f"- 缺演讲稿页：{len(missing)}",
        "",
        "| 页 | 类型 | 章节 | 标题 | 字数 | 大纲条数 | 状态 |",
        "|---|---|---|---|---|---|---|",
    ]
    for p in pages:
        status = "缺演讲稿" if p["speech_missing"] else "ok"
        rows.append(
            f"| {p['id']} | {p.get('kind', 'content')} | {p['chapter'] or '-'} | "
            f"{p['title']} | {p['speech_chars']} | {len(p['outline'])} | {status} |"
        )
    if missing:
        rows += ["", "## 缺演讲稿页", ""]
        rows += [f"- {p['id']} · {p['title']}" for p in missing]
        rows += ["", "补 `> ` 演讲稿后重跑 `--from 1`，或继续（全自动模式回退为大纲拼接）。"]
    path.write_text("\n".join(rows) + "\n", encoding="utf-8")
    return "\n".join(rows)


def fallback_speech(page: dict) -> str:
    """Used when a page has no speech and review mode is non-interactive."""
    outline = [item.rstrip("。；;") for item in page["outline"]]
    if not outline:
        return page["title"]
    return f"本页讲{page['title']}：" + "，".join(outline) + "。"


def apply_fallback(parsed: dict) -> None:
    """Fill missing speeches from outline and refresh the flat page list."""
    for chapter in parsed["chapters"]:
        for page in chapter["pages"]:
            if page.get("speech_missing"):
                page["speech"] = fallback_speech(page)
                page["speech_chars"] = len(page["speech"])
                page["speech_missing"] = False
                page["speech_source"] = "outline_fallback"
    parsed["pages"] = [dict(page) for chapter in parsed["chapters"] for page in chapter["pages"]]
