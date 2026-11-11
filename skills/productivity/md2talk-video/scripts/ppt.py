"""HTML slide generation via ppt-master, one call per page."""

from __future__ import annotations

import html
import re
import sys
from pathlib import Path

from paths import SKILL_DIR, Log, PipelineError, ToolMissing, resolve_tool, render_cmd, run_cmd, write_json, split_template


def check_tool(cfg: dict, ws: Path, provider: str = "builtin") -> None:
    if provider == "ppt-master":
        return  # SVG decks are authored by the ppt-master workflow, not a CLI
    head = split_template(cfg["ppt"]["cmd"])[0]
    if head.startswith("{") and head.endswith("}"):
        return  # supplied by the command context, e.g. {python}
    if resolve_tool(head, ws) is None:
        raise ToolMissing(head, cfg["ppt"]["cmd"], cfg["ppt"].get("install_hint", ""))


def build_page(page: dict, cfg: dict, ws: Path, out_dir: Path, log: Log) -> str:
    build = out_dir / ".build"
    build.mkdir(parents=True, exist_ok=True)
    page_json = build / f"{page['id']}.json"
    write_json(
        page_json,
        {
            "id": page["id"],
            "title": page["title"],
            "chapter": page["chapter"],
            "kind": page.get("kind", "content"),
            "layout": page.get("layout", ""),
            "code": page.get("code", ""),
            "outline": page["outline"],
        },
    )
    out_html = out_dir / f"{page['id']}.html"
    theme = cfg["ppt"]["theme"]
    # Relative theme paths resolve against the skill first, then the workspace,
    # so `assets/theme/default` works no matter where the pipeline is launched.
    candidates = [Path(theme)] if Path(theme).is_absolute() else [SKILL_DIR / theme, Path(ws) / theme]
    theme_path = next((path for path in candidates if path.exists()), None)
    if theme_path is not None:
        theme = str(theme_path)
    ctx = {
        "page_json": str(page_json),
        "out_html": str(out_html),
        "theme": theme,
        "title": page["title"],
        "python": sys.executable,
        "skill": str(SKILL_DIR),
    }
    run_cmd(render_cmd(cfg["ppt"]["cmd"], ctx, ws), ws, log)
    if not out_html.exists():
        raise PipelineError(f"ppt-master produced no html for {page['id']}: {out_html}")
    log.info(f"{page['id']}: html -> {out_html.name}")
    return str(out_html.relative_to(ws))


def build_page_from_svg(page: dict, index: int, svg_dir: Path, ws: Path, out_dir: Path,
                        log: Log) -> str:
    """Wrap one ppt-master SVG page in the HTML shell used by stage 4."""
    svg_files = sorted(p for p in svg_dir.glob("*.svg") if p.is_file())
    if not svg_files:
        raise PipelineError(f"ppt-master 模式找不到 SVG：{svg_dir}")
    exact = [p for p in svg_files if p.name.startswith(page["id"])]
    if exact:
        svg = exact[0]
    elif index < len(svg_files):
        svg = svg_files[index]
    else:
        raise PipelineError(
            f"SVG 数量不足：{page['id']} 需要第 {index + 1} 页，目录只有 {len(svg_files)} 个 SVG"
        )
    out_html = out_dir / f"{page['id']}.html"
    svg_text = svg.read_text(encoding="utf-8")
    svg_text = re.sub(r"^\s*<\?xml[^>]*\?>\s*", "", svg_text, count=1)
    svg_text = re.sub(
        r"<svg\b",
        '<svg style="display:block;width:100%;height:100%"',
        svg_text, count=1,
    )
    out_html.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{html.escape(page['title'])}</title>
<style>
  html, body {{ margin: 0; width: 100%; height: 100vh; overflow: hidden; background: #FDF6E3; }}
  body > svg {{ display: block; width: 100%; height: 100%; }}
</style></head>
<body>{svg_text}</body>
</html>
""",
        encoding="utf-8",
    )
    log.info(f"{page['id']}: svg -> {out_html.name} ({svg.name})")
    return str(out_html.relative_to(ws))


def write_index(pages: list[dict], out_dir: Path, title: str) -> Path:
    """Preview entry; links are page basenames because index sits in out_dir."""
    index = out_dir / "index.html"
    links = "\n".join(
        f'      <li><a href="{html.escape(Path(p["html"]).name)}" target="slide">'
        f'{html.escape(p["id"])} · {html.escape(p.get("title") or "")}</a></li>'
        for p in pages
    )
    first = Path(pages[0]["html"]).name if pages else ""
    index.write_text(
        f"""<!doctype html>
<html lang="zh-CN">
<head><meta charset="utf-8"><title>{html.escape(title)} · 预览</title>
<style>
  body{{margin:0;font:14px/1.5 system-ui,sans-serif;display:flex;height:100vh}}
  nav{{width:260px;overflow:auto;border-right:1px solid #ddd;background:#fafafa}}
  nav h1{{font-size:14px;padding:12px;margin:0;border-bottom:1px solid #ddd}}
  nav ul{{list-style:none;margin:0;padding:8px}}
  nav li{{margin:4px 0}}
  nav a{{color:#1a5fb4;text-decoration:none}}
  main{{flex:1}}
  iframe{{border:0;width:100%;height:100%}}
</style></head>
<body>
  <nav><h1>{html.escape(title)}</h1><ul>
{links}
  </ul></nav>
  <main><iframe name="slide" src="{html.escape(first)}"></iframe></main>
</body>
</html>
""",
        encoding="utf-8",
    )
    return index
