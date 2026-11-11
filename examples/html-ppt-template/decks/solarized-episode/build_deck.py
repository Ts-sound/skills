# -*- coding: utf-8 -*-
"""Build the 16-page Solarized Episode deck template."""
import pathlib

OUT = pathlib.Path(r"C:\Users\17853\.agents\skills\ppt-master\templates\decks\solarized-episode\templates")

SANS = "Noto Sans SC, Source Han Sans SC, Arial, sans-serif"
SERIF = "Noto Serif SC, Source Han Serif SC, serif"

BG, PANEL, INK, BODY, MUTED, META = "#FDF6E3", "#EEE8D5", "#073642", "#657B83", "#93A1A1", "#586E75"
ORANGE, BLUE, YELLOW, CYAN, RULE = "#CB4B16", "#268BD2", "#B58900", "#2AA198", "#E7DCC1"
CHIP_DONE_BG, CHIP_DONE_FG = "#586E75", "#FDF6E3"
CHIP_IDLE_BG, CHIP_IDLE_FG = "#F0E8D4", "#93A1A1"

TOTAL = 16
CHAPTERS = ["开场判断", "不是工具清单", "超级个体机制", "本期生产链路", "五层能力栈", "老板与个体行动", "收束与评论"]

# ---- chips geometry (fixed widths, state changes colour only) ----
WEIGHTS = [len(c) + 6 for c in CHAPTERS]
TOTAL_W, GAP = 1016, 8
FREESPACE = TOTAL_W - GAP * (len(CHAPTERS) - 1)
WIDTHS = [round(FREESPACE * w / sum(WEIGHTS), 1) for w in WEIGHTS]
XS = []
x = 80.0
for w in WIDTHS:
    XS.append(round(x, 1))
    x += w + GAP


def chips(active):
    """active = 1-based chapter index, or 0 for none."""
    parts = ['  <g id="ep-chapter-chips" data-pptx-bounds="80 650 1016 38">']
    for i, label in enumerate(CHAPTERS, start=1):
        if i == active:
            bg, fg, weight = ORANGE, "#FFFCF3", True
        elif active and i < active:
            bg, fg, weight = CHIP_DONE_BG, CHIP_DONE_FG, False
        else:
            bg, fg, weight = CHIP_IDLE_BG, CHIP_IDLE_FG, False
        cx = XS[i - 1] + WIDTHS[i - 1] / 2
        b = ' font-weight="700"' if weight else ""
        parts.append(
            f'    <rect id="chip-{i:02d}-bg" x="{XS[i-1]}" y="650" width="{WIDTHS[i-1]}" height="38" rx="19" fill="{bg}"/>'
        )
        parts.append(
            f'    <text id="chip-{i:02d}-label" x="{cx:.1f}" y="674" text-anchor="middle" fill="{fg}" font-size="12"{b} letter-spacing="1">{label}</text>'
        )
    parts.append("  </g>")
    return "\n".join(parts)


def page_number(n):
    return (
        '  <g id="ep-slide-number-slot" data-pptx-placeholder="slide-number" data-pptx-bounds="1110 656 90 30">\n'
        f'    <text id="ep-slide-number" data-pptx-carrier="true" x="1200" y="676" text-anchor="end" fill="{MUTED}" font-size="12" letter-spacing="1">P{n:02d} / {TOTAL}</text>\n'
        "  </g>"
    )


HEAD = """<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1280 720" width="1280" height="720"
  data-pptx-master="solarized_episode_master" data-pptx-master-name="Solarized Episode"
  data-pptx-layout="{key}" data-pptx-layout-name="{picker}"
  font-family="{sans}">
  <defs>
    <linearGradient id="ep-wash" x1="0" y1="0" x2="0" y2="1">
      <stop offset="0" stop-color="#FFFCF3"/>
      <stop offset="1" stop-color="{bg}"/>
    </linearGradient>
  </defs>
  <rect id="ep-master-bg" data-pptx-layer="master" x="0" y="0" width="1280" height="720" fill="{bg}"/>
  <rect id="ep-master-wash" data-pptx-layer="master" x="0" y="0" width="1280" height="300" fill="url(#ep-wash)"/>
"""

BAR = f'  <rect id="ep-rule" data-pptx-layer="layout" x="80" y="58" width="56" height="4" fill="{ORANGE}"/>'


def svg(key, picker, atoms, body, active, n):
    return (
        HEAD.format(key=key, picker=picker, sans=SANS, bg=BG)
        + atoms
        + "\n" + body
        + "\n" + page_number(n)
        + "\n" + chips(active)
        + "\n</svg>\n"
    )


def cover():
    bars = []
    import math
    for i in range(33):
        x = 380 + i * 16
        env = math.sin(math.pi * (i / 32.0))
        h = 12 + 40 * env
        y = 394 - h / 2
        op = 0.45 + 0.55 * env
        bars.append(
            f'    <rect x="{x}" y="{y:.1f}" width="6" height="{h:.1f}" rx="3" fill="{ORANGE}" fill-opacity="{op:.2f}"/>'
        )
    atoms = (
        f'  <rect id="ep-wave-pill" data-pptx-layer="layout" x="340" y="348" width="600" height="92" rx="46" fill="{INK}"/>\n'
        f'  <g id="ep-wave-bars" data-pptx-bounds="340 348 600 92">\n' + "\n".join(bars) + "\n  </g>"
    )
    body = f"""  <g id="ep-kicker-slot" data-pptx-placeholder="body" data-pptx-bounds="80 64 1120 30">
    <text id="ep-kicker" data-pptx-carrier="true" x="640" y="84" text-anchor="middle" fill="{YELLOW}" font-size="15" font-weight="700" letter-spacing="6">EP.01 / SOLARIZED SERIES</text>
  </g>
  <g id="ep-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 116 1120 164">
    <text id="ep-title" data-pptx-carrier="true" x="640" y="182" text-anchor="middle" fill="{INK}" font-family="{SERIF}" font-size="46" font-weight="700" letter-spacing="4"><tspan x="640" dy="0">一切皆插件的</tspan><tspan x="640" dy="66">Agent 框架</tspan></text>
  </g>
  <g id="ep-subtitle-slot" data-pptx-placeholder="subtitle" data-pptx-bounds="80 268 1120 40">
    <text id="ep-subtitle" data-pptx-carrier="true" x="640" y="302" text-anchor="middle" fill="{BODY}" font-size="17">31 轮对话 · 650+ 步执行 · 缓存命中率接近 100%</text>
  </g>
  <g id="ep-date-slot" data-pptx-placeholder="date" data-pptx-bounds="80 596 320 28">
    <text id="ep-date" data-pptx-carrier="true" x="80" y="616" fill="{MUTED}" font-size="12" letter-spacing="2">2026.11 · 内测记录</text>
  </g>
  <g id="ep-author-slot" data-pptx-placeholder="body" data-pptx-bounds="860 596 340 28">
    <text id="ep-author" data-pptx-carrier="true" x="1200" y="616" text-anchor="end" fill="{MUTED}" font-size="12" letter-spacing="2">深度测评 / 阿江</text>
  </g>"""
    return svg("cover", "Cover — Episode Opener", atoms, body, 0, 1)


TOC_ROWS = [
    ("开场判断：现在必须 All in AI"),
    ("不是工具清单：先看结构"),
    ("超级个体机制：缓存与可追踪"),
    ("本期生产链路：31 轮 · 650+ 步"),
    ("五层能力栈：从插件到工作台"),
    ("老板与个体行动：三步落地"),
    ("收束与评论：判断与下一步"),
]


def toc():
    rows = []
    for i, title in enumerate(TOC_ROWS, start=1):
        x = "80" if i == 1 else '80" dy="48'
        rows.append(
            f'<tspan x="{x}"><tspan fill="{ORANGE}" font-weight="700">{i:02d}</tspan>　{title}</tspan>'
        )
    atoms = (
        BAR + "\n"
        f'  <rect id="ep-toc-rule" data-pptx-layer="layout" x="80" y="560" width="1120" height="1" fill="{RULE}"/>'
    )
    body = f"""  <g id="ep-agenda-kicker-slot" data-pptx-placeholder="body" data-pptx-bounds="80 96 600 24">
    <text id="ep-agenda-kicker" data-pptx-carrier="true" x="80" y="114" fill="{YELLOW}" font-size="12" font-weight="700" letter-spacing="6">SECTIONS 01 — 07</text>
  </g>
  <g id="ep-agenda-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 132 1120 76">
    <text id="ep-agenda-title" data-pptx-carrier="true" x="80" y="188" fill="{INK}" font-family="{SERIF}" font-size="40" font-weight="700" letter-spacing="4">本期导航</text>
  </g>
  <g id="ep-agenda-list-slot" data-pptx-placeholder="body" data-pptx-bounds="80 220 1120 340">
    <text id="ep-agenda-list" data-pptx-carrier="true" x="80" y="256" fill="{BODY}" font-size="20">{''.join(rows)}</text>
  </g>"""
    return svg("agenda", "Agenda — Episode Map", atoms, body, 0, 2)


def section(num, title, desc, page, active):
    atoms = BAR
    body = f"""  <g id="ep-section-number-slot" data-pptx-placeholder="body" data-pptx-bounds="80 150 640 252">
    <text id="ep-section-number" data-pptx-carrier="true" x="80" y="352" fill="#EFE3C6" font-size="132" font-weight="700" letter-spacing="-2">{num}</text>
  </g>
  <g id="ep-section-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 392 1040 88">
    <text id="ep-section-title" data-pptx-carrier="true" x="80" y="452" fill="{INK}" font-family="{SERIF}" font-size="44" font-weight="700" letter-spacing="2">{title}</text>
  </g>
  <g id="ep-section-desc-slot" data-pptx-placeholder="body" data-pptx-bounds="80 474 940 92">
    <text id="ep-section-desc" data-pptx-carrier="true" x="80" y="510" fill="{BODY}" font-size="17">{desc}</text>
  </g>"""
    return svg("section", "Chapter Opener", atoms, body, active, page)


def content(title, lines, page, active):
    atoms = BAR
    spans = "".join(
        f'<tspan x="80" dy="{0 if i == 0 else 34}">{line}</tspan>' for i, line in enumerate(lines)
    )
    body = f"""  <g id="ep-content-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 84 1120 64">
    <text id="ep-content-title" data-pptx-carrier="true" x="80" y="132" fill="{INK}" font-family="{SERIF}" font-size="38" font-weight="700" letter-spacing="2">{title}</text>
  </g>
  <g id="ep-content-body-slot" data-pptx-placeholder="body" data-pptx-bounds="80 190 1120 380">
    <text id="ep-content-body" data-pptx-carrier="true" x="80" y="224" fill="{BODY}" font-size="18">{spans}</text>
  </g>"""
    return svg("content", "Title and Content", atoms, body, active, page)


def cards(title, cards_data, summary, page, active):
    slots = []
    plates = []
    accents = [BLUE, YELLOW, CYAN]
    for i, (tag, head, l1, l2, l3) in enumerate(cards_data):
        x = [80, 467, 854][i]
        tx = x + 26
        plates.append(
            f'  <rect id="ep-card-{i+1}-plate" data-pptx-layer="layout" x="{x}" y="196" width="346" height="300" rx="16" fill="{PANEL}" stroke="{RULE}" stroke-width="1"/>\n'
            f'  <rect id="ep-card-{i+1}-rule" data-pptx-layer="layout" x="{x+30}" y="214" width="48" height="3" fill="{accents[i]}"/>'
        )
        slots.append(
            f"""  <g id="ep-card-{i+1}-slot" data-pptx-placeholder="object" data-pptx-bounds="{x} 196 346 300">
    <text id="ep-card-{i+1}-text" data-pptx-carrier="true" x="{tx}" y="266" fill="{YELLOW}" font-size="11" font-weight="700" letter-spacing="2">{tag}<tspan x="{tx}" dy="38" font-family="{SERIF}" font-size="21" font-weight="700" letter-spacing="0" fill="{INK}">{head}</tspan><tspan x="{tx}" dy="38" font-size="14" font-weight="400" letter-spacing="0" fill="{BODY}">{l1}</tspan><tspan x="{tx}" dy="26" font-size="14" font-weight="400" fill="{BODY}">{l2}</tspan><tspan x="{tx}" dy="26" font-size="14" font-weight="400" fill="{BODY}">{l3}</tspan></text>
  </g>"""
        )
    body = f"""  <g id="ep-cards-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 84 1120 64">
    <text id="ep-cards-title" data-pptx-carrier="true" x="80" y="132" fill="{INK}" font-family="{SERIF}" font-size="38" font-weight="700" letter-spacing="2">{title}</text>
  </g>
""" + "\n".join(slots) + f"""
  <g id="ep-cards-summary-slot" data-pptx-placeholder="body" data-pptx-idx="6" data-pptx-bounds="80 536 1120 42">
    <text id="ep-cards-summary" data-pptx-carrier="true" x="80" y="564" fill="{META}" font-size="17">{summary}</text>
  </g>"""
    atoms = BAR + "\n" + "\n".join(plates)
    return svg("content-cards", "Three Arguments", atoms, body, active, page)


def data(title, metrics, takeaway, page, active):
    atoms = BAR
    slots = []
    colors = [BLUE, YELLOW, ORANGE, CYAN]
    xs = [80, 366, 652, 938]
    for i, (value, label) in enumerate(metrics):
        x = xs[i]
        slots.append(
            f"""  <rect x="{x}" y="196" width="262" height="3" fill="{colors[i]}"/>
  <g id="ep-metric-{i+1}-slot" data-pptx-placeholder="object" data-pptx-bounds="{x} 204 262 110">
    <text id="ep-metric-{i+1}-text" data-pptx-carrier="true" x="{x}" y="266" fill="{colors[i]}" font-size="46" font-weight="700">{value}<tspan x="{x}" dy="34" font-size="13" font-weight="400" fill="{MUTED}">{label}</tspan></text>
  </g>"""
        )
    body = f"""  <g id="ep-data-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 84 1120 64">
    <text id="ep-data-title" data-pptx-carrier="true" x="80" y="132" fill="{INK}" font-family="{SERIF}" font-size="38" font-weight="700" letter-spacing="2">{title}</text>
  </g>
""" + "\n".join(slots) + f"""
  <rect id="ep-takeaway-panel" x="80" y="420" width="1120" height="150" rx="16" fill="{PANEL}"/>
  <rect id="ep-takeaway-bar" x="80" y="444" width="3" height="102" fill="{ORANGE}"/>
  <g id="ep-data-takeaway-slot" data-pptx-placeholder="body" data-pptx-bounds="104 440 1072 110">
    <text id="ep-data-takeaway" data-pptx-carrier="true" x="104" y="496" fill="{INK}" font-size="16">{takeaway[0]}<tspan x="104" dy="30" fill="{BODY}">{takeaway[1]}</tspan></text>
  </g>"""
    return svg("content-data", "Metric Strip", atoms, body, active, page)


def closing(title, subtitle, copy, page, active):
    atoms = (
        BAR + "\n"
        f'  <rect id="ep-closing-rule" data-pptx-layer="layout" x="600" y="392" width="80" height="2" fill="{ORANGE}"/>'
    )
    body = f"""  <g id="ep-closing-title-slot" data-pptx-placeholder="title" data-pptx-bounds="80 190 1120 120">
    <text id="ep-closing-title" data-pptx-carrier="true" x="640" y="272" text-anchor="middle" fill="{INK}" font-family="{SERIF}" font-size="46" font-weight="700" letter-spacing="4">{title}</text>
  </g>
  <g id="ep-closing-contact-slot" data-pptx-placeholder="subtitle" data-pptx-bounds="80 318 1120 46">
    <text id="ep-closing-contact" data-pptx-carrier="true" x="640" y="348" text-anchor="middle" fill="{BODY}" font-size="17">{subtitle}</text>
  </g>
  <g id="ep-closing-copy-slot" data-pptx-placeholder="body" data-pptx-bounds="80 596 1120 28">
    <text id="ep-closing-copy" data-pptx-carrier="true" x="80" y="616" fill="{MUTED}" font-size="12" letter-spacing="1">{copy}</text>
  </g>"""
    return svg("closing", "Closing", atoms, body, active, page)


PAGES = []

PAGES.append(("01_cover", cover()))
PAGES.append(("02_toc", toc()))
PAGES.append(("03_section", section("01", "开场判断：现在必须 All in AI",
    "先把结论摆到前面：工具会过时，结构不会。这一期只讨论一件事——什么样的框架值得押注。", 3, 1)))
PAGES.append(("04_content", content("三个判断，一个前提", [
    "模型能力还在涨，但差距在收窄，单点性能不再是护城河。",
    "真正的分化来自结构：插件怎么接、成本怎么摊、社区怎么长。",
    "判断一：可插拔。任何一层都能被替换，替换后其余层照常工作。",
    "判断二：可追踪。每一步都能复盘，成本才有机会被缓存摊平。",
    "判断三：可生长。插件生态是否一周内长出四种玩法。",
], 4, 1)))
PAGES.append(("05_section", section("02", "不是工具清单，先看结构",
    "把框架拆成五个可替换的接插件，看它们各自负责什么，以及替换之后会发生什么。", 5, 2)))
PAGES.append(("06_content_cards", cards("五个接插件，各管一段", [
    ("01 / 结构", "一切皆插件", "界面、执行器、会话存储都是接插件。", "换掉任何一个，其余两层照常工作。", "这就是可替换性的证据。"),
    ("02 / 证据", "缓存接近全命中", "31 轮、650+ 步的记录里，重复", "计算被缓存吃掉，成本曲线不再", "线性，命中率约为 100%。"),
    ("03 / 生态", "社区接得住", "一周内出现门户皮肤、Claude Code", "风格界面、全能工作台与多 Agent", "协作四种玩法。"),
], "三项证据合起来就是判断：可插拔、低成本、生态活跃——缺任何一条，都不值得押注。", 6, 2)))
PAGES.append(("07_section", section("03", "超级个体机制：缓存与可追踪",
    "同一个人为什么能顶一个团队？答案不在勤奋，而在把重复劳动沉进结构里。", 7, 3)))
PAGES.append(("08_content_data", data("本期链路的关键数据", [
    ("31", "轮对话 · 单次内测"), ("650+", "执行步数"), ("≈100%", "缓存命中率"), ("21", "首轮 token 数"),
], ("成本优势不来自更小的模型，而来自可追踪的缓存结构：同类任务第二次跑，几乎是免费的。",
    "这也是为什么“全程可追踪”不是体验细节，而是成本结构本身。"), 8, 3)))
PAGES.append(("09_section", section("04", "本期生产链路：31 轮 · 650+ 步",
    "从一句需求到一份可交付的模板，中间发生了什么，哪些环节真的省了钱。", 9, 4)))
PAGES.append(("10_content_data", data("成本被摊平在哪一段", [
    ("4×", "复用任务提速"), ("92%", "步骤可复用"), ("1 人", "完成全链路"), ("7 天", "从想法到成稿"),
], ("链路的价值不是更快，而是可复现：同一套结构第二次跑，几乎只剩判断成本。",
    "省下来的不是人力，而是每一次重新想清楚的那段时间。"), 10, 4)))
PAGES.append(("11_section", section("05", "五层能力栈：从插件到工作台",
    "插件、技能、工作流、界面、Agent——五层各自可替换，组合起来才是一个工作台。", 11, 5)))
PAGES.append(("12_content_cards", cards("五层栈，从下往上长", [
    ("01 / 底座", "插件层", "模型、工具、存储都以插件形式接入。", "换模型不改业务，换存储不丢上下文。", "接入成本由此变成一次性投入。"),
    ("02 / 中间", "技能与工作流", "技能是可复用的说明书，工作流是", "可复用的步骤，两者都不绑定具体", "模型，也不绑定具体界面。"),
    ("03 / 顶层", "界面与 Agent", "界面可以换皮肤，Agent 可以换", "执行器；同一套能力，既能长成", "门户，也能长成桌面端。"),
], "层与层之间只有接口约定：下层不动，上层可以反复重做。", 12, 5)))
PAGES.append(("13_section", section("06", "老板与个体行动：三步落地",
    "不需要一次性重构。先找一段最重复的流程，把它变成可复用的结构。", 13, 6)))
PAGES.append(("14_content", content("三步落地，先跑一遍", [
    "第一步：选一段每周都重复的流程，记录它的输入、判断与输出。",
    "第二步：把判断写成技能，把步骤写成工作流，先不追求全自动。",
    "第三步：接入可替换的界面，让不写代码的人也能把它跑起来。",
    "衡量标准只有一条：第二次执行的时间，是否明显短于第一次。",
    "如果答案是否定的，说明它还没有被结构化成可复用的形状。",
], 14, 6)))
PAGES.append(("15_section", section("07", "收束与评论：判断与下一步",
    "工具会继续换。值得留下的，是那套能被反复复用的判断结构。", 15, 7)))
PAGES.append(("16_ending", closing("判断先于工具。", "阿江 · 深度测评 · 2026.11",
    "© 2026 阿江 · 数据来自内测记录，结论仅代表个人判断", 16, 7)))

for name, text in PAGES:
    (OUT / f"{name}.svg").write_text(text, encoding="utf-8")
print("wrote", len(PAGES), "pages")
