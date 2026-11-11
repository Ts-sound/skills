"""Review gates: `all`, `none`, or a list like `1,3`.

A gate never edits artifacts; it only decides whether the pipeline continues.
The point is that stage outputs are themselves the review surface, so a user
can fix files and rerun `--from N` without losing earlier work.

Gate policy: a selected gate STOPS by default. `--yes` (or MD2TALK_AUTO=1) is
the only way to auto-pass, and that opt-in is explicit. This matters when the
pipeline runs under an agent or CI shell, where stdin is not a TTY: silence
must not be read as approval, because then a broken parse would silently spend
TTS quota before anyone looked at it.
"""

from __future__ import annotations

import os
import sys

from paths import Log

VALID_STAGES = {"1", "2", "3", "4"}


def parse_mode(spec: str | list | set | None) -> str | set[str]:
    if spec is None:
        return set(VALID_STAGES)
    if isinstance(spec, (set, list, tuple)):
        return {str(s).strip() for s in spec if str(s).strip()}
    text = str(spec).strip().lower()
    if text in ("all", ""):
        return set(VALID_STAGES)
    if text in ("none", "auto", "off"):
        return "none"
    stages = {part.strip() for part in text.split(",") if part.strip()}
    unknown = stages - VALID_STAGES
    if unknown:
        raise ValueError(f"unknown review stage(s) {sorted(unknown)}; use all|none|1,2,3,4")
    return stages


def _banner(stage: str, summary: str) -> None:
    print("\n" + "=" * 68)
    print(summary)
    print("=" * 68)


def gate(stage: int, mode: str | set[str], summary: str, log: Log) -> bool:
    """Return True to continue, False to pause the pipeline."""
    key = str(stage)
    if mode == "none" or key not in mode:
        log.debug(f"gate {key}: not selected, pass")
        return True

    # Always show the review surface, even when we cannot prompt.
    _banner(key, summary)
    print(f"GATE {key} 已停在审核点。产物在上面列出的路径里，可打开、可手改。")
    print(f"审核通过后重跑：--from {key} --review none（或继续用闸门，加 --yes 自动过）")
    sys.stdout.flush()

    if os.environ.get("MD2TALK_AUTO") == "1":
        log.warn(f"gate {key}: MD2TALK_AUTO=1, auto-pass")
        return True

    if not sys.stdin.isatty():
        log.warn(f"gate {key}: non-interactive stdin, pausing for review")
        return False

    print("Enter = 继续 / e = 停止（产物保留，可改文件后 --from 重跑）")
    try:
        answer = input("> ").strip().lower()
    except EOFError:
        log.warn(f"gate {key}: stdin closed, pausing for review")
        return False
    if answer in ("e", "exit", "stop", "q", "quit"):
        log.warn(f"gate {key}: stopped by user")
        return False
    return True
