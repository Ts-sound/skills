
## 目标

- **主要目标**: 建立完整的 Skills 仓库结构和文档体系
- **成功指标**:
  - 目录结构完整创建
  - 核心文档（README、AGENTS.md、设计、需求、决策）齐备且内容一致
  - 可开始执行第三方 skills 的调研和引入

## 范围

- 目录结构创建（skills/ 6个分类子目录、sources/、data/、docs/reports/）
- 文档体系建立（README.md、AGENTS.md、docs/design/、docs/requirements.md、docs/decisions.md）
- 数据文件创建（data/sub-repo.csv、data/3rd-skills.csv）
- 分类体系定义（core、engineering、planning、productivity、project-mgmt、learning）
- Skills 管理流程规范（添加源、调研、引入、更新）
- 第三方 skills 的实际拉取和调研（后续任务）
- 自动化同步脚本编写（scripts/，后续任务）
- opencode 全局配置修改（单独任务）
- docs/reports/ 内容填充（按需创建）

## 需求描述

### 功能需求

#### F1: 目录结构管理
- 创建 `skills/` 分类子目录（core、engineering、planning、productivity、project-mgmt、learning）
- 创建 `sources/` 作为第三方源码缓存
- 创建 `data/` 存放脚本维护的 CSV 数据
- 创建 `docs/reports/` 存放调研报告
- 创建 `scripts/` 存放自动化脚本

#### F2: 第三方 skills 引入流程
- 通过 git submodule 拉取源码到 `sources/`
- 使用 analyze.py 分析 skills 内容并生成调研报告到 `docs/reports/`
- 报告包含确认列，用户标记 ✅ 后执行引入
- 使用 import.py 解析确认列，写入 data/3rd-skills.csv，复制到对应 `skills/<category>/` 目录

#### F3: 第三方 skills 更新流程
- 使用 update.py 检查 sources/ 中子模块是否有更新
- 有更新则 pull 最新代码
- 使用 diff.py 分析变更内容
- 生成变更报告到 docs/reports/
- 使用 sync.py 同步变更到 skills/ 中已引入的 skills

#### F4: 文档体系
- `README.md` — 项目说明和快速开始
- `AGENTS.md` — AI Agent 使用指引
- `docs/design/README.md` — 设计文档
- `docs/requirements.md` — 需求文档
- `docs/decisions.md` — 决策记录（ADRs）
- `docs/reports/` — 调研报告

#### F5: 数据管理（CSV，脚本维护）
- `data/sub-repo.csv` — 子项目源记录
- `data/3rd-skills.csv` — 第三方 skill 条目

#### F6: Scripts 自动化（Python）
- `scripts/add_source.py` — 添加新源（git submodule）并更新 sub-repo.csv
- `scripts/analyze.py` — 分析 sources/ 中的 skills 并生成含确认列的调研报告
- `scripts/import.py` — 解析报告确认列，写入 3rd-skills.csv，复制到 skills/
- `scripts/update.py` — 检查并拉取 sources/ 更新
- `scripts/diff.py` — 对比 sources/ 与 skills/ 的差异
- `scripts/sync.py` — 将 sources/ 中的变更同步到 skills/
- `scripts/maintain_csv.py` — 维护 data/ 下的 CSV 文件

### 非功能需求

#### NF1: 可维护性
- 每个 skill 目录结构统一为 `<skill-name>/SKILL.md`
- 引入的 skill 需在 `data/3rd-skills.csv` 中登记来源信息
- 文档使用 Markdown 格式，遵循统一的标题层级
- CSV 数据通过脚本维护，不手动编辑

#### NF2: 可追溯性
- 每个引入的 skill 需记录：来源仓库、原始路径、引入日期、是否修改
- `sources/` 保留完整 git 历史
- 变更通过 git commit 记录
- CSV 数据是唯一的来源记录，不维护单独的 catalog.md

#### NF3: 兼容性
- 兼容 opencode 和 Claude Code 的 skill 格式
- skills/ 目录结构不破坏 opencode 扫描机制

#### NF4: 性能
- scripts/ 脚本执行时间 < 30s（单次分析/同步）
- sources/ 仓库数量 < 20 个时保持响应流畅

### 用户故事

```
作为 AI Agent 使用者
我希望有一个统一的 Skills 管理仓库
以便能够方便地引入、管理和更新第三方 skills
```

### 约束条件

| 约束 | 说明 |
|------|------|
| opencode 扫描路径 | 仅 `skills/` 目录会被扫描 |
| Skill 格式 | 每个 skill 必须包含 `SKILL.md` |
| Python 版本 | scripts/ 使用 Python 3.9+ |
| Git 依赖 | sources/ 需要 git clone/pull 能力 |

### 风险与依赖

| 风险 | 影响 | 缓解措施 |
|------|------|----------|
| 上游 skill 格式变更 | 引入的 skill 可能不兼容 | 记录来源 commit，定期验证 |
| 第三方仓库废弃 | 无法更新 | 在 CSV 中记录最后可用版本 |
| Skill 冲突 | 同名 skill 来自不同源 | CSV 中记录优先级 |

### 阶段划分

| 阶段 | 内容 | 交付物 |
|------|------|--------|
| Phase 1: 初始化 | 目录结构创建、文档体系建立 | 完整目录树、核心文档 |
| Phase 2: 引入流程 | 添加 1-2 个源，完成首次引入 | sources/、首份报告、引入的 skills |
| Phase 3: 自动化 | scripts/ 脚本编写 | 可运行的分析/同步脚本 |
| Phase 4: 维护流程 | 更新流程验证、CSV 数据维护 | 更新报告、CSV 数据完整 |

## 验收标准

| ID | 验收项 | 标准 |
|----|--------|------|
| AC1 | 目录结构 | skills/ 下 6 个分类目录全部存在 |
| AC2 | 核心文档 | README.md、AGENTS.md、design/README.md、requirements.md、decisions.md 均存在且非空 |
| AC3 | 首次引入 | 至少 1 个第三方 skill 成功引入到 skills/ |
| AC4 | 报告生成 | 至少 1 份调研报告存在于 docs/reports/ |
| AC5 | 数据记录 | data/3rd-skills.csv 包含所有引入 skill 的来源信息 |
| AC6 | 数据完整性 | data/sub-repo.csv 记录所有 sources/ 下的仓库 |
| AC7 | 文档一致性 | requirements.md、design/README.md、AGENTS.md 中的目录结构描述一致 |
| AC8 | scripts 可用 | scripts/ 中的脚本可执行且输出符合预期 |


## 技术方案

### 目录结构设计

```
/
├── README.md                           # 项目说明
├── AGENTS.md                           # Agent 使用指引
├── LICENSE                             # 许可证
├── .gitignore
│
├── skills/                             # opencode 扫描目录
│   ├── core/                           # 核心基础 skills
│   │   └── <skill-name>/SKILL.md
│   ├── engineering/                    # 编码、测试、调试
│   │   └── <skill-name>/SKILL.md
│   ├── planning/                       # 需求分析、方案设计
│   │   └── <skill-name>/SKILL.md
│   ├── productivity/                   # 效率提升
│   │   └── <skill-name>/SKILL.md
│   ├── project-mgmt/                   # 项目流程管理
│   │   └── <skill-name>/SKILL.md
│   └── learning/                       # 知识沉淀、上下文构建
│       └── <skill-name>/SKILL.md
│
├── sources/                            # 第三方 git submodule 缓存
│
├── data/                               # 数据文件（脚本维护）
│   ├── sub-repo.csv                    # 子项目源记录
│   └── 3rd-skills.csv                  # 第三方 skill 条目
│
└── docs/                               # 文档
    ├── design/                         # 设计文档目录
    │   └── README.md
    ├── requirements.md                 # 需求文档
    ├── decisions.md                    # 决策记录
    └── reports/                        # 调研报告
```

**说明：**
- `skills/` 是 opencode 唯一扫描路径
- 每个分类作为 skills/ 的子目录，skill 以 `<skill-name>/SKILL.md` 形式存放
- `sources/` 仅作为第三方源码缓存，不参与 opencode 扫描
- `data/` 存放脚本维护的 CSV 数据，不手动编辑
- `docs/reports/` 按需创建，每个 source 一份报告

### 分类体系

| 分类 | 定位 | 目录 |
|------|------|------|
| core | 基础工具，不依赖项目上下文 | skills/core/ |
| engineering | 编码、测试、调试 | skills/engineering/ |
| planning | 需求分析、方案设计 | skills/planning/ |
| productivity | 效率提升 | skills/productivity/ |
| project-mgmt | 项目流程管理 | skills/project-mgmt/ |
| learning | 知识沉淀、上下文构建 | skills/learning/ |

### 工作流

#### 引入流程
```
添加源 → python3 scripts/add_source.py <git-url>
  → sources/ 作为 git submodule 添加
  → analyze.py 生成调研报告到 docs/reports/
  → 用户查看报告，在确认列填入 ✅
  → python3 scripts/import.py <report.md>
  → 解析确认列 → 写入 data/3rd-skills.csv → 复制到 skills/<category>/
```

#### 更新流程
```
检查更新 → python3 scripts/update.py
  → pull sources/ 子模块
  → python3 scripts/diff.py 分析差异
  → 同步变更 → python3 scripts/sync.py
```
