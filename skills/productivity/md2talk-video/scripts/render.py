"""Silent per-page video rendering via hyperframes."""

from __future__ import annotations

import sys
from pathlib import Path

from paths import SKILL_DIR, Log, PipelineError, ToolMissing, resolve_tool, render_cmd, run_cmd, split_template


def check_tool(cfg: dict, ws: Path) -> None:
    head = split_template(cfg["render"]["cmd"])[0]
    if head.startswith("{") and head.endswith("}"):
        return  # supplied by the command context, e.g. {python}
    if resolve_tool(head, ws) is None:
        raise ToolMissing(head, cfg["render"]["cmd"], cfg["render"].get("install_hint", ""))


def render_page(page: dict, duration: float, cfg: dict, ws: Path,
                out_dir: Path, log: Log) -> Path:
    build = out_dir / ".build"
    build.mkdir(parents=True, exist_ok=True)
    html_path = ws / page["html"]
    silent = build / f"{page['id']}.silent.mp4"
    ctx = {
        "html": str(html_path),
        "out_mp4": str(silent),
        "duration": f"{duration:.3f}",
        "fps": str(cfg["render"].get("fps", 30)),
        "width": str(cfg["render"].get("width", 1920)),
        "height": str(cfg["render"].get("height", 1080)),
        "python": sys.executable,
        "skill": str(SKILL_DIR),
        "ffmpeg": cfg["compose"]["ffmpeg"],
    }
    run_cmd(render_cmd(cfg["render"]["cmd"], ctx, ws), ws, log)
    if not silent.exists():
        raise PipelineError(f"renderer produced no video for {page['id']}: {silent}")
    log.info(f"{page['id']}: silent video {duration:.2f}s -> {silent.name}")
    return silent
