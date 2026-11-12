---
name: on-demand-toolkit
description: |
  按需安装第三方常用工具指南。当用户需要安装或配置常用开发工具时触发。
  触发条件：安装工具、配置 MCP、设置浏览器自动化、UI/UX 设计工具、bb-browser、ui-ux-pro-max、playwright-mcp、code-review-graph、代码图谱、代码审查、superpowers、lark-cli、飞书、open-design、impeccable、前端设计、AI slop、hyperframes、视频生成、ppt-master、oh-my-ppt、幻灯片、browser-use、浏览器自动化、archify、diagram-design、架构图、图表生成、book-to-skill、书转 skill、PDF 转 skill、读书、hallmark、反 AI 味、text-to-cad、CAD、3D 建模、STEP、URDF、i-have-adhd、ADHD、输出格式、精简输出、lemo-opuscar、代码做片、风格化短片。
---

# 按需工具集

本 skill 提供常用第三方工具的安装指南和源链接。根据用户需求推荐合适的工具，引导用户阅读上游 README 获取最新安装和使用方法。

## 工具清单

### superpowers

**源仓库**: <https://github.com/Ts-sound/superpowers>
**本地路径**: `/opt/tong/ws/git-repo/superpowers`
**使用说明**: 见 [README.md](https://github.com/Ts-sound/superpowers/blob/main/README.md)

> **优先使用本地路径**：superpowers 已安装在 `/opt/tong/ws/git-repo/superpowers`，直接使用本地路径，无需重复克隆。

opencode/Claude Code 技能集合，包含 brainstorming、project-workflow、systematic-debugging 等 22 个 skills。
如需更新，请拉取上游最新代码到本地路径。

---

### bb-browser

**源仓库**: <https://github.com/epiral/bb-browser>
**使用说明**: 见 [README.md](https://github.com/epiral/bb-browser/blob/main/README.md)

你的浏览器就是 API。AI agent 可以直接控制 Chrome，使用你当前的登录状态访问任何网站。无需 API key、无需爬虫、无需 bot。支持 36 个平台、103 条命令。

---

### ui-ux-pro-max

**源仓库**: <https://github.com/nextlevelbuilder/ui-ux-pro-max-skill>
**使用说明**: 见 [README.md](https://github.com/nextlevelbuilder/ui-ux-pro-max-skill/blob/main/README.md)

AI 设计智能工具。提供 67 种 UI 风格、161 种配色方案、57 种字体搭配、161 条行业推理规则，可为任何项目生成完整的设计系统。

---

### playwright-mcp

**源仓库**: <https://github.com/microsoft/playwright-mcp>
**使用说明**: 见 [README.md](https://github.com/microsoft/playwright-mcp/blob/main/README.md)

Playwright MCP 服务器。通过结构化无障碍树（而非截图）让 LLM 与网页交互，支持浏览器自动化、自动化测试、页面分析。

---

### code-review-graph

**源仓库**: <https://github.com/tirth8205/code-review-graph>
**官网/文档**: <https://code-review-graph.com>
**使用说明**: 见 [USAGE.md](https://github.com/tirth8205/code-review-graph/blob/main/docs/USAGE.md)

给 AI 编码工具装一个**本地代码知识图谱**，解决「改一个函数，agent 却把半个仓库读一遍」的 token 浪费。

- **建图**：用 Tree-sitter 把仓库解析成节点（函数、类、import）与边（调用、继承、测试覆盖），存进本地 SQLite `.code-review-graph/`，不上传代码。
- **查图**：改一个文件后做**爆炸半径分析**（blast radius），顺着调用/引用边找出真正受影响的文件与测试，只把这些上下文喂给 agent。
- **省 token**：6 个开源仓库实测每问题中位数约 63× 减少（最高 358×，fastapi），图谱回答稳定在 2–4k token。
- **增量更新**：编辑器 hook、git hook（pre-commit/post-checkout/post-merge）、watch 模式触发；只重解析 SHA-256 变了的文件（3000 文件仓库两文件改动约 2.5s）。
- **接入方式**：MCP server + CLI，一条 `install` 自动探测并配置 14+ 个客户端（Claude Code、Cursor、Codex、Copilot、OpenCode、Gemini CLI 及 `dsh` 等）。
- **CI 可选**：GitHub Action 在 PR 上贴一条风险评分评论（高风险函数、受影响执行流、测试缺口），可 `fail-on-risk` 做合并门禁。

```bash
pip install code-review-graph      # 需 Python 3.10+
code-review-graph install          # 探测已装 AI 工具，写入 MCP 配置；--dry-run 只看 diff
code-review-graph install --platform dsh   # 只配 DeepSeek Harness
code-review-graph build            # 首次建图（3000 文件约 40s）
```

装完重启编辑器，然后直接对 agent 说「Build the code review graph for this project」。卸载用 `uninstall`（`--dry-run` 可预览，`--keep-data` 保留图谱）。

注意：省的是**检索**成本——图谱先告诉你该读哪几个文件，agent 再打开这些文件时仍要付正常读取成本；小仓库收益有限，大仓库才明显。

---

### lark-cli

**源仓库**: <https://github.com/larksuite/cli>
**使用说明**: 见 [README.md](https://github.com/larksuite/cli/blob/main/README.md)

飞书/Lark 官方 CLI 工具。200+ 命令、24 个 AI Agent Skills，覆盖日历、即时通讯、文档、多维表格、电子表格、幻灯片、邮件、任务等 17 种业务领域。

---

### open-design

**源仓库**: <https://github.com/nexu-io/open-design>
**使用说明**: 见 [README.md](https://github.com/nexu-io/open-design/blob/main/README.md)

开源的 Claude Design 替代方案。本地优先、可部署到 Vercel，31 个可组合 Skills + 72 个品牌级设计系统，支持生成 web/desktop/mobile 原型、幻灯片、图片、视频。

---

### hyperframes

**源仓库**: <https://github.com/heygen-com/hyperframes>
**使用说明**: 见 [README.md](https://github.com/heygen-com/hyperframes/blob/main/README.md)

写 HTML 即可生成视频。为 AI Agent 原生设计的开源视频渲染框架，支持 GSAP、Lottie、CSS、Three.js 等动画运行时，可导出 MP4。

---

### ppt-master

**源仓库**: <https://github.com/hugohe3/ppt-master>
**使用说明**: 见 [README.md](https://github.com/hugohe3/ppt-master/blob/main/README.md)

从任何文档（PDF/DOCX/URL/Markdown）生成原生可编辑 PPTX。真实的 PowerPoint 形状、文本框和图表，非图片导出。支持模板复制、动画、语音旁白。

---

### oh-my-ppt

**源仓库**: <https://github.com/arcsin1/oh-my-ppt>
**使用说明**: 见 [README.md](https://github.com/arcsin1/oh-my-ppt/blob/main/README.md)

本地优先的 AI 幻灯片生成器和编辑器。输出纯 HTML 幻灯片，支持即时浏览器预览、可视化编辑、动画、多格式导出（PDF/PNG/PPTX）。

---

### browser-use

**源仓库**: <https://github.com/browser-use/browser-use>
**使用说明**: 见 [README.md](https://github.com/browser-use/browser-use/blob/main/README.md)

让网站对 AI Agent 可访问。Python 浏览器自动化框架，支持 LLM 驱动的网页交互、表单填写、数据抓取。提供开源 agent 和云端 stealth 浏览器。

---

### diagram-design

**源仓库**: <https://github.com/cathrynlavery/diagram-design>
**使用说明**: 见 [README.md](https://github.com/cathrynlavery/diagram-design/blob/main/README.md)

让 agent 画「编辑级」示意图的 skill：先判断该用哪种图型（架构、流程、时序、关系、数据、变更前后等），再直接产出**单个自包含的 HTML + SVG 文件**（内联 SVG、品牌 token、可访问性元数据、编辑排版风格），不依赖 Mermaid 渲染、无阴影。

- **45 种图型/图表类型**，覆盖架构图、流程图、时序图、状态机、ERD、组织树、对比、瀑布、时间线等
- **可导入现成图**：`.drawio`、Mermaid、Excalidraw 文件转成同风格 HTML/SVG
- **自带质检**：输出前检查几何对齐、间距、连线走向、复杂度，避免线穿框、图太挤
- **品牌化**：按项目已有颜色/字体生成，不是模板套壳

不适用：一行 Unicode 字符图、纯列表、单形状示意、只比属性的表格式内容。

安装（skills CLI，任意目录执行，按提示选目标 agent）：

```bash
npx skills add cathrynlavery/diagram-design
```

装完重开会话生效。注意：该 skill 含 6 个脚本，第三方审计 3 项中 2 项通过（Snyk 有告警），装前建议先读一遍脚本再运行。

---

### archify

**源仓库**: <https://github.com/tt-a1i/archify>
**使用说明**: 见 [README.md](https://github.com/tt-a1i/archify/blob/main/README.md)

把一句描述、一个问题或一整个仓库变成可交互的 HTML 图表。10 种图型：架构、工作流、时序、数据流、生命周期、ERD、类图、树、时间线、瀑布。产物是单个自包含 HTML，可导出 PNG / 视频 / 分享卡片，也能当一页式讲解页（先结论、后问答面板）。

安装（把 `<agent>` 换成 cursor / codex / claude-code / opencode）：

```bash
npx -y skills@latest add https://archify.si --skill archify --agent <agent> --global --copy --yes
```

DeepSeek Harness 也可走插件：`dsh plugin --profile web add @tt-a1i/archify-dsh@1.1.0`。

---

### impeccable

**源仓库**: <https://github.com/pbakaus/impeccable>
**官网/文档**: <https://impeccable.style>
**使用说明**: 见 [README.md](https://github.com/pbakaus/impeccable/blob/main/README.md)

给编码 agent 装一套「前端设计能力」，让 agent 写页面时不再产出千篇一律的 AI 风格界面。它本身不生成设计图、不托管设计稿，而是往 agent 的上下文里塞三样东西：

1. **设计上下文文件**：`PRODUCT.md`（写给谁用、要达成什么）和 `DESIGN.md`（现有配色、字体、圆角、间距、组件规则）。agent 动手前先读它们，新页面因此沿用项目已有视觉体系。
2. **26 个设计命令**：`/impeccable polish`（收尾打磨）、`bolder` / `quieter`（加强或弱化）、`typeset`（排版层级）、`distill`（去 clutter）、`critique` / `audit`（挑毛病）、`generate`（同元素出多个变体供挑选）、`live`（对着本地页面点选元素改）。用自然语言描述目标也行，不必记命令。
3. **确定性 detector**：62 条纯代码规则（无需 AI 模型、无需 API key），查对比度不足、文字溢出、AI 味套路（渐变文字、米色底、斜体衬线标题、侧边标签、脉冲小点、嵌套卡片等）以及与 `DESIGN.md` 的漂移。agent 每次改完 UI，hook 自动跑 detector 并把问题回灌给它修；也可手动跑。

一句话：**给 agent 补设计品味 + 用规则兜底防翻车**，产物仍是项目里的原生 HTML/CSS/组件代码。

安装（在项目目录内执行，按提示选 agent）：

```bash
npx impeccable install
```

之后在 agent 里跑 `/impeccable init` 建立 `PRODUCT.md` / `DESIGN.md` 上下文，再 `/impeccable hooks on` 开启自动检查（Codex 需在 `/hooks` 里信任 `PostToolUse` 与 `Stop`）；更新用 `npx impeccable update`。GitHub Copilot app 已内置，在 **Settings → Experimental** 启用。

手动扫描（不经过 AI，可直接进 CI）：

```bash
npx impeccable detect src/                      # 扫源码
npx impeccable detect http://localhost:3000     # 扫渲染后的页面
npx impeccable detect --json src/               # 机器可读，退出码 2 = 有问题
```

---

### hallmark

反 AI 味的前端设计 skill，Claude Code / Cursor / Codex 通用。解决的问题很具体：模型默认只会把同一套模板换配色。hallmark 用「页型（macrostructure）× 主题库」强行拉开结构差异，再靠 58 条 slop-test 闸门在出码前拦下 AI 常见毛病。

**源仓库**: <https://github.com/Nutlope/hallmark>（MIT，~53.5k stars，官网 <https://www.usehallmark.com/>）

**使用说明**

```bash
# 自动装（skills CLI）
npx skills add nutlope/hallmark

# 手动：Claude Code → ~/.claude/skills/hallmark/
#      Codex       → ~/.codex/skills/hallmark/
#      Cursor      → 把 SKILL.md 正文（去掉 frontmatter）存成 .cursor/rules/hallmark.mdc
```

装完直接说需求即默认 build 模式，另有三个动词：

| 动词 | 作用 | 是否改你的代码 |
|------|------|----------------|
| 默认（build） | 选页型 + 主题，跑完 slop test 出页面 | 是，新写 |
| `hallmark audit <目标>` | 按反模式打分，出改进清单 | 否 |
| `hallmark redesign <目标>` | 保留文案、IA、品牌，换掉整页结构 | 是，重写结构 |
| `hallmark study <截图或URL>` | 提取参考设计的 DNA（字体搭配、色锚点、结构）成 `design.md` | 否，只产出说明 |

设计系统底座：OKLCH 色彩空间、4pt 间距刻度、21 种页型、20+ 主题。产出物带 CSS fingerprint 标记，能看出这页是哪个主题生成的。

注意：

- 定位是「防同质化」，不是「替你审美」。brief 太糊它也只能挑个主题硬套，需求写清楚才有好结果。
- `study` 明确拒绝像素级复刻付费模板，只抽 DNA。
- 装了它跟 impeccable 不冲突：hallmark 管「怎么生成」，impeccable 管「生成后怎么挑错」。

---

### book-to-skill

把技术书（PDF / EPUB / DOCX / HTML / MD / RTF / MOBI）编译成一个 agent skill：核心 `SKILL.md` 约 4k token 存框架与主题索引，章节细节拆到 `chapters/` 按需读取。不是 RAG 式向量检索，是「编译期」提炼——把作者的框架、原则、套路固化成结构化知识库，用起来像随身带着这本书的作者。

**源仓库**: <https://github.com/virgiliojr94/book-to-skill>（MIT，~37.6k stars）

**使用说明**

1. 装成 agent skill（推荐，才有 `/book-to-skill` 命令）：

```bash
# Claude Code
git clone https://github.com/virgiliojr94/book-to-skill.git ~/.claude/skills/book-to-skill
# GitHub Copilot CLI
git clone https://github.com/virgiliojr94/book-to-skill.git ~/.copilot/skills/book-to-skill
# Amp / 跨 agent
git clone https://github.com/virgiliojr94/book-to-skill.git ~/.agents/skills/book-to-skill
```

2. 只用抽取引擎（脚本化预处理）时走 pip：`pip install "book-to-skill[all]"`，`book-to-skill --check` 查当前环境支持哪些格式。技术书表格/公式多，需 `book-to-skill[technical]`（底层 Docling）；纯文字书用 `pdftotext` 更快。MOBI/AZW 依赖 Calibre 的 `ebook-convert`。

3. 生成：`/book-to-skill <文件/目录/glob> [slug]`，会先问 技术书 还是 文字书。四种模式：

| 模式 | 触发说法 | 行为 |
|------|----------|------|
| 全量转换 | 默认 | 跑完 0–9 步，直接出全部文件 |
| 只分析 | "analyze"、"先看框架" | 只跑 0–3 步，出框架报告，不写文件 |
| 从分析生成 | "用现成分析生成" | 跳过抽取，直接用笔记生成 |
| 更新 / 合并 | 给新文件 + 已有 slug | 增量并进旧 skill，索引与术语表同步 |

4. 用生成的 skill：`/my-book` 载入核心；`/my-book 复制` 用主题索引定位到 `chapters/ch05-*.md`；`/my-book ch05` 直读章节。另有 `glossary.md`、`patterns.md`、`cheatsheet.md`。

产出目录示例：`SKILL.md` + `chapters/chNN-*.md` + `glossary.md` + `patterns.md` + `cheatsheet.md`。

注意：

- 需要 Claude Code / Amp / Copilot CLI 之一，生成过程走宿主模型，长书（20 万 token 级）耗时与花费都不低。
- 相比把整本书塞进 context，官方称省 24×–51× token；相比 RAG，优势是保留作者原话精度与结构，劣势是书更新后要重跑 fold-in。
- 版权自负：只处理你有权使用的书。

---

### i-have-adhd

**源仓库**: <https://github.com/ayghri/i-have-adhd>
**安装说明**: 见 [INSTALL.md](https://github.com/ayghri/i-have-adhd/blob/main/INSTALL.md)

改 agent 的**回复格式**，不改代码能力。让 agent 把答案放最前面、话说短、别铺垫，专治「答案埋在第三段」「寒暄半天不给命令」。不需要 ADHD 诊断，任何人嫌回复啰嗦都能用。

十条输出规则（`skills/i-have-adhd/SKILL.md`）：

1. **先给动作**：第一行就是命令 / 文件路径 / 代码，解释放后面
2. **多步骤编号**：每步只做一件事，禁止「然后…再然后…」
3. **结尾只给一个下一步**：2 分钟内能做完的那种
4. **支线问题先压住**：主线做完再单独问，不塞进当前修复
5. **每轮重申进度**：如「第 3/5 步完成」，照顾工作记忆
6. **给具体时间**：写「约 5 分钟」，不写「很快」
7. **完成项直接说**：写「登录已可用」，不写「做了若干改进」
8. **报错不带情绪**：去掉 "Unfortunately"，直接给原因 + 修法
9. **列表不超过 5 条**：超了拆「现在做 / 以后做」
10. **零废话**：禁 "Great question"、"Sure!"、"Hope this helps"，答完即止

会话内触发后一直生效，说「stop adhd mode」或「normal mode」关掉。三种装法：

```bash
# Claude Code（插件市场，推荐）
claude plugin marketplace add ayghri/i-have-adhd
claude plugin install i-have-adhd@i-have-adhd

# Codex
codex plugin marketplace add ayghri/i-have-adhd --ref main

# Cursor / 通用 skills CLI
npx skills add ayghri/i-have-adhd -a cursor
```

Claude Code 内输入 `/i-have-adhd` 激活；Codex 用 `$i-have-adhd`。想全局常开，把对应规则写进 `~/.claude/CLAUDE.md`。纯 markdown + 插件清单，无后台进程无 hook，想调风格直接改 `SKILL.md`。

---

### text-to-cad

用代码做实体产品：把 CAD 当代码写。agent 改 Python 脚本（`build123d` 建几何、`ezdxf` 画 2D），跑 CLI 生成 STEP / STL / 3MF / DXF / GLB、机器人描述 URDF / SDF / SRDF，再用自带 3D 预览器看结果，形成「描述 → 改码 → 重生成 → 目视检查」的闭环。

**源仓库**: <https://github.com/earthtojake/text-to-cad>（MIT，~26.1k stars，官网 <https://www.texttocad.dev>）

**使用说明**

```bash
git clone https://github.com/earthtojake/text-to-cad
cd text-to-cad

# Python 3.12+：几何内核
python3.12 -m venv .venv
./.venv/bin/python -m pip install -r requirements-dev.txt

# 预览器（React + Vite）
cd viewer && npm install && npm run dev   # 默认 4178
```

装完直接在 Claude Code / Cursor / Codex 里说需求，模型会写 `models/*.step.py` 并调 `gen_step_part` 之类工具生成产物。环境变量 `CAD_DIR` 指定模型根目录，`VIEWER_PORT` 改端口。

自带工具链：

| 能力 | 工具 | 输出 |
|------|------|------|
| 零件 / 装配 | `gen_step_part`、`gen_step_assembly` | STEP、GLB、topology.json |
| 2D 下料图 | `gen_dxf` | DXF + 预览 |
| 机器人描述 | URDF / SDF / SRDF skill | `.urdf` / `.sdf` / `.srdf`（含 MoveIt2 规划组） |
| 标准件 | step.parts 目录 + `download_step_part` | 螺丝、轴承等现成 STEP |
| 可制造性预检 | SendCutSend skill | 预检报告 |
| 3D 打印 | G-code / Bambu Labs skill | G-code，局域网直接下发打印机 |

注意：

- 双环境：Python 管几何，Node 管预览，两个都得装。OpenCascade 走 `OCP`，Windows 上安装偶尔要折腾 wheel。
- 产物是 `models/` 下的隐藏目录 `.part.step/`，大文件走 Git LFS，别让 agent 全仓扫二进制。
- 几何精度靠人验：预览好看不代表能加工，出图前自己过一遍尺寸链。

---

### lemo-opuscar

**源仓库**: <https://github.com/lemomo-ai/lemo-opuscar>
**使用说明**: 见 [README.md](https://github.com/lemomo-ai/lemo-opuscar/blob/main/README.md) 与[中文版](https://github.com/lemomo-ai/lemo-opuscar/blob/main/README.zh-CN.md)

用代码做片（程序化影片）。66 种现成电影风格（字幕新闻、延时交响、卫星简报、数据实物化、油画厚涂、中国水墨、浮世绘、Risograph、蓝图、瑞士动态排版、16-bit 像素 RPG、积木玩具、移轴微缩…），给定主题后由 agent 写 canvas/WebGL 的 `render(t)` 页面，配原创配乐、TTS 旁白、音效、混音，产出 30–60 秒 MP4 加海报与字幕。不生成视频、不用素材库。

安装（Claude Code 插件市场）：

```bash
claude plugin marketplace add lemomo-ai/lemo-opuscar
claude plugin install lemo-opuscar@lemolab
```

其他客户端：把仓库 `plugin/skills/lemo-opuscar/` 复制到自己的 skills 目录；或直接 `git clone` 后在仓库里开 agent。

前置：Node 20+、ffmpeg 7+、Python 3.11+（或 uv）。首次使用会下载指南、工具与风格提示词到 `~/lemo-opuscar`；自制风格存 `~/lemo-my-styles/<name>/`，更新/卸载不影响。影格默认 1920×1080、24 fps。注意：风格为 Claude Opus 5.5 调校，其他模型复现效果可能打折；一次成片约 30–60 分钟。

---

## 工具选择

| 场景 | 推荐工具 |
|------|----------|
| 工作流程管理、代码审查、调试 | superpowers |
| 飞书/Lark 办公自动化 | lark-cli |
| AI 设计助手（替代 Claude Design） | open-design |
| 视频生成（HTML 转 MP4） | hyperframes |
| 原生可编辑 PPTX 生成 | ppt-master |
| HTML 幻灯片制作 | oh-my-ppt |
| LLM 驱动浏览器自动化 | browser-use |
| 访问已登录网站（CLI） | bb-browser |
| UI/UX 设计建议 | ui-ux-pro-max |
| 浏览器自动化测试（MCP） | playwright-mcp |
| 代码知识图谱 / 省 context 的 code review | code-review-graph |
| 架构图 / 交互式图表生成 | archify |
| 品牌化示意图 / 45 种图型 / 导入 drawio、Mermaid | diagram-design |
| 前端 UI 设计 / 去 AI 味 | impeccable |
| 落地页结构差异化 / slop-test 58 闸门 / 设计 DNA 提取 | hallmark |
| 精简输出 / ADHD 友好回复 / 去铺垫 | i-have-adhd |
| 技术书转 agent skill / 边做边查书 | book-to-skill |
| 实体产品建模 / STEP、STL、DXF / 机器人 URDF | text-to-cad |
| 代码做片 / 风格化短片 / 程序化影片 | lemo-opuscar |
