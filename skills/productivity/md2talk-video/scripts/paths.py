"""Path resolution and shell helpers shared by the md2talk-video pipeline.

The skill is called with a workspace path only. Every other path (config,
themes, bundled tools) is derived from this file's own location, so callers
never pass script or asset paths.
"""

from __future__ import annotations

import json
import os
import shlex
import shutil
import subprocess
import sys
from pathlib import Path

SCRIPT_DIR = Path(__file__).resolve().parent
SKILL_DIR = SCRIPT_DIR.parent
CONFIG_PATH = SKILL_DIR / "config" / "default.yaml"

OUT_SUBDIRS = ("1_md", "2_tts", "3_htmlppt", "4_video")


class PipelineError(RuntimeError):
    """Fatal, user-facing error. Printed without a traceback."""


# --------------------------------------------------------------------------
# configuration
# --------------------------------------------------------------------------


def _strip_comment(line: str) -> str:
    quote = None
    for i, ch in enumerate(line):
        if quote:
            if ch == quote:
                quote = None
        elif ch in "'\"":
            quote = ch
        elif ch == "#" and (i == 0 or line[i - 1].isspace()):
            return line[:i]
    return line


def _scalar(text: str):
    t = text.strip()
    if not t:
        return ""
    if len(t) >= 2 and t[0] == t[-1] and t[0] in "'\"":
        return t[1:-1]
    low = t.lower()
    if low in ("true", "yes", "on"):
        return True
    if low in ("false", "no", "off"):
        return False
    if low in ("null", "~", "none"):
        return None
    if t.startswith("[") and t.endswith("]"):
        inner = t[1:-1].strip()
        return [_scalar(part) for part in inner.split(",")] if inner else []
    try:
        return int(t)
    except ValueError:
        pass
    try:
        return float(t)
    except ValueError:
        pass
    return t


def load_yaml(path: Path) -> dict:
    """Parse the small YAML subset used by config/default.yaml.

    Nested mappings, quoted/bare scalars, booleans, numbers and inline lists
    are supported. Anything else raises, so a config typo never silently
    becomes a string.
    """
    root: dict = {}
    stack: list[tuple[int, dict]] = [(-1, root)]
    for lineno, raw in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        line = _strip_comment(raw).rstrip()
        if not line.strip():
            continue
        indent = len(line) - len(line.lstrip(" "))
        body = line.strip()
        if ":" not in body:
            raise PipelineError(
                f"{path}:{lineno}: only 'key: value' mappings are supported, got {body!r}"
            )
        key, _, value = body.partition(":")
        key = key.strip()
        while stack and indent <= stack[-1][0]:
            stack.pop()
        parent = stack[-1][1]
        if value.strip():
            parent[key] = _scalar(value)
        else:
            child: dict = {}
            parent[key] = child
            stack.append((indent, child))
    return root


_CONFIG_CACHE: dict | None = None


def load_config(path: str | os.PathLike | None = None) -> dict:
    global _CONFIG_CACHE
    if path is None and _CONFIG_CACHE is not None:
        return _CONFIG_CACHE
    if path:
        cfg_path = Path(path).expanduser()
        # Relative --config is documented relative to the skill, not the cwd:
        # the pipeline is normally launched from the workspace.
        if not cfg_path.is_absolute() and not cfg_path.exists():
            cfg_path = SKILL_DIR / cfg_path
        cfg_path = cfg_path.resolve()
    else:
        cfg_path = CONFIG_PATH
    if not cfg_path.exists():
        raise PipelineError(f"config not found: {cfg_path}")
    cfg = load_yaml(cfg_path)
    if path is None:
        _CONFIG_CACHE = cfg
    return cfg


# --------------------------------------------------------------------------
# workspace
# --------------------------------------------------------------------------


def resolve_workspace(arg: str | os.PathLike) -> Path:
    ws = Path(arg).expanduser().resolve()
    if not ws.is_dir():
        raise PipelineError(f"workspace is not a directory: {ws}")
    return ws


def ensure_out(ws: Path) -> dict[str, Path]:
    out = ws / "out"
    dirs = {name: out / name for name in OUT_SUBDIRS}
    for path in dirs.values():
        path.mkdir(parents=True, exist_ok=True)
    (ws / "logs").mkdir(parents=True, exist_ok=True)
    return dirs


# --------------------------------------------------------------------------
# logging
# --------------------------------------------------------------------------


class Log:
    def __init__(self, ws: Path, verbose: bool = False):
        self.verbose = verbose
        self.path = ws / "logs" / "run.log"
        self.path.parent.mkdir(parents=True, exist_ok=True)

    def _emit(self, text: str) -> None:
        line = f"{text}"
        try:
            print(line, flush=True)
        except UnicodeEncodeError:
            # Legacy Windows consoles (cp936) cannot encode arrows/emoji; never
            # let logging crash a stage that otherwise succeeded.
            enc = sys.stdout.encoding or "utf-8"
            print(line.encode(enc, "replace").decode(enc, "replace"), flush=True)
        with self.path.open("a", encoding="utf-8") as fh:
            fh.write(line + "\n")

    def info(self, msg: str) -> None:
        self._emit(msg)

    def debug(self, msg: str) -> None:
        if self.verbose:
            self._emit(msg)

    def warn(self, msg: str) -> None:
        self._emit(f"WARN  {msg}")

    def error(self, msg: str) -> None:
        self._emit(f"ERROR {msg}")


# --------------------------------------------------------------------------
# command rendering / execution
# --------------------------------------------------------------------------


def _candidate_roots(ws: Path | None) -> list[Path]:
    roots = [SKILL_DIR]
    if ws is not None:
        roots.append(ws)
    return roots


def resolve_tool(name: str, ws: Path | None = None) -> str | None:
    """Resolve a tool name to an executable path, or None when absent."""
    if not name:
        return None
    candidate = Path(name)
    if candidate.is_absolute():
        return str(candidate) if candidate.exists() else None
    if candidate.parent != Path(".") or name.startswith("."):
        for root in _candidate_roots(ws):
            path = root / candidate
            if path.exists():
                return str(path)
        return None
    return shutil.which(name)


def split_template(template: str) -> list[str]:
    return shlex.split(template, posix=os.name != "nt")


def render_cmd(template: str, ctx: dict, ws: Path | None = None) -> list[str]:
    """Render a command template and resolve its first token as a tool."""
    parts = split_template(template)
    if not parts:
        raise PipelineError("empty command template")
    try:
        rendered = [part.format_map(_SafeDict(ctx)) for part in parts]
    except KeyError as exc:  # pragma: no cover - defensive
        raise PipelineError(f"unknown placeholder {exc.args[0]!r} in {template!r}")
    head = rendered[0]
    resolved = resolve_tool(head, ws)
    if resolved is None:
        raise ToolMissing(head, template)
    rendered[0] = resolved
    return rendered


class _SafeDict(dict):
    def __missing__(self, key: str) -> str:
        raise KeyError(key)


class ToolMissing(PipelineError):
    def __init__(self, tool: str, template: str, hint: str = ""):
        self.tool = tool
        self.template = template
        self.hint = hint
        msg = f"required tool not found: {tool}"
        if hint:
            msg += f"\n  install: {hint}"
        msg += f"\n  command template: {template}"
        super().__init__(msg)


def run_cmd(cmd: list[str], cwd: Path, log: Log, timeout: int | None = None) -> subprocess.CompletedProcess:
    log.debug("$ " + " ".join(shlex.quote(c) for c in cmd))
    try:
        proc = subprocess.run(
            cmd,
            cwd=str(cwd),
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=timeout,
        )
    except FileNotFoundError as exc:
        raise PipelineError(f"cannot execute {cmd[0]}: {exc}")
    if proc.returncode != 0:
        tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-8:]
        detail = "\n  ".join(tail) if tail else "(no output)"
        raise PipelineError(
            f"command failed (exit {proc.returncode}): {' '.join(cmd)}\n  {detail}"
        )
    return proc


def ffprobe_duration(path: Path, cfg: dict, ws: Path, log: Log) -> float:
    cmd = render_cmd(
        "{ffprobe} -v error -show_entries format=duration -of default=nw=1:nk=1 {path}",
        {"ffprobe": cfg["compose"]["ffprobe"], "path": str(path)},
        ws,
    )
    proc = run_cmd(cmd, ws, log)
    try:
        return float(proc.stdout.strip())
    except ValueError:
        raise PipelineError(f"cannot read duration of {path}")


def write_json(path: Path, data) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def read_json(path: Path, default=None):
    if not path.exists():
        return default
    return json.loads(path.read_text(encoding="utf-8"))
