# AGENTS.md

## Skills 仓库使用指引

本仓库用「源仓库 submodule + 分类目录 + CSV 元数据 + 脚本」管理第三方 skills。所有变更走脚本，人工只做评审与确认。

### 目录结构

```
/
├── skills/           # 客户端扫描目录（6 个分类，当前 4 个分类在用）
│   ├── core/
│   ├── engineering/
│   ├── planning/     # 空
│   ├── productivity/
│   ├── project-mgmt/
│   └── learning/     # 空
├── sources/          # 第三方 git submodule 缓存（只读，不手动修改）
├── data/
│   ├── sub-repo.csv  # 源仓库清单：repo_name, repo_url, branch, last_commit, added_date, status
│   └── 3rd-skills.csv# 已引入 skill：skill_name, category, source_repo, source_path, imported_date, modified, last_sync, priority
├── scripts/
│   ├── lib/          # 公共函数（git、CSV、复制）
│   ├── add_source.py
│   ├── analyze.py
│   ├── import.py
│   ├── update.py
│   ├── diff.py
│   ├── sync.py
│   ├── maintain_csv.py
│   ├── install-claude.sh / install-opencode.sh
│   └── add-caveman-hook.py
└── docs/
    ├── design/       # 设计文档
    ├── requirements.md
    ├── decisions.md  # 架构决策（ADR）
    ├── others.md
    └── reports/      # 调研/评估报告（确认入口）
```

## 安装

```bash
git clone <this-repo> ~/skills-repo
cd ~/skills-repo

# 关键：初始化源仓库 submodule，否则 sources/ 是空目录
git submodule update --init --recursive

# 链接到 Claude Code（含 skills + 启动自动激活 caveman）
bash scripts/install-claude.sh
python3 scripts/add-caveman-hook.py --claude
```

使用 symlink 方式，skills 更新后自动同步，无需重新安装。

Windows 下用目录联接（junction）代替软链接，无需管理员：

```powershell
git clone <this-repo> "$env:USERPROFILE\skills-repo"
cd "$env:USERPROFILE\skills-repo"
git submodule update --init --recursive

New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\skills-tong" "$env:USERPROFILE\skills-repo"
```

更新只需 `git pull`，联接自动跟随；源仓库内容用 `scripts/update.py` 拉取。目标路径按客户端约定调整，如 `C:\Users\17853\.agents\skills\skills-tong`。

## 工作流

### 引入第三方 Skills

```
1. 添加源  → python3 scripts/add_source.py <git-url> [branch]
             自动克隆为 sources/<owner-repo> 并运行 analyze.py
2. 评审报告 → docs/reports/<owner-repo>.md
3. 标记确认 → 在报告表格「确认」列填入 ✅
4. 执行引入 → python3 scripts/import.py docs/reports/<owner-repo>.md
```

**关键规则：**

- 必须通过脚本操作，不手动修改 `data/` 下的 CSV
- 报告中的「确认」列是用户参与点，必须等待用户标记后再执行引入
- 源仓库以 `owner-repo` 格式命名（如 `anthropics-skills`），避免不同仓库同名冲突
- `import.py` 只认带 ✅ 的表格行；未标记的不会引入
- `source_repo` / `source_path` 由脚本在 `sources/` 中自动定位并写入 CSV，报告文件名不参与定位

### 更新 Skills

```
1. 检查更新 → python3 scripts/update.py
2. 查看差异 → python3 scripts/diff.py
3. 同步变更 → python3 scripts/sync.py
```

- `update.py`：`fetch` 源仓库分支，内容有变化时 `checkout` 到 `origin/<branch>` 并更新 `sub-repo.csv` 的 `last_commit`。源未初始化时打印 `Not initialized: ...` 并跳过（返回码 1）。
- `diff.py`：按 CSV 的 `source_path` 比较源与 `skills/`，列出新增/修改/删除。
- `sync.py`：按 CSV 的 `source_path` 复制到 `skills/<category>/`，同步成功后写回 `last_sync`。
  - 源仓库中已不存在该路径时只警告并跳过（如 `caveman`，源已删、本地保留副本，属预期）
  - 复制时排除 `.git`、`node_modules`

### 维护查询

```
python3 scripts/maintain_csv.py list-skills
python3 scripts/maintain_csv.py list-sources
python3 scripts/maintain_csv.py remove-skill <name>
```

`remove-skill` 只删除 `skills/<category>/<name>/` 与 `3rd-skills.csv` 对应行，不动 `sources/`。

## 最佳实践

### 脚本优先

- **所有操作通过脚本执行**：不手动编辑 CSV、不手动复制 skills
- **用户确认不可跳过**：必须展示报告清单，等待用户标记 ✅ 后才能引入
- **CSV 是唯一元数据源**：不维护单独的 catalog.md

### Skill 命名与分类

- 使用短名：`auth/` 而非 `authentication/`
- 小写 + 短横线：`web-artifacts-builder/`
- 分类标准：
  - **core** — 基础工具（skill-creator, find-skills）
  - **engineering** — 编码/测试/调试（diagnosing-bugs, frontend-design）
  - **planning** — 需求分析/方案设计（暂空）
  - **productivity** — 效率提升与文本处理（handoff, humanizer-zh）
  - **project-mgmt** — 项目流程管理（triage, to-tickets）
  - **learning** — 知识沉淀（暂空）

### 报告规范

`import.py` 的正则严格匹配 6 列表格，列顺序与内容格式不可改：

```
| ID | Skill | 描述 | 推荐度 | 分类 | 确认 |
|----|-------|------|--------|------|------|
| 1  | diagnosing-bugs | 系统化排障流程 | 5 | engineering | ✅ |
```

- `ID` 为数字；`Skill` 为 `[\w-]+`（目录名/短名）；`推荐度` 为 1–5（纯数字）；`分类` 必须是 6 个合法值之一（否则 `import.py` 回退 `productivity` 并警告）；`确认` 列只有该列填 ✅ 才会被引入
- 描述使用中文，可保留技术名词；体积大（>1MB）或依赖外部服务的 skill 在描述或报告备注中标明
- 每个源仓库一份报告：`docs/reports/<owner-repo>.md`；跨源汇总评估可另建 `docs/reports/new-skills-<date>.md`（能否引入只看 ✅ 行，不看文件名）
- 报告顶部「源仓库」应写真实 GitHub URL，不要用目录名拼 URL（owner-repo 是本地命名）

### Git 管理

- `sources/` 使用 git submodule，保留完整历史；`.gitmodules` 不手动编辑
- 新克隆必须 `git submodule update --init --recursive`，否则 `update.py` 会跳过全部源
- `sources/` 内容不手动修改；`data/` CSV 只由脚本写入
- 本地自研 skill（`on-demand-toolkit`、`gen-practice-notes`、`kbase`、`md2talk-video`）不在 CSV 管理范围，`sync.py` 不会处理

### 环境注意（Windows）

- 脚本按 UTF-8 读取 git 输出；Windows 默认 GBK 会报 `UnicodeDecodeError`（已在 `scripts/lib` 处理）
- Git 走 schannel 报 `SEC_E_NO_CREDENTIALS` 时，脚本会自动用 `-c http.sslBackend=openssl` 重试；手动 `git pull` 可执行 `git config --global http.sslBackend openssl`
- 沙箱环境里 `git submodule update --init` 可能报 `couldn't create signal pipe`；改用 `git -c http.sslBackend=openssl clone` 直接克隆对应源亦可

### 已知限制

- `analyze.py` 生成的 `**源仓库**: https://github.com/<source_name>` 对 `owner-repo` 命名会拼出无效 URL（如 `github.com/anthropics-skills`），以真实仓库地址为准
- `add_source.py` 写入的 `added_date` 可能为空，`last_commit` 为短 hash
- 源仓库删除/改名的 skill 不会自动清理，`sync.py` 仅警告；需要删除时用 `maintain_csv.py remove-skill`
