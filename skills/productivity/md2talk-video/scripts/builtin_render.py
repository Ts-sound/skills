#!/usr/bin/env python3
"""Bundled silent-video renderer: headless browser screenshot -> ffmpeg loop.

Used by the default config so stage 4 works without `hyperframes`. The slide is
a static HTML page, so a screenshot plus a still-image encode is enough; motion
is the audio's job. The render raster size defaults to 1920x1080 and is
independent of the 1280x720 slide canvas (SVG/HTML scale to the window).

Browser lookup order: --browser, $MD2TALK_BROWSER, common Edge/Chrome install
paths, then PATH. Nothing else is required beyond ffmpeg (already a pipeline
dependency).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

WINDOWS_BROWSERS = [
    r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
    r"C:\Program Files\Google\Chrome\Application\chrome.exe",
    r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
]
UNIX_BROWSERS = [
    "/usr/bin/google-chrome",
    "/usr/bin/chromium",
    "/usr/bin/chromium-browser",
    "/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",
    "/Applications/Microsoft Edge.app/Contents/MacOS/Microsoft Edge",
]


def find_browser(explicit: str | None) -> str | None:
    for cand in (explicit, os.environ.get("MD2TALK_BROWSER")):
        if cand and Path(cand).is_file():
            return cand
    for cand in WINDOWS_BROWSERS + UNIX_BROWSERS:
        if Path(cand).is_file():
            return cand
    for name in ("msedge", "chrome", "chromium", "chromium-browser", "google-chrome"):
        found = shutil.which(name)
        if found:
            return found
    return None


def screenshot(browser: str, page: Path, png: Path, profile: Path,
               width: int, height: int) -> bool:
    base = [
        browser,
        "--headless=new",
        "--disable-gpu",
        "--hide-scrollbars",
        "--no-first-run",
        "--no-default-browser-check",
        f"--user-data-dir={profile}",
        f"--window-size={width},{height}",
        "--force-device-scale-factor=1",
        f"--screenshot={png}",
        page.as_uri(),
    ]
    for headless in ("--headless=new", "--headless"):
        cmd = [headless if i == 1 else part for i, part in enumerate(base)]
        try:
            proc = subprocess.run(cmd, capture_output=True, text=True,
                                  encoding="utf-8", errors="replace", timeout=120)
        except (OSError, subprocess.TimeoutExpired):
            continue
        if png.is_file() and png.stat().st_size > 0:
            return True
        print(f"WARN  browser screenshot failed ({headless}, exit {proc.returncode})",
              file=sys.stderr)
    return False


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--html", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--duration", type=float, required=True)
    ap.add_argument("--fps", type=int, default=30)
    ap.add_argument("--width", type=int, default=1920)
    ap.add_argument("--height", type=int, default=1080)
    ap.add_argument("--ffmpeg", default="ffmpeg")
    ap.add_argument("--browser", default=None)
    args = ap.parse_args()

    page = Path(args.html).resolve()
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    browser = find_browser(args.browser)
    if not browser:
        print("ERROR no Edge/Chrome found; set MD2TALK_BROWSER or install one, "
              "or point render.cmd at hyperframes", file=sys.stderr)
        return 2

    tmp_path = Path(tempfile.mkdtemp(prefix="md2talk-shot-"))
    try:
        png = tmp_path / "slide.png"
        profile = tmp_path / "profile"
        if not screenshot(browser, page, png, profile, args.width, args.height):
            print(f"ERROR screenshot failed for {page}", file=sys.stderr)
            return 1
        cmd = [
            args.ffmpeg, "-y",
            "-loop", "1", "-framerate", str(args.fps), "-i", str(png),
            "-t", f"{max(args.duration, 0.1):.3f}",
            "-vf", f"scale={args.width}:{args.height}",
            "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
            "-pix_fmt", "yuv420p", "-r", str(args.fps),
            "-movflags", "+faststart", str(out),
        ]
        proc = subprocess.run(cmd, capture_output=True, text=True,
                              encoding="utf-8", errors="replace")
        if proc.returncode != 0 or not out.is_file():
            tail = (proc.stderr or proc.stdout or "").strip().splitlines()[-8:]
            print("ERROR ffmpeg still-image encode failed\n  " + "\n  ".join(tail),
                  file=sys.stderr)
            return 1
    finally:
        # Edge keeps handles on its profile longer than the process; cleanup is
        # best-effort or Windows raises WinError 5 on chmod.
        shutil.rmtree(tmp_path, ignore_errors=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
