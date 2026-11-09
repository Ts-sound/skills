---
name: on-demand-toolkit
description: |
  按需安装第三方常用工具指南。当用户需要安装或配置常用开发工具时触发。
  触发条件：安装工具、配置 MCP、设置浏览器自动化、UI/UX 设计工具、bb-browser、ui-ux-pro-max、playwright-mcp、superpowers、lark-cli、飞书、open-design、hyperframes、视频生成、ppt-master、oh-my-ppt、幻灯片、browser-use、浏览器自动化、archify、架构图、图表生成、lemo-opuscar、代码做片、风格化短片。
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
| 架构图 / 交互式图表生成 | archify |
| 代码做片 / 风格化短片 / 程序化影片 | lemo-opuscar |
