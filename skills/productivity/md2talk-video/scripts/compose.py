"""ffmpeg assembly: mux page audio, concat pages, optional subtitle burn-in."""

from __future__ import annotations

from pathlib import Path

from paths import Log, PipelineError, render_cmd, run_cmd

VIDEO_ENCODE = [
    "-c:v", "libx264", "-preset", "veryfast", "-crf", "20",
    "-pix_fmt", "yuv420p", "-r", "{fps}", "-movflags", "+faststart",
]


def mux_page(silent: Path, wav: Path, duration: float, out_mp4: Path,
             cfg: dict, ws: Path, log: Log) -> Path:
    out_mp4.parent.mkdir(parents=True, exist_ok=True)
    template = (
        "{ffmpeg} -y -i {video} -i {audio}"
        " -map 0:v:0 -map 1:a:0"
        " -vf tpad=stop_mode=clone:stop_duration=5"
        " -t {dur} -c:a aac -b:a 192k -ar 44100"
        " " + " ".join(VIDEO_ENCODE) + " {out}"
    )
    ctx = {
        "ffmpeg": cfg["compose"]["ffmpeg"],
        "video": str(silent),
        "audio": str(wav),
        "dur": f"{duration:.3f}",
        "fps": str(cfg["render"].get("fps", 30)),
        "out": str(out_mp4),
    }
    run_cmd(render_cmd(template, ctx, ws), ws, log)
    log.info(f"{out_mp4.name}: muxed {duration:.2f}s")
    return out_mp4


def concat(pages: list[dict], out_mp4: Path, cfg: dict, ws: Path, log: Log) -> Path:
    if not pages:
        raise PipelineError("nothing to concat: no page videos")
    build = out_mp4.parent / ".build"
    build.mkdir(parents=True, exist_ok=True)
    list_file = build / "concat.txt"
    lines = []
    for page in pages:
        path = (ws / page["video"]).resolve()
        lines.append("file '{}'".format(str(path).replace("'", r"'\''")))
    list_file.write_text("\n".join(lines) + "\n", encoding="utf-8")
    ctx = {"ffmpeg": cfg["compose"]["ffmpeg"], "list": str(list_file), "out": str(out_mp4)}
    run_cmd(
        render_cmd(
            "{ffmpeg} -y -f concat -safe 0 -i {list} -c copy -movflags +faststart {out}",
            ctx,
            ws,
        ),
        ws,
        log,
    )
    log.info(f"final: {out_mp4.name}")
    return out_mp4


def burn_subtitles(video: Path, srt_path: Path, out_mp4: Path, cfg: dict,
                   ws: Path, log: Log) -> Path:
    escaped = str(srt_path).replace("\\", "/").replace(":", r"\:")
    ctx = {"ffmpeg": cfg["compose"]["ffmpeg"], "video": str(video),
           "srt": escaped, "out": str(out_mp4)}
    template = (
        '{ffmpeg} -y -i {video} -vf "subtitles=\'{srt}\'" '
        "-c:v libx264 -preset veryfast -crf 20 -c:a copy {out}"
    )
    run_cmd(render_cmd(template, ctx, ws), ws, log)
    log.info(f"subtitles burned: {out_mp4.name}")
    return out_mp4
