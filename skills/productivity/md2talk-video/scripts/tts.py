"""Text-to-speech backends: audiocpp (wav only) and edge-tts (wav + srt)."""

from __future__ import annotations

from pathlib import Path

import srt
from paths import (
    Log,
    PipelineError,
    ToolMissing,
    ffprobe_duration,
    render_cmd,
    resolve_tool,
    run_cmd,
    split_template,
    write_json,
)

BACKEND_ALIASES = {
    "edge-tts": "edge-tts",
    "edge_tts": "edge-tts",
    "edge": "edge-tts",
    "audiocpp": "audiocpp",
    "audio-cpp": "audiocpp",
}


def resolve_backend(cfg: dict, backend: str | None = None, voice: str | None = None,
                    rate: str | None = None) -> dict:
    name = BACKEND_ALIASES.get((backend or cfg["tts"].get("backend", "edge-tts")).lower())
    if name is None:
        raise PipelineError(
            f"unknown tts backend {backend!r}; use one of {sorted(BACKEND_ALIASES)}"
        )
    key = "edge_tts" if name == "edge-tts" else "audiocpp"
    section = dict(cfg["tts"][key])
    if name == "edge-tts":
        if voice:
            section["voice"] = voice
        if rate:
            section["rate"] = rate
    return {"backend": name, **section}


def check_backend(backend_cfg: dict, ws: Path) -> None:
    """Fail fast, before any page is synthesized, if the tool is absent."""
    template = backend_cfg["cmd"]
    head = split_template(template)[0]
    if resolve_tool(head, ws) is None:
        raise ToolMissing(head, template, backend_cfg.get("install_hint", ""))


def _tts_text(speech: str) -> str:
    """Speech text as fed to the backend: pause markers become commas."""
    return srt.clean_text(speech).replace("\n", " ")


def synth_page(page: dict, backend_cfg: dict, cfg: dict, ws: Path,
               out_dir: Path, log: Log) -> dict:
    page_id = page["id"]
    build = out_dir / ".build"
    build.mkdir(parents=True, exist_ok=True)
    text_file = build / f"{page_id}.txt"
    text_file.write_text(_tts_text(page["speech"]), encoding="utf-8")

    wav = out_dir / f"{page_id}.wav"
    srt_path = out_dir / f"{page_id}.srt"
    backend = backend_cfg["backend"]

    if backend == "edge-tts":
        raw_media = build / f"{page_id}.mp3"
        raw_srt = build / f"{page_id}.raw.srt"
        ctx = {
            "voice": backend_cfg["voice"],
            "rate": backend_cfg["rate"],
            "text_file": str(text_file),
            "out_wav": str(raw_media),
            "raw_srt": str(raw_srt),
        }
        run_cmd(render_cmd(backend_cfg["cmd"], ctx, ws), ws, log)
        if not raw_media.exists():
            raise PipelineError(f"edge-tts produced no audio for {page_id}: {raw_media}")
        run_cmd(
            render_cmd(
                "{ffmpeg} -y -i {src} -ar 44100 -ac 1 {dst}",
                {"ffmpeg": cfg["compose"]["ffmpeg"], "src": str(raw_media), "dst": str(wav)},
                ws,
            ),
            ws,
            log,
        )
        segments = srt.parse_srt(raw_srt.read_text(encoding="utf-8")) if raw_srt.exists() else []
        if segments:
            srt_text = srt.to_srt(segments)
        else:
            log.warn(f"{page_id}: edge-tts gave no subtitles, estimating timings")
            srt_text = srt.from_text(page["speech"], 1000)
    else:
        ctx = {
            "bin": backend_cfg["bin"],
            "model": backend_cfg["model"],
            "ref_audio": backend_cfg["ref_audio"],
            "text_file": str(text_file),
            "out_wav": str(wav),
        }
        run_cmd(render_cmd(backend_cfg["cmd"], ctx, ws), ws, log)
        if not wav.exists():
            raise PipelineError(f"audiocpp produced no audio for {page_id}: {wav}")
        srt_text = None  # needs the real duration, filled in below

    duration = ffprobe_duration(wav, cfg, ws, log)
    if srt_text is None:
        srt_text = srt.from_text(page["speech"], int(duration * 1000))
    srt_path.write_text(srt_text, encoding="utf-8")

    record = {
        "id": page_id,
        "wav": str(wav.relative_to(ws)),
        "srt": str(srt_path.relative_to(ws)),
        "wav_dur": round(duration, 3),
        "srt_lines": len(srt.parse_srt(srt_text)),
        "backend": backend,
        "voice": backend_cfg.get("voice", ""),
    }
    log.info(
        f"{page_id}: {record['wav_dur']:.2f}s, {record['srt_lines']} subtitle lines "
        f"({backend})"
    )
    return record


def write_manifest(records: list[dict], out_dir: Path, backend_cfg: dict) -> dict:
    manifest = {
        "backend": backend_cfg["backend"],
        "voice": backend_cfg.get("voice", ""),
        "total_dur": round(sum(r["wav_dur"] for r in records), 3),
        "pages": records,
    }
    write_json(out_dir / "manifest.json", manifest)
    return manifest
