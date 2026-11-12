# 新增 Skills 更新评估报告

**评估日期**: 2026-11-12
**更新范围**: 4 个源仓库 pull 后新增 52 个 skill（anthropics-skills 17、mattpocock-skills 35）
**已装 skill 变更**: 8 个已同步（另见文末「源内消失的已装 skill」）

在「确认」列填 `✅` 后执行：

```bash
python scripts/import.py docs/reports/new-skills-2026-11-12.md
```

## anthropics-skills（17）

| ID | Skill | 描述 | 推荐度 | 分类 | 确认 |
|----|-------|------|--------|------|------|
| 1 | academy-guide | Claude Academy 课程/教程推荐，回答「怎么用 Claude」类问题 | 2 | learning | |
| 2 | algorithmic-art | p5.js 生成艺术（种子随机、参数交互） | 2 | productivity | |
| 3 | brand-guidelines | 套用 Anthropic 品牌色/字体到 artifact | 2 | productivity | |
| 4 | canvas-design | 用设计理念产出 PNG/PDF 视觉作品，含 83 个资源（5.5MB） | 3 | productivity | |
| 5 | claude-api | Claude API/SDK 全参考：模型、定价、流式、工具调用、MCP、缓存（96 文件，2.1MB） | 5 | engineering | |
| 6 | discernment-nudge | 回答后追加 2-3 个核查问题，防用户盲信 | 3 | productivity | |
| 7 | doc-coauthoring | 结构化文档协作编写流程 | 3 | productivity | |
| 8 | docx | Word 文档创建/读取/编辑/模板（61 文件） | 4 | productivity | |
| 9 | internal-comms | 内部沟通写作（状态报告/FAQ/Newsletter） | 2 | productivity | |
| 10 | mcp-builder | 构建高质量 MCP server（Python FastMCP / Node SDK） | 5 | engineering | |
| 11 | pdf | PDF 读取/合并/拆分/水印/表单/OCR | 4 | productivity | |
| 12 | pptx | PPTX/POTX 创建与编辑（56 文件） | 4 | productivity | |
| 13 | slack-gif-creator | 为 Slack 制作优化动画 GIF | 2 | productivity | |
| 14 | theme-factory | 10 套主题样式化文档/页面/幻灯片 | 3 | productivity | |
| 15 | web-artifacts-builder | React/Tailwind/shadcn 复杂 HTML artifact | 4 | engineering | |
| 16 | webapp-testing | Playwright 测试本地 Web 应用 | 4 | engineering | |
| 17 | xlsx | 电子表格创建/编辑/公式/清洗（53 文件） | 4 | productivity | |

## mattpocock-skills（35）

| ID | Skill | 描述 | 推荐度 | 分类 | 确认 |
|----|-------|------|--------|------|------|
| 18 | ask-matt | 路由：按场景推荐本仓 skill/流程 | 1 | productivity | |
| 19 | code-review | 从固定点起按「规范/正确性」两轴审查改动 | 4 | engineering | |
| 20 | codebase-design | 深模块设计词汇，改善模块接口 | 3 | engineering | |
| 21 | diagnosing-bugs | 难 bug/性能回归诊断循环（= 旧 diagnose 新版） | 4 | engineering |✅ |
| 22 | domain-modeling | 建立/打磨领域模型与 GLOSSARY | 3 | engineering | |
| 23 | implement | 按 spec/ticket 实现，薄封装 | 2 | engineering | |
| 24 | implement-spec | 落地 /to-spec + /to-tickets 的产物 | 3 | engineering | |
| 25 | improve-codebase-architecture | 扫描深模块机会，出 HTML 报告再逐个 grill | 3 | engineering | |
| 26 | pr | 写 PR 描述 | 3 | engineering | |
| 27 | prototype | 一次性原型验证设计问题 | 3 | engineering | |
| 28 | research | 查一手资料并把结论写成仓内 Markdown | 3 | engineering | |
| 29 | retro | 编码会话复盘 | 3 | engineering | |
| 30 | setup-matt-pocock-skills | 为本仓配置 issue tracker/label/领域文档（仓特定） | 1 | project-mgmt | |
| 31 | tdd | 红-绿-重构测试先行开发 | 4 | engineering | |
| 32 | to-spec | 把当前对话整理成 spec 并发到 issue tracker | 4 | project-mgmt | |
| 33 | to-tickets | 拆 tracer-bullet 票据，标注阻塞关系（= 旧 to-issues） | 4 | project-mgmt |✅ |
| 34 | wayfinder | 单会话装不下的大块工作拆成决策票据地图 | 3 | planning | |
| 35 | wizard | 生成交互式 bash 向导，引导人工完成步骤 | 2 | engineering | |
| 36 | chief-of-staff | 单会话内用 subagent 推进长期目标 | 3 | planning | |
| 37 | claude-handoff | 对话交接给后台新 agent（与已装 handoff 重叠） | 2 | productivity | |
| 38 | loop-me | grill 工作流 spec（仓内自用） | 1 | planning | |
| 39 | setup-ts-deep-modules | 用 dependency-cruiser 把 TS 包约束成深模块 | 2 | engineering | |
| 40 | software-factory | 设计 software factory 的共用语言 | 2 | planning | |
| 41 | writing-beats | 写作：把素材编成 beat 行程 | 2 | learning | |
| 42 | writing-fragments | 写作：先挖碎片，不立结构 | 2 | learning | |
| 43 | writing-shape | 写作：把素材逐段塑成文章 | 2 | learning | |
| 44 | git-guardrails-claude-code | Claude Code hooks 拦截危险 git 命令 | 2 | engineering | |
| 45 | migrate-to-shoehorn | 测试里的 `as` 断言迁到 shoehorn | 2 | engineering | |
| 46 | scaffold-exercises | 生成可过 lint 的练习目录（题/解/讲解） | 2 | learning | |
| 47 | setup-pre-commit | 配 Husky + lint-staged + 类型检查 + 测试 | 3 | engineering | |
| 48 | grilling | 无情追问计划/决策/想法（与已装 grill-me 重叠） | 3 | productivity | |
| 49 | teach | 在工作区内教学新技能/概念 | 3 | learning | |
| 50 | to-questionnaire | 把答不了的决策转成他人填写的问卷 | 3 | productivity | |
| 51 | wait-what | 上条消息没落地，要求重讲（566B 微技能） | 2 | productivity | |
| 52 | writing-for-agents | 写 agent 文档：SKILL.md / AGENTS.md / CLAUDE.md | 4 | core |✅ |

## 建议优先级

**优先引入（5 个，均为工程硬价值）**

- 5 claude-api、10 mcp-builder：高密度参考 + 脚本，日常直接用。
- 19 code-review、31 tdd、52 writing-for-agents：流程类，触发场景明确。

**值得引入（推荐度 4）**

- 8 docx、11 pdf、12 pptx、17 xlsx：能力完整，但与已装 `office` 系列重叠，二选一。
- 15 web-artifacts-builder、16 webapp-testing：前端构建/测试闭环。
- 21 diagnosing-bugs、32 to-spec、33 to-tickets：分别替代/升级已装 diagnose、to-issues。

**跳过（推荐度 1）**

- 18 ask-matt、30 setup-matt-pocock-skills、38 loop-me：绑定 mattpocock 仓库自身工作流，外部无收益。

## 风险与注意

- **体积**: canvas-design 5.5MB、claude-api 2.1MB、docx/pptx/xlsx 各约 1.1MB，共约 9MB；引入前确认仓库体积可接受。
- **重叠**: office 四件套与现有 `office` skill 重复；grilling/grill-me、claude-handoff/handoff、diagnosing-bugs/diagnose 是迭代版本，建议替换而非并存。
- **源内消失的已装 skill**: `diagnose`、`to-issues`、`caveman`、`write-a-skill` 在 mattpocock-skills 新版本中已无对应目录（仓库重组：diagnose→diagnosing-bugs、to-issues→to-tickets、caveman 移除）。`sync.py` 已跳过并在 CSV 保留旧记录，需人工决定：保留本地副本、改指新名、或标记 deprecated。
- **in-progress 分组**: 36–43 来自 `skills/in-progress/`，上游标为未完成，稳定度低。
