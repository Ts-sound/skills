# Skills 仓库

统一管理、引入和更新第三方 skills 的集中式仓库。

## 安装使用

### Claude Code

```bash
# 1. Clone 仓库
git clone https://github.com/Ts-sound/skills.git ~/skills-repo
cd ~/skills-repo

# 2. 初始化源仓库 submodule（否则 sources/ 为空，更新脚本无法工作）
git submodule update --init --recursive

# 3. 链接到 Claude Code（扁平链接，Claude Code 直接可用）
bash scripts/install-claude.sh

# 4. 配置启动时自动激活 caveman（仅 Claude Code）
python3 scripts/add-caveman-hook.py --claude

# 5. 更新本仓库
git pull
```

链接后 `~/.claude/skills/` 下直接是各 skill 目录（扁平结构，与 [mattpocock/skills](https://github.com/mattpocock/skills) 一致）。

### OpenCode

```bash
# 1. Clone 仓库并初始化 submodule
git clone https://github.com/Ts-sound/skills.git ~/skills-repo
cd ~/skills-repo
git submodule update --init --recursive

# 2. 安装为 OpenCode 插件（plugin + skills symlink）
bash scripts/install-opencode.sh

# 3. 更新本仓库
git pull
```

安装后重启 OpenCode，插件自动加载 skills。卸载：`bash scripts/install-opencode.sh --uninstall`

### Windows

Windows 下不用 bash 脚本，直接给全局 skills 目录建一个目录联接（junction），指向仓库根目录。`mklink /J` 不需要管理员权限。

```powershell
# 1. Clone 仓库（Git Bash 或 PowerShell 均可）
git clone https://github.com/Ts-sound/skills.git "$env:USERPROFILE\skills-repo"
cd "$env:USERPROFILE\skills-repo"
git submodule update --init --recursive

# 2. 建目录联接。目标形如 C:\Users\<用户名>\.agents\skills\skills-tong
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\skills-tong" "$env:USERPROFILE\skills-repo"

# 3. 更新本仓库（junction 自动跟随，无需重链）
cd "$env:USERPROFILE\skills-repo"; git pull
```

- 目标路径按客户端约定替换，例如 `C:\Users\17853\.agents\skills\skills-tong`
- 仓库保留 `skills/<category>/<name>/SKILL.md` 层级，递归扫描由客户端负责；一个联接指仓库根即可，不需要为每个 skill 单独建联接
- 符号链接 `New-Item -ItemType SymbolicLink` 需管理员或开启开发者模式，目录联接不需要
- 删除联接用 `cmd /c rmdir "<路径>"`，不要用 `del`，也不会删到仓库内容
- 若 git 报 `SEC_E_NO_CREDENTIALS`，执行 `git config --global http.sslBackend openssl` 后重试

## 维护管理

```bash
# 首次/新克隆：初始化源仓库 submodule
git submodule update --init --recursive

# 添加新源（自动克隆到 sources/<owner-repo> 并生成报告）
python3 scripts/add_source.py https://github.com/owner/repo.git

# 评审 docs/reports/<owner-repo>.md：在「确认」列填 ✅，然后引入
python3 scripts/import.py docs/reports/<owner-repo>.md

# 检查/同步已有源的更新
python3 scripts/update.py   # 拉取源仓库
python3 scripts/diff.py     # 查看差异
python3 scripts/sync.py     # 复制到 skills/

# 维护查询
python3 scripts/maintain_csv.py list-skills
python3 scripts/maintain_csv.py list-sources
python3 scripts/maintain_csv.py remove-skill <name>
```

报告表格固定 6 列：`| ID | Skill | 描述 | 推荐度 | 分类 | 确认 |`，顺序和格式不能改，否则 `import.py` 无法识别；只有「确认」列为 ✅ 的才会被引入。

## 目录结构

| 目录 | 说明 |
|------|------|
| `skills/` | 客户端扫描目录（按分类组织，当前 4 个分类 16 个 skill） |
| `sources/` | 第三方 git submodule 缓存 |
| `data/` | CSV 元数据（脚本维护） |
| `scripts/` | 自动化脚本 |
| `docs/` | 文档体系（设计、决策、调研报告） |

## 分类

| 分类 | 定位 |
|------|------|
| core | 基础工具 |
| engineering | 编码/测试/调试 |
| planning | 需求分析/方案设计 |
| productivity | 效率提升 |
| project-mgmt | 项目流程管理 |
| learning | 知识沉淀 |

## 已引入 Skills

共 16 个，分布在 4 个分类（以 `skills/` 目录实际内容为准，插件会自动扫描并注入说明）。

| Skill | 分类 | 来源 |
|-------|------|------|
| find-skills | core | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| on-demand-toolkit | core | 本地编写 |
| skill-creator | core | [anthropics/skills](https://github.com/anthropics/skills) |
| writing-for-agents | core | [mattpocock/skills](https://github.com/mattpocock/skills) |
| diagnosing-bugs | engineering | [mattpocock/skills](https://github.com/mattpocock/skills) |
| frontend-design | engineering | [anthropics/skills](https://github.com/anthropics/skills) |
| grill-me | engineering | [mattpocock/skills](https://github.com/mattpocock/skills) |
| grill-with-docs | engineering | [mattpocock/skills](https://github.com/mattpocock/skills) |
| caveman | productivity | 本地保留副本（源仓库已移除该目录） |
| gen-practice-notes | productivity | 本地编写 |
| handoff | productivity | [mattpocock/skills](https://github.com/mattpocock/skills) |
| humanizer-zh | productivity | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) |
| kbase | productivity | 本地编写 |
| md2talk-video | productivity | 本地编写 |
| to-tickets | project-mgmt | [mattpocock/skills](https://github.com/mattpocock/skills) |
| triage | project-mgmt | [mattpocock/skills](https://github.com/mattpocock/skills) |

> `planning/`、`learning/` 分类暂未引入 skill；`caveman` 因上游删除目录，已转为本地维护，`sync.py` 对其报 warning 属预期。
