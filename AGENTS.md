# AGENTS.md

## Skills 仓库使用指引

### 目录结构

```
/
├── skills/           # opencode 扫描目录（6 个分类）
│   ├── core/
│   ├── engineering/
│   ├── planning/
│   ├── productivity/
│   ├── project-mgmt/
│   └── learning/
├── sources/          # 第三方 git submodule 缓存
├── data/             # CSV 元数据（脚本维护，不手动编辑）
├── scripts/          # 自动化脚本
└── docs/
    ├── design/       # 设计文档
    ├── requirements.md
    ├── decisions.md
    └── reports/      # 调研报告
```

## 安装

```bash
git clone <this-repo> ~/skills-repo
cd ~/skills-repo

# 链接到 Claude Code（含 skills + 启动自动激活 caveman）
bash scripts/link-skills.sh --claude
python3 scripts/add-caveman-hook.py --claude

# 或链接到 opencode（仅 skills，不含 caveman）
bash scripts/link-skills.sh --opencode
```

整个 `skills/` 目录作为一个 namespace 链接到目标路径下的 `ts-sound-skills/`。
使用 symlink 方式，skills 更新后自动同步，无需重新安装。
`git pull` 后无需重新运行脚本。

## 工作流

### 引入第三方 Skills

```
1. 添加源 → python3 scripts/add_source.py <git-url>
2. 查看报告 → docs/reports/<repo-name>.md
3. 标记确认 → 在报告的「确认」列填入 ✅
4. 执行引入 → python3 scripts/import.py docs/reports/<repo-name>.md
```

**关键规则：**
- 必须通过脚本操作，不手动修改 `data/` 下的 CSV
- 报告中的「确认」列是用户参与点，必须等待用户标记后再执行引入
- 源仓库以 `owner-repo` 格式命名，避免冲突

### 更新 Skills

```
1. 检查更新 → python3 scripts/update.py
2. 查看差异 → python3 scripts/diff.py
3. 同步变更 → python3 scripts/sync.py
```

### 维护查询

```
python3 scripts/maintain_csv.py list-skills
python3 scripts/maintain_csv.py list-sources
python3 scripts/maintain_csv.py remove-skill <name>
```

## 最佳实践

### 脚本优先

- **所有操作通过脚本执行**：不手动编辑 CSV、不手动复制 skills
- **用户确认不可跳过**：必须展示报告清单，等待用户标记 ✅ 后才能引入
- **CSV 是唯一元数据源**：不维护单独的 catalog.md

### Skill 命名与分类

- 使用短名：`auth/` 而非 `authentication/`
- 小写 + 短横线：`web-artifacts-builder/`
- 分类标准：
  - **core** — 基础工具（skill-creator, mermaid-diagram）
  - **engineering** — 编码/测试/调试（claude-api, mcp-builder）
  - **planning** — 需求分析/方案设计
  - **productivity** — 效率提升（docx, pdf, xlsx）
  - **project-mgmt** — 项目流程管理
  - **learning** — 知识沉淀

### 报告规范

- 描述使用中文
- 包含推荐度（1-5）
- 包含确认列，供用户标记
- 源仓库 URL 使用 `https://github.com/...` 格式

### Git 管理

- sources/ 使用 git submodule，保留完整历史
- .gitmodules 不手动编辑
- sources/ 内容不手动修改
