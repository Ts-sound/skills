"""Subtitle timing: split, estimate, shift, merge.

edge-tts gives real timestamps, so its SRT is shifted per page and merged as
is. audiocpp gives no timestamps, so sentences are split and the page's wav
duration is distributed by text weight. Both backends end up with one page SRT
and a global `final.srt` whose offsets equal the sum of earlier page durations.
"""

from __future__ import annotations

import math
import re

HARD_PUNCT = "。！？!?；;"
SOFT_PUNCT = "，,、：:"
MAX_CHARS = 28
MIN_DUR_MS = 600
MAX_DUR_MS = 8000
PAUSE_RE = re.compile(r"\[\s*pause\s*\]", re.IGNORECASE)
SRT_TIME_RE = re.compile(
    r"(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})\s*-->\s*(\d{1,2}):(\d{2}):(\d{2})[,.](\d{3})"
)


def clean_text(text: str) -> str:
    text = PAUSE_RE.sub("，", text)
    text = re.sub(r"\s+", " ", text).strip()
    # A [pause] right after 。 or ？ should not leave "。 ，"; keep the stronger mark.
    text = re.sub(r"([。！？!?；;])[，,、]+", r"\1", text)
    text = re.sub(r"([，,、])[，,、]+", r"\1", text)
    text = re.sub(r"\s+([，。！？；：,、])", r"\1", text)
    return text


def _is_cjk(ch: str) -> bool:
    return "\u3400" <= ch <= "\u9fff" or "\uf900" <= ch <= "\ufaff"


def weight(text: str) -> float:
    """CJK counts per character, latin per word."""
    cjk = sum(1 for ch in text if _is_cjk(ch))
    latin = len(re.findall(r"[A-Za-z0-9][A-Za-z0-9'._-]*", text))
    return max(cjk + latin + 0.5, 0.5)


def split_sentences(text: str, max_chars: int = MAX_CHARS) -> list[str]:
    text = clean_text(text)
    if not text:
        return []
    chunks: list[str] = []
    buf = ""
    for ch in text:
        buf += ch
        if ch in HARD_PUNCT and len(buf.strip()) >= 2:
            chunks.append(buf.strip())
            buf = ""
    if buf.strip():
        chunks.append(buf.strip())

    out: list[str] = []
    for chunk in chunks:
        if sum(weight(c) for c in chunk) <= max_chars:
            out.append(chunk)
            continue
        cur, w = "", 0.0
        for ch in chunk:
            cur += ch
            w += weight(ch)
            if w >= max_chars and (ch in SOFT_PUNCT or ch in HARD_PUNCT or ch == " "):
                out.append(cur.strip())
                cur, w = "", 0.0
        if cur.strip():
            out.append(cur.strip())
    return [s for s in out if s]


def _split_text_even(text: str, parts: int) -> list[str]:
    """Split one sentence into `parts` roughly equal pieces at natural breaks."""
    if parts <= 1:
        return [text]
    target = math.ceil(len(text) / parts)
    pieces: list[str] = []
    cur = ""
    for ch in text:
        cur += ch
        if len(cur) >= target and (ch in SOFT_PUNCT or ch in HARD_PUNCT or ch == " "):
            pieces.append(cur.strip())
            cur = ""
    if cur.strip():
        if pieces and len(pieces) == parts:
            pieces[-1] += cur
        else:
            pieces.append(cur.strip())
    while len(pieces) > parts:  # merge overflow back into the last piece
        pieces[-2] += pieces.pop()
    return [p for p in pieces if p]


def _fmt(ms: int) -> str:
    ms = max(0, int(round(ms)))
    hours, rem = divmod(ms, 3_600_000)
    minutes, rem = divmod(rem, 60_000)
    seconds, millis = divmod(rem, 1000)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{millis:03d}"


def segments_from_text(text: str, total_ms: int) -> list[dict]:
    """Estimate per-sentence timings across a clip of `total_ms`."""
    sentences = split_sentences(text)
    if not sentences:
        return []
    total_ms = max(int(total_ms), len(sentences) * MIN_DUR_MS)

    weights = [weight(s) for s in sentences]
    total_w = sum(weights)
    durs = [max(MIN_DUR_MS, round(total_ms * w / total_w)) for w in weights]

    # Long sentences are re-split so no subtitle sits past MAX_DUR_MS.
    texts: list[str] = []
    out_durs: list[int] = []
    for sentence, dur in zip(sentences, durs):
        if dur <= MAX_DUR_MS:
            texts.append(sentence)
            out_durs.append(dur)
            continue
        parts = min(4, math.ceil(dur / MAX_DUR_MS))
        pieces = _split_text_even(sentence, parts)
        share = dur / len(pieces)
        for piece in pieces:
            texts.append(piece)
            out_durs.append(int(share))

    # Glue subtitles shorter than MIN_DUR_MS onto their neighbour.
    merged: list[tuple[str, int]] = []
    for sentence, dur in zip(texts, out_durs):
        if merged and dur < MIN_DUR_MS:
            prev_text, prev_dur = merged[-1]
            merged[-1] = (prev_text + sentence, prev_dur + dur)
        else:
            merged.append((sentence, dur))

    # Normalise to exactly total_ms.
    scale = total_ms / max(1, sum(d for _, d in merged))
    segments: list[dict] = []
    cursor = 0
    for i, (sentence, dur) in enumerate(merged):
        dur = int(round(dur * scale))
        if i == len(merged) - 1:
            dur = total_ms - cursor
        segments.append({"start": cursor, "end": cursor + dur, "text": sentence})
        cursor += dur
    return segments


def to_srt(segments: list[dict]) -> str:
    lines: list[str] = []
    for i, seg in enumerate(segments, 1):
        lines.append(str(i))
        lines.append(f"{_fmt(seg['start'])} --> {_fmt(max(seg['end'], seg['start'] + 200))}")
        lines.append(seg["text"])
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"


def from_text(text: str, total_ms: int) -> str:
    return to_srt(segments_from_text(text, total_ms))


def parse_srt(srt_text: str) -> list[dict]:
    segments: list[dict] = []
    blocks = re.split(r"\n\s*\n", srt_text.replace("\r\n", "\n").strip())
    for block in blocks:
        lines = [line.strip() for line in block.splitlines() if line.strip()]
        if len(lines) < 2:
            continue
        match = None
        for i, line in enumerate(lines):
            match = SRT_TIME_RE.search(line)
            if match:
                start_idx = i
                break
        if not match:
            continue
        g = [int(x) for x in match.groups()]
        start = ((g[0] * 60 + g[1]) * 60 + g[2]) * 1000 + g[3]
        end = ((g[4] * 60 + g[5]) * 60 + g[6]) * 1000 + g[7]
        text = " ".join(lines[start_idx + 1 :])
        text = clean_text(text)
        if text:
            segments.append({"start": start, "end": end, "text": text})
    return segments


def shift(segments: list[dict], offset_ms: int) -> list[dict]:
    return [
        {"start": s["start"] + offset_ms, "end": s["end"] + offset_ms, "text": s["text"]}
        for s in segments
    ]


def merge_page_srts(pairs: list[tuple[str, int]]) -> str:
    """[(page_srt_text, page_offset_ms), ...] -> global srt."""
    merged: list[dict] = []
    for srt_text, offset in pairs:
        merged.extend(shift(parse_srt(srt_text), offset))
    merged.sort(key=lambda s: s["start"])
    return to_srt(merged)
