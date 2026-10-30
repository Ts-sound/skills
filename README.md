# Skills 仓库

统一管理、引入和更新第三方 skills 的集中式仓库。

## 安装使用

### Claude Code

```bash
# 1. Clone 仓库
git clone https://github.com/Ts-sound/skills.git ~/skills-repo

# 2. 链接到 Claude Code（扁平链接，Claude Code 直接可用）
bash ~/skills-repo/scripts/install-claude.sh

# 3. 配置启动时自动激活 caveman（仅 Claude Code）
python3 ~/skills-repo/scripts/add-caveman-hook.py --claude

# 4. 更新
cd ~/skills-repo && git pull
```

链接后 `~/.claude/skills/` 下直接是各 skill 目录（扁平结构，与 [mattpocock/skills](https://github.com/mattpocock/skills) 一致）。

### OpenCode

```bash
# 1. Clone 仓库
git clone https://github.com/Ts-sound/skills.git ~/skills-repo

# 2. 安装为 OpenCode 插件（plugin + skills symlink）
bash ~/skills-repo/scripts/install-opencode.sh

# 3. 更新
cd ~/skills-repo && git pull
```

安装后重启 OpenCode，插件自动加载 skills。卸载：`bash scripts/install-opencode.sh --uninstall`

### Windows

Windows 下不用 bash 脚本，直接给全局 skills 目录建一个目录联接（junction），指向仓库根目录。`mklink /J` 不需要管理员权限。

```powershell
# 1. Clone 仓库（Git Bash 或 PowerShell 均可）
git clone https://github.com/Ts-sound/skills.git "$env:USERPROFILE\skills-repo"

# 2. 建目录联接。目标形如 C:\Users\<用户名>\.agents\skills\skills-tong
New-Item -ItemType Directory -Force -Path "$env:USERPROFILE\.agents\skills" | Out-Null
cmd /c mklink /J "$env:USERPROFILE\.agents\skills\skills-tong" "$env:USERPROFILE\skills-repo"

# 3. 更新（junction 自动跟随，无需重链）
cd "$env:USERPROFILE\skills-repo"; git pull
```

- 目标路径按客户端约定替换，例如 `C:\Users\17853\.agents\skills\skills-tong`
- 仓库保留 `skills/<category>/<name>/SKILL.md` 层级，客户端需支持递归扫描；只认扁平结构的客户端改用 `install-claude.sh`（需 Git Bash）或逐个建联接
- 符号链接 `New-Item -ItemType SymbolicLink` 需管理员或开启开发者模式，目录联接不需要
- 删除联接用 `cmd /c rmdir "<路径>"`，不要用 `del`，也不会删到仓库内容

## 维护管理

```bash
# 添加新源
python3 scripts/add_source.py https://github.com/owner/repo.git

# 查看报告 → 编辑确认列 → 执行引入
python3 scripts/import.py docs/reports/<repo>.md

# 维护查询
python3 scripts/maintain_csv.py list-skills
python3 scripts/maintain_csv.py list-sources
```

## 目录结构

| 目录 | 说明 |
|------|------|
| `skills/` | opencode 扫描目录（按分类组织，当前 4 个分类 14 个 skill） |
| `sources/` | 第三方 git submodule 缓存 |
| `data/` | CSV 元数据（脚本维护） |
| `scripts/` | 自动化脚本 |
| `docs/` | 文档体系 |

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

共 14 个，分布在 4 个分类（以 `skills/` 目录实际内容为准，插件会自动扫描并注入说明）。

| Skill | 分类 | 来源 |
|-------|------|------|
| find-skills | core | [vercel-labs/skills](https://github.com/vercel-labs/skills) |
| on-demand-toolkit | core | 本地编写 |
| skill-creator | core | [anthropics/skills](https://github.com/anthropics/skills) |
| write-a-skill | core | [mattpocock/skills](https://github.com/mattpocock/skills) |
| diagnose | engineering | [mattpocock/skills](https://github.com/mattpocock/skills) |
| frontend-design | engineering | [anthropics/skills](https://github.com/anthropics/skills) |
| grill-me | engineering | [mattpocock/skills](https://github.com/mattpocock/skills) |
| grill-with-docs | engineering | [mattpocock/skills](https://github.com/mattpocock/skills) |
| caveman | productivity | [mattpocock/skills](https://github.com/mattpocock/skills) |
| gen-practice-notes | productivity | 本地编写 |
| handoff | productivity | [mattpocock/skills](https://github.com/mattpocock/skills) |
| humanizer-zh | productivity | [op7418/Humanizer-zh](https://github.com/op7418/Humanizer-zh) |
| kbase | productivity | 本地编写 |
| to-issues | project-mgmt | [mattpocock/skills](https://github.com/mattpocock/skills) |
| triage | project-mgmt | [mattpocock/skills](https://github.com/mattpocock/skills) |

> `planning/`、`learning/` 分类暂未引入 skill。
