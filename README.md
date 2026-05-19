# Skills 仓库

统一管理、引入和更新第三方 skills 的集中式仓库。

## 快速开始

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
| `skills/` | opencode 扫描目录（6 个分类） |
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

| Skill | 分类 | 来源 |
|-------|------|------|
| skill-creator | core | anthropics/skills |
