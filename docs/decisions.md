# Architecture Decision Records

## ADR-001: 采用 sources/ submodule + skills/ 分类的分离架构

**日期**: 2025-05-19
**状态**: 已采纳

### 背景

需要建立一个第三方 skills 的统一管理机制，既要保留完整 git 历史，又要让 opencode 能正确扫描。

### 决策

sources/ 使用 git submodule 管理第三方源码，skills/<category>/ 作为分类目录供 opencode 扫描。引入流程通过脚本（add_source.py → analyze.py → import.py）完成，用户通过报告确认列参与决策。

### 理由

- git submodule 保留完整 git 历史，便于追踪变更来源和版本对比
- opencode 只扫描 `skills/` 避免干扰和重复加载
- 分类目录便于管理和查找
- 脚本操作保证可追溯性，CSV 是唯一元数据源

### 替代方案

1. **裸 git clone** — 放弃，无法追踪版本
2. **单一目录扁平存放** — 放弃，skill 数量增多后难以维护

### 影响

- 需要维护 sources/ 与 skills/ 的同步机制
- 引入的 skill 需在 3rd-skills.csv 中登记来源
- 必须通过脚本操作，不手动编辑 CSV
