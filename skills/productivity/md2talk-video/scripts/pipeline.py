#!/usr/bin/env python3
"""md2talk-video pipeline.

Stage 0  init   read input.md, load/create job.json, resolve review mode
Stage 1  md     parse -> out/1_md/*            GATE 1
Stage 2  tts    per-page wav + srt             GATE 2 / 2b
Stage 3  ppt    per-page html slide            GATE 3
Stage 4  video  render, mux, concat, final srt GATE 4

`job.json` is the single source of truth: it holds the review mode, the TTS
choice and per-page artifacts, so rerunning the same command resumes instead
of redoing finished work.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

import compose
import deck_check
import md_parse
import ppt
import render
import review
import srt
import tts
from paths import (
    Log,
    PipelineError,
    ToolMissing,
    ensure_out,
    load_config,
    read_json,
    resolve_workspace,
    write_json,
)

STAGE_NAMES = {1: "md", 2: "tts", 3: "ppt", 4: "video"}


def _fingerprint(label: str, *parts) -> str:
    """Stable content key; artifacts are reusable only while it matches."""
    blob = json.dumps(parts, ensure_ascii=False, sort_keys=True).encode("utf-8")
    return f"{label}:{hashlib.sha1(blob).hexdigest()}"


def _file_digest(path: Path) -> str:
    digest = hashlib.sha1()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _svg_stamp(svg_dir: Path | None) -> str:
    if svg_dir is None or not svg_dir.is_dir():
        return ""
    files = sorted(p for p in svg_dir.glob("*.svg") if p.is_file())
    return "|".join(f"{p.name}:{p.stat().st_size}:{p.stat().st_mtime_ns}" for p in files)


def _utf8_stdio() -> None:
    """Force UTF-8 console output; legacy Windows code pages mangle summaries."""
    for stream in (sys.stdout, sys.stderr):
        try:
            stream.reconfigure(encoding="utf-8", errors="replace")
        except (AttributeError, ValueError, OSError):
            pass


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(
        prog="md2talk-video",
        description="Markdown 演讲稿 -> 配音 + 字幕 + HTML PPT + 成片",
    )
    p.add_argument("workspace", help="工作目录，需含 input.md")
    p.add_argument("--review", default=None,
                   help="审核闸门：all | none | 1,2,3,4（默认沿用 job.json，新建为 all）")
    p.add_argument("--tts", default=None, help="edge-tts | audiocpp（默认读配置）")
    p.add_argument("--ppt", choices=["builtin", "ppt-master"], default=None,
                   help="阶段 3 的 PPT provider：内置 HTML 或 ppt-master SVG")
    p.add_argument("--svg-dir", default=None,
                   help="ppt-master 模式：SVG 页目录（svg_output/），相对路径按 workspace 解析")
    p.add_argument("--voice", default=None, help="音色/参考音频")
    p.add_argument("--rate", default=None, help="语速，如 +10%%")
    p.add_argument("--from", dest="from_stage", type=int, choices=[1, 2, 3, 4],
                   default=None, help="从指定阶段重跑")
    p.add_argument("--force", action="store_true", help="忽略已有产物强制重跑")
    p.add_argument("--only", default=None, help="只处理某一页，如 p003")
    p.add_argument("--config", default=None, help="自定义配置 yaml")
    p.add_argument("--yes", action="store_true", help="所有审核闸门自动通过")
    p.add_argument("--verbose", action="store_true", help="打印命令与调试信息")
    return p.parse_args(argv)


# --------------------------------------------------------------------------
# job state
# --------------------------------------------------------------------------


def write_job(job: dict, path: Path) -> None:
    write_json(path, job)


def upsert_pages(job: dict, updates: list[dict]) -> None:
    by_id = {rec["id"]: dict(rec) for rec in job.get("pages", [])}
    for rec in updates:
        by_id.setdefault(rec["id"], {}).update(rec)
    job["pages"] = [by_id[key] for key in sorted(by_id)]


def pages_of(job: dict) -> dict[str, dict]:
    return {rec["id"]: rec for rec in job.get("pages", [])}


def load_parsed(dirs: dict[str, Path]) -> dict:
    parsed = read_json(dirs["1_md"] / "parsed.json")
    if not parsed:
        raise PipelineError("parsed.json missing; run stage 1 first (--from 1)")
    return parsed


# --------------------------------------------------------------------------
# stage 1
# --------------------------------------------------------------------------


def stage_md(ws: Path, job: dict, dirs: dict[str, Path], mode, log: Log) -> tuple[dict | None, bool]:
    log.info("[1/4] 解析 input.md")
    parsed = md_parse.parse(ws / "input.md")
    write_json(dirs["1_md"] / "parsed.json", parsed)
    md_parse.write_script_md(parsed, dirs["1_md"] / "script.md")
    summary = md_parse.write_review_md(parsed, dirs["1_md"] / "review.md")

    # Deck mechanics are cheap to check here and expensive to discover after
    # TTS: wrong kinds, missing agenda, paragraph bullets. Report, do not block:
    # a deliberate deviation is still the author's call at GATE 1.
    issues = deck_check.audit(parsed)
    if issues:
        errors = sum(1 for i in issues if i["level"] == "error")
        warns = len(issues) - errors
        summary += (
            f"\n\nDECK CHECK：{errors} error / {warns} warning"
            "（详情：python scripts/deck_check.py <ws>/input.md）"
        )
        for i in issues[:6]:
            where = f"{i['page']} {i['title']}".strip()
            log.warn(f"deck {i['level']}: {where} — {i['message']}")
        if len(issues) > 6:
            log.warn(f"deck: 其余 {len(issues) - 6} 条省略")

    # A re-parse can shrink the deck; records for pages that no longer exist
    # would otherwise linger in job.json and confuse stage 2/4 ordering.
    valid = {p["id"] for p in parsed["pages"]}
    dropped = [rec["id"] for rec in job.get("pages", []) if rec["id"] not in valid]
    if dropped:
        job["pages"] = [rec for rec in job.get("pages", []) if rec["id"] in valid]
        log.warn(f"清理过期页记录：{', '.join(dropped)}")

    missing = [p for p in parsed["pages"] if p["speech_missing"]]
    if missing:
        log.warn(f"{len(missing)} 页缺演讲稿：" + ", ".join(p["id"] for p in missing))

    if not review.gate(1, mode, summary, log):
        return None, False

    if missing:
        md_parse.apply_fallback(parsed)
        write_json(dirs["1_md"] / "parsed.json", parsed)
        log.warn("已用大纲要点回退生成演讲稿（speech_source=outline_fallback）")
    return parsed, True


# --------------------------------------------------------------------------
# stage 2
# --------------------------------------------------------------------------


def _gate_tts_choice(backend_cfg: dict, mode, ws: Path, log: Log) -> dict:
    """GATE 2: pick backend/voice/rate before spending synthesis time."""
    if mode == "none" or not isinstance(mode, set) or "2" not in mode:
        return backend_cfg
    if os.environ.get("MD2TALK_AUTO") == "1" or not sys.stdin.isatty():
        return backend_cfg
    print("\n" + "=" * 68)
    print("GATE 2 · TTS 设置")
    print(f"  当前：backend={backend_cfg['backend']}  "
          f"voice={backend_cfg.get('voice', '-')}  rate={backend_cfg.get('rate', '-')}")
    print("  直接回车沿用；也可输入新的 voice（例如 zh-CN-YunxiNeural）")
    print("=" * 68)
    try:
        voice = input("voice> ").strip()
        rate = input("rate> ").strip()
    except EOFError:
        log.warn("GATE 2: stdin closed, keeping current tts settings")
        return backend_cfg
    if voice:
        backend_cfg = {**backend_cfg, "voice": voice}
    if rate:
        backend_cfg = {**backend_cfg, "rate": rate}
    return backend_cfg


def stage_tts(ws: Path, job: dict, cfg: dict, dirs: dict[str, Path], mode, only: str | None,
              force: bool, backend_cfg: dict, log: Log, job_path: Path) -> bool:
    log.info("[2/4] 合成配音 + 字幕")
    parsed = load_parsed(dirs)
    tts.check_backend(backend_cfg, ws)
    existing = pages_of(job)
    records: list[dict] = []
    tts_voice = (backend_cfg.get("backend"), backend_cfg.get("voice"), backend_cfg.get("rate"))
    for page in parsed["pages"]:
        if only and page["id"] != only:
            continue
        rec = existing.get(page["id"])
        wav = ws / rec["wav"] if rec and rec.get("wav") else None
        if page.get("speech_source") == "outline_fallback" or not page["speech"]:
            page = {**page, "speech": md_parse.fallback_speech(page)}
        fingerprint = _fingerprint("tts", page["speech"], *tts_voice)
        if rec and wav and wav.exists() and rec.get("tts_fp") == fingerprint and not force:
            log.info(f"{page['id']}: 复用已有音频 ({rec['wav_dur']:.2f}s)")
            records.append(rec)
            continue
        rec_new = {**tts.synth_page(page, backend_cfg, cfg, ws, dirs["2_tts"], log),
                   "title": page["title"], "tts_fp": fingerprint}
        records.append(rec_new)
        upsert_pages(job, [rec_new])
        write_job(job, job_path)

    upsert_pages(job, records)
    all_records = [pages_of(job)[p["id"]] for p in parsed["pages"] if p["id"] in pages_of(job)]
    manifest = tts.write_manifest(all_records, dirs["2_tts"], backend_cfg)
    summary = (
        "GATE 2b · 音频审核\n"
        f"后端：{manifest['backend']}  总时长：{manifest['total_dur']:.1f}s  页数：{len(all_records)}\n"
        + "\n".join(f"  {r['id']}  {r['wav_dur']:6.2f}s  {r['srt_lines']} 行字幕" for r in all_records)
        + f"\n产物：{dirs['2_tts']}"
    )
    return review.gate(2, mode, summary, log)


# --------------------------------------------------------------------------
# stage 3
# --------------------------------------------------------------------------


def stage_ppt(ws: Path, job: dict, cfg: dict, dirs: dict[str, Path], mode, only: str | None,
              force: bool, log: Log, job_path: Path,
              provider: str = "builtin", svg_dir: Path | None = None) -> bool:
    if provider == "ppt-master":
        log.info("[3/4] 用 ppt-master SVG 生成 HTML PPT")
        if svg_dir is None or not svg_dir.is_dir():
            raise PipelineError(
                "ppt-master 模式需要 --svg-dir，指向 ppt-master 导出的 svg_output/ 目录"
            )
    else:
        log.info("[3/4] 生成 HTML PPT")
    parsed = load_parsed(dirs)
    if provider == "ppt-master":
        svgs = sorted(p for p in svg_dir.glob("*.svg") if p.is_file())
        if not only and len(svgs) < len(parsed["pages"]):
            raise PipelineError(
                f"SVG 数量不足：{svg_dir} 只有 {len(svgs)} 个 SVG，"
                f"讲稿有 {len(parsed['pages'])} 页；先让 ppt-master 导出全部页面"
            )
        if not only and len(svgs) > len(parsed["pages"]):
            log.warn(f"SVG 多于页数（{len(svgs)} > {len(parsed['pages'])}），多余文件不会用到")
    ppt.check_tool(cfg, ws, provider)
    existing = pages_of(job)
    updates: list[dict] = []
    svg_stamp = _svg_stamp(svg_dir) if provider == "ppt-master" else ""
    for index, page in enumerate(parsed["pages"]):
        if only and page["id"] != only:
            continue
        rec = existing.get(page["id"])
        html_path = ws / rec["html"] if rec and rec.get("html") else None
        tool_stamp = (
            _file_digest(Path(ppt.__file__)),
            _file_digest(Path(ppt.__file__).with_name("builtin_ppt.py")),
        )
        html_fp = _fingerprint(
            "html", provider, tool_stamp,
            {k: page.get(k) for k in ("id", "title", "chapter", "kind", "layout", "outline", "code")},
            svg_stamp,
        )
        if (rec and html_path and html_path.exists()
                and rec.get("html_fp") == html_fp and not force):
            log.info(f"{page['id']}: 复用已有 html")
            continue
        if provider == "ppt-master":
            html_rel = ppt.build_page_from_svg(page, index, svg_dir, ws, dirs["3_htmlppt"], log)
        else:
            html_rel = ppt.build_page(page, cfg, ws, dirs["3_htmlppt"], log)
        update = {"id": page["id"], "title": page["title"], "html": html_rel,
                  "html_fp": html_fp}
        updates.append(update)
        upsert_pages(job, [update])
        write_job(job, job_path)
    upsert_pages(job, updates)
    page_list = []
    for p in parsed["pages"]:
        rec = pages_of(job).get(p["id"], {})
        if rec.get("html"):
            page_list.append({**p, "html": rec["html"]})
    index = ppt.write_index(page_list, dirs["3_htmlppt"], Path(ws).name)
    summary = (
        "GATE 3 · PPT 审核\n"
        f"已生成 {len(page_list)} 页 HTML\n"
        f"预览：{index}\n"
        "可直接修改 HTML；重跑 --from 4 会直接复用修改后的文件。"
    )
    return review.gate(3, mode, summary, log)


# --------------------------------------------------------------------------
# stage 4
# --------------------------------------------------------------------------


def stage_video(ws: Path, job: dict, cfg: dict, dirs: dict[str, Path], mode, only: str | None,
                force: bool, log: Log, job_path: Path) -> bool:
    log.info("[4/4] 渲染、混流、拼接")
    parsed = load_parsed(dirs)
    recs = pages_of(job)
    missing = [p["id"] for p in parsed["pages"]
               if not recs.get(p["id"], {}).get("wav") or not recs.get(p["id"], {}).get("html")]
    if missing:
        raise PipelineError(f"缺少音频或 HTML，无法渲染：{', '.join(missing)}（先跑阶段 2/3）")
    render.check_tool(cfg, ws)
    render_cfg = cfg.get("render", {})
    size_cfg = (
        render_cfg.get("width", 1920),
        render_cfg.get("height", 1080),
        render_cfg.get("fps", 30),
    )
    updates: list[dict] = []
    for page in parsed["pages"]:
        if only and page["id"] != only:
            continue
        rec = recs[page["id"]]
        final_page = dirs["4_video"] / f"{page['id']}.mp4"
        html_file = ws / rec["html"]
        wav_file = ws / rec["wav"]
        video_fp = _fingerprint(
            "video",
            _file_digest(html_file) if html_file.is_file() else "",
            wav_file.stat().st_size if wav_file.is_file() else 0,
            wav_file.stat().st_mtime_ns if wav_file.is_file() else 0,
            *size_cfg,
        )
        if (final_page.exists() and rec.get("video_fp") == video_fp and not force):
            log.info(f"{page['id']}: 复用已有页面视频")
            updates.append({"id": page["id"], "video": str(final_page.relative_to(ws)),
                            "video_fp": video_fp})
            continue
        silent = render.render_page({**page, **rec}, rec["wav_dur"], cfg, ws, dirs["4_video"], log)
        compose.mux_page(silent, ws / rec["wav"], rec["wav_dur"], final_page, cfg, ws, log)
        update = {"id": page["id"], "video": str(final_page.relative_to(ws)),
                  "video_fp": video_fp}
        updates.append(update)
        upsert_pages(job, [update])
        write_job(job, job_path)
    upsert_pages(job, updates)

    if only:
        # --only rebuilds one page; concatenating now would need every other
        # page video and would fail on a deck that is still being worked on.
        rec = pages_of(job).get(only, {})
        summary = (
            "GATE 4 · 单页视频\n"
            f"{only}: {rec.get('video', '(未生成)')}\n"
            "其余页未重跑；需要整片时再跑 --from 4。"
        )
        return review.gate(4, mode, summary, log)

    recs = pages_of(job)
    ordered = [recs[p["id"]] for p in parsed["pages"]]
    final = dirs["4_video"] / "final.mp4"
    compose.concat(ordered, final, cfg, ws, log)

    pairs: list[tuple[str, int]] = []
    offset = 0.0
    for rec in ordered:
        srt_text = (ws / rec["srt"]).read_text(encoding="utf-8")
        pairs.append((srt_text, int(round(offset * 1000))))
        offset += rec["wav_dur"]
    final_srt = dirs["4_video"] / "final.srt"
    final_srt.write_text(srt.merge_page_srts(pairs), encoding="utf-8")
    log.info(f"final.srt: {final_srt.name}（{offset:.1f}s）")

    if cfg["compose"].get("burn_subtitles"):
        compose.burn_subtitles(final, final_srt, dirs["4_video"] / "final_subbed.mp4", cfg, ws, log)

    summary = (
        "GATE 4 · 成片验收\n"
        f"成片：{final}（{offset:.1f}s）\n"
        f"字幕：{final_srt}\n"
        f"分页视频：{dirs['4_video']}"
    )
    return review.gate(4, mode, summary, log)


# --------------------------------------------------------------------------
# orchestration
# --------------------------------------------------------------------------


def run(args: argparse.Namespace) -> int:
    ws = resolve_workspace(args.workspace)
    cfg = load_config(args.config)
    dirs = ensure_out(ws)
    log = Log(ws, args.verbose)
    job_path = ws / "job.json"

    if args.yes:
        os.environ["MD2TALK_AUTO"] = "1"

    job = read_json(job_path, {}) or {}
    job["workspace"] = str(ws)
    job.setdefault("stages", {})
    job.setdefault("pages", [])
    job.setdefault("tts", {})
    job.setdefault("ppt", {})

    try:
        mode = review.parse_mode(args.review if args.review is not None else job.get("review", "all"))
    except ValueError as exc:
        raise PipelineError(str(exc))
    job["review"] = mode if isinstance(mode, str) else sorted(mode)

    ppt_provider = args.ppt or job["ppt"].get("provider") or cfg["ppt"].get("provider", "builtin")
    svg_raw = args.svg_dir or job["ppt"].get("svg_dir") or cfg["ppt"].get("svg_dir") or ""
    svg_dir = None
    if svg_raw:
        svg_dir = Path(svg_raw)
        if not svg_dir.is_absolute():
            svg_dir = ws / svg_dir
    job["ppt"] = {"provider": ppt_provider, "svg_dir": str(svg_dir) if svg_dir else ""}
    write_job(job, job_path)

    tts_choice = {
        "backend": args.tts or job["tts"].get("backend") or cfg["tts"]["backend"],
        "voice": args.voice or job["tts"].get("voice"),
        "rate": args.rate or job["tts"].get("rate"),
    }
    backend_cfg = tts.resolve_backend(cfg, tts_choice["backend"], tts_choice["voice"], tts_choice["rate"])
    job["tts"] = {
        "backend": backend_cfg["backend"],
        "voice": backend_cfg.get("voice", ""),
        "rate": backend_cfg.get("rate", ""),
    }
    write_job(job, job_path)
    log.info(f"workspace: {ws}")
    log.info(f"review: {job['review']}   tts: {job['tts']['backend']}")

    first = args.from_stage or 1
    for stage in (1, 2, 3, 4):
        if stage < first:
            continue
        status = job["stages"].get(str(stage), "pending")
        if status == "done" and not args.force and args.from_stage is None:
            log.info(f"[{stage}/4] 已完成，跳过（--force 或 --from {stage} 可重做）")
            continue

        job["stages"][str(stage)] = "running"
        write_job(job, job_path)
        ok = True
        try:
            if stage == 1:
                parsed, ok = stage_md(ws, job, dirs, mode, log)
                if not ok:
                    job["stages"]["1"] = "paused"
                    write_job(job, job_path)
                    log.warn("已在 GATE 1 停止；改完 input.md 后重跑同一命令或 --from 1")
                    return 0
            elif stage == 2:
                backend_cfg = _gate_tts_choice(backend_cfg, mode, ws, log)
                job["tts"] = {
                    "backend": backend_cfg["backend"],
                    "voice": backend_cfg.get("voice", ""),
                    "rate": backend_cfg.get("rate", ""),
                }
                write_job(job, job_path)
                ok = stage_tts(ws, job, cfg, dirs, mode, args.only, args.force, backend_cfg,
                               log, job_path)
            elif stage == 3:
                ok = stage_ppt(ws, job, cfg, dirs, mode, args.only, args.force, log, job_path,
                               ppt_provider, svg_dir)
            else:
                ok = stage_video(ws, job, cfg, dirs, mode, args.only, args.force, log, job_path)
        except PipelineError:
            job["stages"][str(stage)] = "failed"
            write_job(job, job_path)
            raise

        if not ok:
            job["stages"][str(stage)] = "paused"
            write_job(job, job_path)
            log.warn(f"已在 GATE {stage} 停止；产物已保留，可用 --from {stage} 续跑")
            return 0

        job["stages"][str(stage)] = "partial" if args.only else "done"
        write_job(job, job_path)

    log.info("完成。")
    log.info(f"  成片: {dirs['4_video'] / 'final.mp4'}")
    log.info(f"  字幕: {dirs['4_video'] / 'final.srt'}")
    return 0


def main(argv: list[str] | None = None) -> int:
    _utf8_stdio()
    args = parse_args(argv)
    try:
        return run(args)
    except ToolMissing as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 2
    except PipelineError as exc:
        print(f"ERROR {exc}", file=sys.stderr)
        return 1
    except KeyboardInterrupt:
        print("\ninterrupted", file=sys.stderr)
        return 130


if __name__ == "__main__":
    raise SystemExit(main())
