---
name: on-demand-toolkit
description: |
  按需安装第三方常用工具指南。当用户需要安装或配置常用开发工具时触发。
  触发条件：安装工具、配置 MCP、设置浏览器自动化、UI/UX 设计工具、bb-browser、ui-ux-pro-max、playwright-mcp、superpowers。
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

## 工具选择

| 场景 | 推荐工具 |
|------|----------|
| 工作流程管理、代码审查、调试 | superpowers |
| 访问已登录网站 | bb-browser |
| UI/UX 设计建议 | ui-ux-pro-max |
| 浏览器自动化测试 | playwright-mcp |
