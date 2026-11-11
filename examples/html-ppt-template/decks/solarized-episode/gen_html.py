# -*- coding: utf-8 -*-
"""Bundle the template SVGs into one self-contained HTML deck."""
import pathlib
import re

WS = pathlib.Path(r"C:\Users\17853\.agents\skills\ppt-master\templates\decks\solarized-episode")
SRC = WS / "templates"
OUT = WS / "exports" / "solarized-episode-deck.html"

files = sorted(SRC.glob("*.svg"))


def inline(svg_text, idx):
    s = svg_text.strip()
    s = re.sub(r"^<\?xml[^>]*\?>\s*", "", s)
    # namespace the gradient id so 16 documents on one page cannot collide
    s = s.replace('id="ep-wash"', f'id="ep-wash-{idx}"')
    s = s.replace("url(#ep-wash)", f"url(#ep-wash-{idx})")
    # let CSS control size
    s = s.replace('width="1280" height="720"', 'width="100%" height="100%"')
    return s


slides = []
for i, f in enumerate(files, start=1):
    slides.append(
        f'    <section class="slide" id="s{i}" aria-label="{f.stem}">\n'
        f"      {inline(f.read_text(encoding='utf-8'), i)}\n"
        f"    </section>"
    )

HTML = """<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Solarized Episode · 16 页</title>
<style>
  :root { --paper:#FDF6E3; --ink:#073642; --muted:#93A1A1; --accent:#CB4B16; }
  * { box-sizing:border-box; }
  html,body { margin:0; height:100%; background:#1b1b1b; }
  body {
    font-family:"Noto Sans SC","Source Han Sans SC",PingFang SC,Microsoft YaHei,sans-serif;
    display:flex; align-items:center; justify-content:center; overflow:hidden;
  }
  .stage {
    position:relative;
    width:min(100vw, calc(100vh * 16 / 9));
    height:min(100vh, calc(100vw * 9 / 16));
    background:var(--paper);
    box-shadow:0 24px 80px rgba(0,0,0,.45);
  }
  .slide {
    position:absolute; inset:0;
    opacity:0; visibility:hidden;
    transition:opacity .22s ease;
  }
  .slide.active { opacity:1; visibility:visible; }
  .slide svg { display:block; width:100%; height:100%; }
  .hud {
    position:fixed; right:18px; bottom:14px;
    color:#9aa0a0; font-size:12px; letter-spacing:.14em;
    font-variant-numeric:tabular-nums; user-select:none;
  }
  .hint {
    position:fixed; left:18px; bottom:14px;
    color:#6d7373; font-size:11px; letter-spacing:.08em;
    transition:opacity .4s ease; user-select:none;
  }
  .hint.fade { opacity:0; }
  .bar {
    position:fixed; left:0; top:0; height:2px; background:var(--accent);
    width:0; transition:width .18s ease;
  }
  @media print {
    html,body { background:#fff; display:block; overflow:visible; }
    .stage { width:100%; height:auto; box-shadow:none; }
    .slide { position:relative; opacity:1; visibility:visible; page-break-after:always; }
    .slide:last-child { page-break-after:auto; }
    .hud,.hint,.bar { display:none; }
    @page { size:1280px 720px; margin:0; }
  }
</style>
</head>
<body>
<div class="bar" id="bar"></div>
<div class="stage">
__SLIDES__
</div>
<div class="hud"><span id="page">1</span> / __TOTAL__</div>
<div class="hint" id="hint">← → 翻页 · F 全屏 · P 打印 / 存 PDF</div>
<script>
  const slides = [...document.querySelectorAll('.slide')];
  const total = slides.length;
  const bar = document.getElementById('bar');
  const pageEl = document.getElementById('page');
  const hint = document.getElementById('hint');
  let i = 0;

  function show(n) {
    i = Math.max(0, Math.min(total - 1, n));
    slides.forEach((s, k) => s.classList.toggle('active', k === i));
    pageEl.textContent = i + 1;
    bar.style.width = ((i + 1) / total * 100) + '%';
    history.replaceState(null, '', '#' + (i + 1));
  }
  const next = () => show(i + 1);
  const prev = () => show(i - 1);

  addEventListener('keydown', e => {
    if (['ArrowRight', 'ArrowDown', 'PageDown', ' ', 'Enter'].includes(e.key)) { e.preventDefault(); next(); }
    else if (['ArrowLeft', 'ArrowUp', 'PageUp', 'Backspace'].includes(e.key)) { e.preventDefault(); prev(); }
    else if (e.key === 'Home') show(0);
    else if (e.key === 'End') show(total - 1);
    else if (e.key === 'f' || e.key === 'F') {
      if (document.fullscreenElement) document.exitFullscreen();
      else document.documentElement.requestFullscreen();
    } else if (e.key === 'p' || e.key === 'P') { print(); }
  });

  document.addEventListener('click', e => {
    const x = e.clientX / innerWidth;
    if (x > 0.62) next();
    else if (x < 0.38) prev();
  });

  let tx = null;
  addEventListener('touchstart', e => { tx = e.touches[0].clientX; }, { passive: true });
  addEventListener('touchend', e => {
    if (tx === null) return;
    const dx = e.changedTouches[0].clientX - tx;
    if (Math.abs(dx) > 40) (dx < 0 ? next : prev)();
    tx = null;
  }, { passive: true });

  setTimeout(() => hint.classList.add('fade'), 4200);

  const start = parseInt(location.hash.slice(1), 10);
  show(Number.isFinite(start) ? start - 1 : 0);
</script>
</body>
</html>
"""

html = HTML.replace("__SLIDES__", "\n".join(slides)).replace("__TOTAL__", str(len(files)))
OUT.parent.mkdir(parents=True, exist_ok=True)
OUT.write_text(html, encoding="utf-8")
print("wrote", OUT, f"{OUT.stat().st_size/1024:.0f} KB")
