#!/usr/bin/env python3
"""Bundled HTML slide generator: one 1280x720 page per invocation.

Used by the default config so stage 3 works without an external `ppt-master`
CLI (that name is a skill workflow, not an executable). It renders the same
page model stage 1 produced: chapter tag, title, outline bullets. Swap it out
by pointing `ppt.cmd` at any tool that accepts `{page_json} {out_html} {theme}
{title}`; see config/default.yaml.

Theme: `<theme>/slide.css` is appended to the built-in stylesheet when present,
so colour/font tweaks stay in the assets directory instead of this script.
"""

from __future__ import annotations

import argparse
import html
import json
import re
from pathlib import Path

MAX_BULLETS = 7

BASE_CSS = """
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; width: 100%; height: 100%; overflow: hidden; background: #f7f5f2; }
body {
  font-family: "Microsoft YaHei", "PingFang SC", "Noto Sans CJK SC",
               system-ui, -apple-system, sans-serif;
  background: #f7f5f2;
  color: #1d1c1a;
}
.slide {
  width: 1280px; height: 720px; padding: 84px 104px 72px;
  display: flex; flex-direction: column;
  background:
    radial-gradient(900px 520px at 92% -10%, #efe6da 0%, transparent 60%),
    #f7f5f2;
  position: absolute; left: 50%; top: 50%;
  transform-origin: center center;
}
.chapter {
  font-size: 24px; letter-spacing: .16em; text-transform: uppercase;
  color: #a3541f; font-weight: 600; margin-bottom: 18px;
}
h1 {
  font-size: 62px; line-height: 1.16; margin: 0 0 42px; font-weight: 700;
  letter-spacing: -.01em; max-width: 1000px;
}
h1.small { font-size: 48px; }
ul { list-style: none; margin: 0; padding: 0; flex: 0 1 auto; }
li {
  font-size: 31px; line-height: 1.62; padding-left: 34px; position: relative;
  margin-bottom: 16px; color: #2b2926;
}
li::before {
  content: ""; position: absolute; left: 0; top: .62em;
  width: 12px; height: 12px; border-radius: 3px; background: #c96f2f;
}
li.dense { font-size: 27px; margin-bottom: 10px; }
code {
  font-family: "Cascadia Mono", Consolas, monospace; font-size: .92em;
  background: #eae4da; padding: 2px 8px; border-radius: 6px;
}
.foot {
  position: absolute; left: 104px; right: 104px; bottom: 34px;
  display: flex; justify-content: space-between;
  font-size: 19px; color: #8a837a; letter-spacing: .08em;
}
.accent { position: absolute; left: 0; top: 0; width: 12px; height: 720px; background: #c96f2f; }
.slide.cover, .slide.closing { justify-content: center; align-items: center; text-align: center; }
.slide.section { justify-content: center; }
.slide.section h1 { font-size: 66px; margin: 0; max-width: 1040px; }
.slide.section .closing-line { width: 64px; height: 5px; background: #c96f2f; margin: 0 0 34px; }
.slide.section .chapter { margin-bottom: 22px; }
.slide.cards ul { display: grid; grid-template-columns: 1fr 1fr; gap: 18px; }
.slide.cards li {
  padding: 22px 24px; margin: 0; border-radius: 14px;
  background: #efe8dc; font-size: 28px; line-height: 1.45;
}
.slide.cards li::before { display: none; }
.slide.data .big {
  font-size: 118px; line-height: 1; font-weight: 700; color: #c96f2f;
  letter-spacing: -.03em; margin: 8px 0 30px;
}
.slide.cover h1 { font-size: 78px; margin: 0 0 28px; max-width: 1040px; }
.slide.cover .subtitle { font-size: 26px; color: #6b645c; letter-spacing: .06em; }
.slide.cover .chapter { margin-bottom: 30px; }
.slide.closing h1 { font-size: 56px; margin: 0 0 18px; }
.slide.closing .closing-line { width: 64px; height: 5px; background: #c96f2f; margin: 0 0 34px; }
.slide.closing p { font-size: 28px; color: #4a453e; margin: 6px 0; }
ol.agenda { list-style: none; margin: 12px 0 0; padding: 0; }
ol.agenda li {
  display: flex; gap: 26px; align-items: baseline;
  font-size: 30px; line-height: 1.5; margin-bottom: 14px; padding-left: 0;
}
ol.agenda li::before { display: none; }
ol.agenda .num { color: #c96f2f; font-weight: 700; min-width: 52px; }
pre.code {
  margin: 18px 0 0; padding: 20px 26px;
  background: #f4efe6; border-left: 4px solid #c96f2f;
  font-family: Consolas, "Cascadia Mono", "Courier New", monospace;
  font-size: 21px; line-height: 1.45; color: #3b3630;
  white-space: pre-wrap; max-height: 210px; overflow: hidden;
  flex: 0 0 auto;
}
.slide.has-code h1 { margin-bottom: 26px; }
.slide.has-code li { font-size: 26px; line-height: 1.45; margin-bottom: 8px; }
.slide.has-code pre.code { font-size: 19px; padding: 14px 20px; margin-top: 14px; }
"""


def _cover(title: str, chapter: str, bullets: list[str]) -> str:
    subtitle = bullets[0] if bullets else ""
    chapter_html = f'<div class="chapter">{html.escape(chapter)}</div>' if chapter else ""
    return f"""
  {chapter_html}
  <h1>{html.escape(title)}</h1>
  {"<div class='subtitle'>" + inline(subtitle) + "</div>" if subtitle else ""}
"""


def _agenda(title: str, chapter: str, bullets: list[str]) -> str:
    chapter_html = f'<div class="chapter">{html.escape(chapter)}</div>' if chapter else ""
    items = "".join(
        f'<li><span class="num">{i:02d}</span><span>{inline(b)}</span></li>'
        for i, b in enumerate(bullets, 1)
    )
    return f"""
  {chapter_html}
  <h1 class="small">{html.escape(title)}</h1>
  <ol class="agenda">{items}</ol>
"""


def _closing(title: str, bullets: list[str]) -> str:
    paras = "".join(f"<p>{inline(b)}</p>" for b in bullets)
    return f"""
  <div class="closing-line"></div>
  <h1>{html.escape(title)}</h1>
  {paras}
"""


def _section(title: str, chapter: str) -> str:
    chapter_html = f'<div class="chapter">{html.escape(chapter)}</div>' if chapter else ""
    return f"""
  {chapter_html}
  <div class="closing-line"></div>
  <h1>{html.escape(title)}</h1>
"""


def _bold(segment: str) -> str:
    parts = segment.split("**")
    return "".join(f"<strong>{p}</strong>" if i % 2 else p for i, p in enumerate(parts))


def inline(text: str) -> str:
    """Escape, then handle `code` spans before **bold** inside them."""
    escaped = html.escape(text)
    pieces = escaped.split("`")
    return "".join(
        _bold(p) if i % 2 == 0 else f"<code>{p}</code>" for i, p in enumerate(pieces)
    )


def build(page: dict, theme: Path | None) -> str:
    title = re.sub(r"^P\d+\s*", "", page.get("title") or "未命名")
    chapter = page.get("chapter") or ""
    kind = page.get("kind") or "content"
    bullets = [b for b in page.get("outline", []) if b.strip()][:MAX_BULLETS]
    code = (page.get("code") or "").strip()
    if code:
        bullets = bullets[:4]

    extra = ""
    if theme:
        css = theme / "slide.css" if theme.is_dir() else theme
        if css.is_file():
            extra = "\n" + css.read_text(encoding="utf-8")

    if kind == "cover":
        body = _cover(title, chapter, bullets)
    elif kind == "agenda":
        body = _agenda(title, chapter, bullets)
    elif kind == "closing":
        body = _closing(title, bullets)
    elif kind == "section":
        body = _section(title, chapter)
    elif kind == "data":
        chapter_html = f'<div class="chapter">{html.escape(chapter)}</div>' if chapter else ""
        big = inline(bullets[0]) if bullets else ""
        rest = "".join(f'<li class="dense">{inline(b)}</li>' for b in bullets[1:])
        body = f"""
  {chapter_html}
  <h1 class="small">{html.escape(title)}</h1>
  <div class="big">{big}</div>
  <ul>{rest}</ul>
"""
    else:
        chapter_html = f'<div class="chapter">{html.escape(chapter)}</div>' if chapter else ""
        code_html = f'<pre class="code">{html.escape(code)}</pre>' if code else ""
        if bullets:
            dense = len(bullets) >= 6 or sum(len(b) for b in bullets) > 260
            items = "".join(
                f'<li{" class=dense" if dense else ""}>{inline(b)}</li>' for b in bullets
            )
            body = f"""
  {chapter_html}
  <h1 class="{'small' if len(title) > 18 else ''}">{html.escape(title)}</h1>
  <ul>{items}</ul>
  {code_html}
"""
        else:
            body = f"""
  {chapter_html}
  <h1 class="{'small' if len(title) > 18 else ''}">{html.escape(title)}</h1>
  <ul><li class="dense">（本页无大纲）</li></ul>
  {code_html}
"""

    return f"""<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<title>{html.escape(title)}</title>
<style>{BASE_CSS}{extra}</style>
</head>
<body>
<div class="slide {kind}{' has-code' if code else ''}">
  <div class="accent"></div>
  {body}
  <div class="foot"><span>md2talk-video</span><span>{html.escape(str(page.get("id", "")))}</span></div>
</div>
<script>
  const slide = document.querySelector('.slide');
  const fit = () => {{
    const s = Math.min(window.innerWidth / 1280, window.innerHeight / 720);
    slide.style.transform = `translate(-50%, -50%) scale(${{s}})`;
  }};
  fit();
  window.addEventListener('resize', fit);
</script>
</body>
</html>
"""


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--in", dest="src", required=True)
    ap.add_argument("--out", dest="dst", required=True)
    ap.add_argument("--theme", default="")
    ap.add_argument("--title", default="")
    args = ap.parse_args()

    page = json.loads(Path(args.src).read_text(encoding="utf-8-sig"))
    theme = Path(args.theme).expanduser() if args.theme else None
    dst = Path(args.dst)
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_text(build(page, theme), encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
