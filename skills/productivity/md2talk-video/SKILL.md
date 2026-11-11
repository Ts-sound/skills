---
name: md2talk-video
description: 把 Markdown 演讲大纲变成带配音和字幕的演讲视频：解析「大章节 / 子页 / 演讲稿」，逐页产出 Markdown 解析结果、wav + srt、HTML PPT、最终 MP4，四个审核闸门默认停在审核点，支持断点续跑和单页返工。当用户说「把 md 讲稿做成视频」「大纲转演讲视频」「给 PPT 配讲解音频」「md2talk」「生成带字幕的讲解片」时使用；只要输入是带 `##/###/>` 结构的讲稿 Markdown 且要出视频，就用这个 skill。
---

# md2talk-video

一份讲稿 Markdown 进来，一条带配音和字幕的演讲视频出去。中间四个阶段各有独立产物，默认停在审核点，确认后再走下一段。

## 整体流程

| 阶段 | 输入 | 动作 | 产物 | 闸门 | 谁做 |
|---|---|---|---|---|---|
| 0 转写 | 原始 md（教程、笔记、文章） | 改写成标准 PPT 讲稿：封面/目录/内容/收尾 + kind + 短要点，**流水线不创作** | `<ws>/input.md` | `deck_check.py` + 自检清单 | 人 / agent |
| 1 解析 | `input.md` | 按 `##` / `###` / `>` 切章节、页面、台词 | `out/1_md/{parsed.json,script.md,review.md}` | GATE 1：看切分、缺稿 | 脚本，人审 |
| 2 配音 | `parsed.json` | edge-tts 或 audiocpp 逐页合成 | `out/2_tts/pNNN.wav + pNNN.srt` | GATE 2：抽听、核字幕 | 脚本，人审 |
| 3 PPT | 页面 JSON 或 SVG | `builtin` 生成 HTML；`--ppt ppt-master --svg-dir` 包装外部 SVG | `out/3_htmlppt/pNNN.html + index.html` | GATE 3：浏览器看版式 | 脚本，人审 |

`ppt-master` 模式把 SVG 内联进 HTML（不引用 `file://`），整个 `3_htmlppt/` 可整体拷走；`index.html` 用文件名相对链接，不依赖工作目录。
| 4 成片 | HTML + wav + srt | 渲染、混流、拼接、可选烧字幕 | `out/4_video/final.mp4 + final.srt` | GATE 4：播放验收 | 脚本，人审 |

判定很简单：**`input.md` 不是讲稿，就回阶段 0，不要硬跑。** 原文档直接喂给阶段 1，普通段落会被当成大纲，示例引用会被当成台词。

## 工作目录

在**当前目录**下为每个视频建一个工作目录，不要直接跑在 skill 目录里：

```bash
python scripts/init_workspace.py talk-md-syntax --title "Markdown 语法速查"
```

脚本会创建 `talk-md-syntax/input.md` 模板并打印下一步命令；目录已存在但 `input.md` 不在时复用，`input.md` 已存在则拒绝覆盖（exit 2）。

```
<ws>/
├── input.md                  # 唯一输入，阶段 0 的产物
├── job.json                  # 状态、参数、审核决策、逐页产物
├── out/                      # 全部派生，可整体删除后重跑
│   ├── 1_md/{parsed.json, script.md, review.md}
│   ├── 2_tts/{pNNN.wav, pNNN.srt, manifest.json}
│   ├── 3_htmlppt/{pNNN.html, index.html}
│   └── 4_video/{pNNN.mp4, final.mp4, final.srt}
└── logs/run.log
```

`out/1_md` 是解析结果，不是第二个输入目录。多份 `input.md` 一定会漂移，只留根目录那一份。

## 阶段 0：原始 md → 标准 PPT 讲稿

pipeline 只解析，不把教程自动改写成演讲稿。标准 PPT 和文章不是一种东西：**一页一个观点，正文是短语，台词另写，代码是示例**。先按这个标准提炼，再交给阶段 1。

### 先定骨架

默认 18 页：封面 1 + 目录 1 + 内容 15 + 收尾 1；若每个内容章都加过渡页，常见为 23 页。总页数 10–24 之间可调，每章 2–4 页，目录列的是**章**，不是页。

内容章 ≥ 3 个、总页数 ≥ 15 时，建议**每个内容章插 1 个 `section` 过渡页**（24 页封顶，算好页数）。过渡页只放章名和一句过渡词，不放大纲；开场、目录、收尾之前不加。例：18 页 + 5 个内容章过渡 = 23 页。

页面类型写在 `###` 下一行，用 HTML 注释声明：

| kind | 用途 | 要点 |
|---|---|---|
| `cover` | 封面，必须是第一页 | 标题 + 一句副标题 |
| `agenda` | 目录，必须是第二页 | 4–8 条，列章 |
| `section` | 章节过渡页，可选 | 放在 `##` 章首、该章第一个内容页之前；**标题就是章名**（与 `##` 一致），过渡词放台词；标题 ≤ 16 字，台词 15–46 字，不放大纲 |
| `content` | 默认内容页 | 一个观点 + 2–5 条短要点 |
| `cards` | 并列卡片页，可选 | 每张一个短标题 + 一句解释 |
| `data` | 数据页，可选 | 数字 + 一句结论 |
| `closing` | 收尾，必须是最后一页 | 一句行动号召，≤ 3 条 |

骨架示例（中间页省略，过渡页放在章首）：

```markdown
# Markdown 语法速查

## 开场
### P01 Markdown 语法速查
<!-- kind: cover -->
> 大家好，今天用十分钟把 Markdown 的高频语法过一遍。
- 十分钟上手日常写作

## 目录
### P02 今天讲什么
<!-- kind: agenda -->
> 我们按写作顺序走：先文本，再结构，最后是链接和表格。
- 文本：标题、换行、强调
- 结构：引用、列表、代码、分隔线
- 扩展：链接、图片、表格、任务列表

## 文本语法
### P03 文本语法
<!-- kind: section -->
> 接下来三页，先把最常用的文字语法过一遍：标题、换行和强调。

### P04 井号越多，标题级别越低
<!-- kind: content -->
> 一个井号是一级标题，两个是二级，最多六级。写作时一般只用前三级。

- `#` 一级标题
- `##` 二级标题
- `###` 三级标题

## 收尾
### P18 现在就打开编辑器
<!-- kind: closing -->
> 别背语法，打开编辑器敲一遍，比看十遍都管用。
- 挑一段旧笔记，改成 Markdown
- 下次写作直接用
```

### 一页怎么写

```markdown
### P03 井号越多，标题级别越低
<!-- kind: content -->
> 一个井号是一级标题，两个是二级，最多六级。写作时一般只用前三级。

- `#` 一级标题
- `##` 二级标题
- `###` 三级标题
```

- **标题是结论**，不是名词；≤ 24 字，不写「P3」
- **过渡页**：`##` 章首、内容页之前，标题 ≤ 16 字，台词 15–46 字，不放大纲
- **正文 2–5 条**，每条 ≤ 26 字，关键词，不加句号；整句留给 `>`
- **台词 40–220 字**，一页只讲一件事，像跟人说话
- **代码**：行内用反引号；围栏代码块会成为该页的代码示例（每页取第一块，建议 ≤ 12 行），不参与切分和台词
- 第一页之前的围栏/`<!-- -->` 当草稿忽略；页面内的围栏原样上屏，别把 `###`、`>` 示例放进去

### 自检

```bash
python scripts/deck_check.py <ws>/input.md
```

检查封面/目录/收尾位置、过渡页规则（章首、无大纲、短台词）、页数、要点数量与长度、标题长度、台词长度、重复标题。**error 必须改，warning 要么改要么说明理由**；阶段 1 也会把同样的结果附在 GATE 1 摘要里。

原始笔记 → 讲稿的最小对照：

```markdown
## 二级标题
二级标题用两个井号。
```

```markdown
### P03 井号越多，标题级别越低
<!-- kind: content -->
> 二级标题用两个井号，一般用来分章。你可以把它理解成书的目录。

- `##` 二级标题
- 用来分章
```

转写完的检查清单：

- 封面、目录、收尾齐全，页数 10–24
- 内容章 ≥ 3 个时每章最多 1 个 `section` 过渡页，且都在篇首
- 每页一个观点，标题是结论
- 正文是 2–5 条短要点，不是段落
- 每页 `>` 台词 40–220 字，念 15–45 秒
- 代码示例放在页面内的围栏里，页面外的示例清掉
- `deck_check.py` 0 error，然后 `--review all --from 1` 看 GATE 1

## 逐步执行协议

每个阶段一条命令，跑到闸门就停，看完产物再决定继续：

| 步骤 | 命令 | 预期 | 用户动作 |
|---|---|---|---|
| 1 | `pipeline.py <ws> --review all --from 1` | 打印审核摘要，停在 GATE 1，exit 0，`stage1=paused` | 看切分、补缺稿，或放行 |
| 2 | `pipeline.py <ws> --review all --from 2` | 合成配音后停在 GATE 2 | 抽听 wav、核 srt |
| 3 | `pipeline.py <ws> --review all --from 3` | 生成 HTML 后停在 GATE 3 | 浏览器开 `index.html` |
| 4 | `pipeline.py <ws> --review all --from 4` | 出成片后停在 GATE 4 | 播放验收 |
| 收尾 | `pipeline.py <ws> --review none` | 跑完剩余阶段，不再停 | 交付 |

规则：

- 闸门默认停，非交互环境（agent、CI、stdin 不是 TTY）也停，避免没人看就花掉 TTS 配额
- 暂停时退出码 0，阶段状态记 `paused`，产物保留
- `--review` 会写进 `job.json`，之后重跑沿用；恢复逐步审核要显式传 `--review all`
- `--yes`（等价 `MD2TALK_AUTO=1`）才全自动，这是显式选择
- 只重做某阶段用 `--from N`；只重做某页加 `--only pNNN --force`
- 改产物文件后（HTML、SRT、单页音频）直接从对应阶段续跑

## 用法

```bash
python scripts/pipeline.py <workspace> [options]
```

| 参数 | 说明 | 默认 |
|---|---|---|
| `<workspace>` | 工作目录，必须含 `input.md` | 必填 |
| `--review` | `all` / `none` / `1,3` 或 `2b` | 新工作目录为 `all` |
| `--tts` | `edge-tts` / `audiocpp` | 配置默认 |
| `--ppt` | 阶段 3 provider：`builtin` / `ppt-master` | `builtin` |
| `--svg-dir` | ppt-master 模式的 SVG 页目录（相对路径按 workspace） | 配置 `ppt.svg_dir` |
| `--voice` | 音色或参考音频 | 配置默认 |
| `--rate` | 语速，如 `+10%` | `+0%` |
| `--from` | 从阶段 `1/2/3/4` 重跑 | 按 `job.json` 续跑 |
| `--only` | 只处理一页，如 `p003` | 全部 |
| `--force` | 忽略已有产物强制重跑 | 否 |
| `--config` | 自定义 yaml（相对路径先按 skill 找） | `config/default.yaml` |
| `--yes` | 所有闸门自动通过 | 否 |

## 输入格式

- `## ` 大章节，`### ` 子页（一页 = 一张 PPT = 一段音频/字幕）
- 连续 `>` 行是该页演讲稿，合并成一段；`[pause]` 保留在稿子里，进字幕前转成逗号
- 其余正文是该页大纲；**PPT 里一页只放 2–5 条**
- `<!-- kind: cover|agenda|section|content|cards|data|closing -->` 声明页面类型，默认 `content`；`<!-- layout: ... -->` 可透传给外部模板
- 页面内的围栏代码块进入 `page["code"]`，作为该页代码示例（每页第一块）；页面外/第一个 `###` 前的围栏忽略
- 缺演讲稿的页标 `speech_missing`，GATE 1 列出来；继续跑则用大纲拼一句兜底
- 有章节但没 `###` 时整章当一页，不丢内容
- HTML 注释（非 kind/layout）与页面外代码围栏整段跳过：示例里的 `###`、`>` 不会变成页面或台词

## 依赖与渲染

- Python 3.10+，脚本只用标准库
- `ffmpeg` / `ffprobe` 在 `PATH`（或在 `compose` 配置写绝对路径）
- TTS：`edge-tts`（原生字幕时间戳）或 `audiocpp`（本地参考音色，字幕按权重估时）
- PPT / 渲染默认用内置实现，不依赖外部 CLI：
  - `scripts/builtin_ppt.py` 生成 1280×720 HTML
  - `scripts/builtin_render.py` 无头 Edge/Chrome 截图，再用 ffmpeg 定格编码；输出默认 **1920×1080**（`render.width` / `render.height` 可改）。画布仍是 1280×720，SVG/HTML 随窗口等比放大。
- 阶段 3 也可用 `--ppt ppt-master --svg-dir <dir>`：`ppt-master` 是 agent 工作流、不是 CLI，先在它那边按模板生成/导出每页 SVG（如 `svg_output/`），流水线把 SVG 包成同尺寸 HTML，后续阶段不变。SVG 按文件名 `pNNN*.svg` 匹配，否则按排序序号对应；数量少于页数会报错，多出的会 warning 并忽略。

`ppt-master` 模式的典型串联：

```bash
python scripts/pipeline.py <ws> --from 3 --review all \
  --ppt ppt-master --svg-dir <ppt-master-project>/svg_output
python scripts/pipeline.py <ws> --from 4 --review all
```

### 用 ppt-master 出页面（手动）

pipeline **不会**调用 ppt-master，也不会代跑它的 Stage 1/2 确认门。流程是两边接力：

1. 本 skill 阶段 0 定稿 `input.md`，阶段 1 过 GATE 1。
2. 在对话里按 ppt-master 的流程跑：Stage 1 契约 → 模板安装 → Stage 2 方案 → 逐页 SVG，导出 `svg_output/`。
3. 命名建议与讲稿对齐：`p001-cover.svg`、`p003-section.svg`……；做不到就保证**顺序与页序一致**，pipeline 按排序对应。
4. 导出目录只放本次页面：每页一个 SVG，数量等于讲稿页数，画布 16:9（1280×720 或同比例）。
5. 回 pipeline 消费：

   ```bash
   python scripts/pipeline.py <ws> --from 3 --review all \
     --ppt ppt-master --svg-dir <project>/svg_output
   ```

6. GATE 3 看 `index.html`，GATE 4 照常出片。PPTX 不是必需产物。

页面文案与 `input.md` 必须同源；只改 SVG 不改讲稿，字幕和音频会对不上。改稿后重跑阶段 1/2，再重新导出 SVG。

找不到浏览器或起不来时，按顺序选：

```
builtin_render
├─ 找到 Edge/Chrome            → 直接截图
├─ 设了 MD2TALK_BROWSER        → 用指定浏览器
├─ 受限沙箱 / 无浏览器          → 换外部渲染器（hyperframes 等，改 render.cmd）
└─ 只测流程                    → faketools 假渲染（产物是纯色视频，不能交付）
```

实例：DSH 沙箱内 Edge 会报 `OpenProcess: 拒绝访问`，阶段 4 需要一次性 `danger-full-access`，或在沙箱外跑，或换外部渲染器。`ppt-master` 是 agent 工作流、`hyperframes` 需另装，二者都不是开箱即用的 PATH 命令。

### 外部命令与占位符

`config/default.yaml` 里所有外部命令都是模板：

```yaml
ppt:
  cmd: "{python} {skill}/scripts/builtin_ppt.py --in {page_json} --out {out_html} --theme {theme} --title {title}"

render:
  cmd: "{python} {skill}/scripts/builtin_render.py --html {html} --out {out_mp4} --duration {duration} --fps {fps} --ffmpeg {ffmpeg}"
```

| 段落 | 占位符 |
|---|---|
| `tts.edge_tts` | `{voice} {rate} {text_file} {out_wav} {raw_srt}` |
| `tts.audiocpp` | `{bin} {model} {ref_audio} {text_file} {out_wav}` |
| `ppt` | `{page_json} {out_html} {theme} {title} {python} {skill}` |
| `render` | `{html} {out_mp4} {duration} {fps} {python} {skill} {ffmpeg}` |

模板首 token 是 `{python}` / `{ffmpeg}` 这类占位符时跳过工具探测；裸名字按 PATH 找；相对路径先按 skill 目录、再按工作目录找。启动时会探测当前阶段要用的工具，缺了立即失败：

```
ERROR required tool not found: edge-tts
  install: pip install edge-tts   (or: uv tool install edge-tts)
  command template: ...
```

### 字幕策略

- edge-tts：原生 SRT，重编号、按页平移，合并成 `final.srt`
- audiocpp：无时间戳，按标点切句，按「中文按字 / 英文按词」权重分配 wav 时长；单句 0.6–8 秒，超长再切，过短合并

### 视频合成

```
无声 pNNN.mp4 + pNNN.wav --ffmpeg--> out/4_video/pNNN.mp4
p001.mp4 … pNNN.mp4 --concat demuxer--> final.mp4
final.srt 可选烧录（compose.burn_subtitles）
```

以 wav 实际时长为准裁切/补帧，避免音画错位。`--only` 只产出单页视频，不拼整片。

## 产物与断点续跑

`job.json` 是唯一事实源：

- 阶段 `done` 且产物存在 → 跳过
- 逐页指纹：台词变只重做该页音频；标题/要点/kind 变只重做该页 HTML；HTML 或渲染参数变才重做该页视频。改稿后直接重跑，不会拿错位旧件
- `--from N` → 从 N 起重跑，之前的不动
- `--only pNNN` → 只处理该页，其余复用；阶段状态记 `partial`
- `--force` → 覆盖已有产物（脚本改动或想彻底重来时用）
- 重新解析后，`job.json` 里已不存在的页记录会被清掉，旧页不会混进拼接
- 已生成文件可直接改，再从对应阶段续跑

## 验收清单

GATE 4 逐条过：

- 成片时长 ≈ 各页 wav 之和（偏差应小于 1 秒）
- 视频 h264、音频 aac，默认 **1920×1080**（`render.width` / `render.height` 可改；画布仍是 1280×720）
- 抽 3 帧看标题/要点没溢出、没乱码
- `final.srt` 是 UTF-8，首条从 0 附近开始，没有大面积空洞
- `job.json` 四个阶段都是 `done`

## 脚本职责

| 脚本 | 职责 |
|---|---|
| `scripts/init_workspace.py` | 建工作目录、写 `input.md` 模板，不覆盖已有稿 |
| `scripts/paths.py` | 路径自解析、配置加载、命令模板渲染、ffprobe 时长 |
| `scripts/md_parse.py` | 章节/子页/台词/kind/代码示例解析、`script.md`、`review.md`、缺稿兜底 |
| `scripts/deck_check.py` | 标准 PPT 讲稿检查：kind 顺序、过渡页规则、页数、要点/标题/台词长度，退出码 1 表示有 error |
| `scripts/srt.py` | 切句、估时、SRT 解析/平移/合并 |
| `scripts/tts.py` | edge-tts / audiocpp 分发，逐页合成 |
| `scripts/ppt.py` | 逐页调 PPT 命令，补 `index.html` 预览 |
| `scripts/builtin_ppt.py` | 内置 HTML 页生成器（默认） |
| `scripts/render.py` | 逐页调渲染命令出无声视频 |
| `scripts/builtin_render.py` | 内置截图 + 定格编码渲染器（默认） |
| `scripts/compose.py` | 混流、拼接、可选烧字幕 |
| `scripts/review.py` | 闸门模式解析与停/过判定 |
| `scripts/pipeline.py` | 参数解析、状态机、阶段编排、逐页指纹缓存 |

开发改动后跑回归：`python -m unittest discover -s tests -v`（9 项，覆盖解析、deck_check、指纹、HTML 内联与 index 链接）。

## 失败处理

- 缺工具：exit 2，按提示安装后重跑同一命令
- TTS / 渲染命令失败：exit 1，打印命令和 stderr 尾部，已完成页复用
- 缺演讲稿：GATE 1 列页号，补 `>` 后 `--from 1`
- 闸门暂停：exit 0，状态 `paused`，`--review none` 或 `--yes` 继续
- 中途停止：阶段记 `paused`，产物保留

## Windows 控制台

脚本启动时把 stdout/stderr 切到 UTF-8。外层仍是旧代码页时先设：

```powershell
$env:PYTHONIOENCODING='utf-8'
[Console]::OutputEncoding=[Text.Encoding]::UTF8
```

`edge-tts.exe` 常装在 `%LOCALAPPDATA%\Programs\Python\Python3xx\Scripts`，该目录不在 PATH 时把整个 Scripts 目录前置：

```powershell
$env:PATH="$env:LOCALAPPDATA\Programs\Python\Python314\Scripts;$env:PATH"
```

## 最小示例

```bash
python scripts/init_workspace.py talk-demo --title "最小示例"
# 编辑 talk-demo/input.md，或复制 demo/input.md 覆盖它
python scripts/pipeline.py talk-demo --review all --from 1
```
