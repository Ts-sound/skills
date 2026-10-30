---
name: kbase
description: 知识库（KBase）。将对话、文档或 gen-practice-notes 的笔记二次归纳为可检索的知识条目，支持按关键词/标签/别名检索。写入前先查重并反馈提纲，经允许后写入。
---

# 知识库（KBase）

## 定位
二级提炼：只留结论、要点、适用场景，去上下文，强调可检索、可复用。
与 gen-practice-notes 分工：notes 保过程，KBase 保结论，source 做桥。

## 何时使用
- 写入：用户说“归纳到知识库/KBase”“把 notes 提炼进来”“记成知识条目”
- 检索：用户问“KBase 里有没有 X”“查一下之前记的 Y”

## notes 目录
- 约定：skill 目录下 `notes/` 是指向用户指定目录的软链接
- 首次使用：`notes/` 缺失或断链时，询问用户提供 KBase 根目录**绝对路径**，
  校验存在/可写后建软链接，写入 `notes.config`，之后不再询问
- 断链检测：`[ -L notes ] && [ -e notes ]`；断链则提示重新配置，不自动回退
- 目录结构：`notes/INDEX.md` + `notes/entries/`

## INDEX.md 格式
固定四列，顺序不变：

```markdown
# KBase 索引

| 标题 | tags | 路径 | 更新时间 |
|---|---|---|---|
| 提交前本地跑 lint | git, ci, lint | entries/kb-0001-precommit-lint.md | 2026-09-02 |
```

- 路径相对 notes 根，不带前导 `./`
- tags 用逗号串，不用 YAML 列表
- 按 id 升序，新条目追加末尾；合并更新只改原有行的更新时间，不挪位置
- INDEX 只做导航，不放结论；写了条目就必有一行，反之亦然

## 条目格式
文件名：`<id>-<kebab-slug>.md`，如 `kb-0004-docker-build-cache.md`
frontmatter 必含：id / title / tags / aliases / keywords / source / created / updated
正文：结论（一句话）→ 要点 → 适用场景 → 参考
- 结论必须可独立读懂
- aliases 收常见叫法，keywords 收检索词
- source 必填：回指 notes 文件路径或原始来源

## id 分配
- 格式固定 `kb-` + 四位补零序号，`kb-0001` 起
- 写入前**重新列一次** `entries/` 取当前最大序号 +1，不要用提纲阶段的旧值（中间可能有别的写入）
- 目标文件名已存在 → 重取一次最大序号再写，不覆盖
- 并行/多会话同时 ingestion 时，落盘后校验 id 与文件名一致；不一致则改名并对齐 INDEX 行
- id 只增不回收，删除条目后空号保留

## 查重与合并判定
按顺序判定，命中即止：
1. 待入库内容与某条目的 `source` 指向同一个 notes 文件 → 合并更新该条目
2. title / aliases / keywords 有实质交集，且「适用场景」讲的是同一个问题 → 合并，source 追加新来源
3. 同主题但层次不同（如「工具用法」vs「协作流程」）→ 新建，并在两边「参考」互相链接
4. 吃不准 → 提纲里标「待定」，说明两种处理差异，交用户裁决，不要擅自新建

合并只做增量：补要点、补 aliases/keywords、必要时改写结论；不删除原有要点，不整段重写。合并后 bump `updated`。

## ingest 模式（从实践笔记二次归纳）
触发：用户要求把 notes 提炼进 KBase，或由 gen-practice-notes 移交
1. 读取指定 notes（单条/多条/最近 N 条）
2. 按主题聚合，一个主题一条 KB 条目
3. 提炼为：结论 + 要点 + 适用场景，source 回指 notes 路径
4. 查重：按「查重与合并判定」处理，同主题合并更新（bump updated），否则新建
5. 反馈提纲：title / tags / aliases / keywords / 结论摘要 / 新建或合并 / source
6. **等待用户允许**
7. 写入 entries/（id 按「id 分配」现取，不沿用提纲值），更新 INDEX.md
8. 回报：新建/合并条目、溯源 notes、索引变更

## 直接写入模式
用户直接给内容要求入库时，同样走：提炼 → 查重 → 反馈提纲 → 等待允许 → 写入 → 更新索引。

## 检索流程
1. 读 `notes/INDEX.md`，按 title/tags/aliases/keywords 匹配
2. 未命中用 `rg -i "<关键词>" notes/entries/` 兜底
3. 返回 top 3–5：title + 结论 + 路径
4. 需要详情再读对应条目
5. 若只在一级 notes 命中、KBase 没有，可提议提炼成 KB 条目

## 约束
- 未获允许不得写入
- 写入前必须查重，禁止同主题重复建条
- 不复制 notes 全文，只提炼结论式条目
- source 必填，保证可溯源
- INDEX.md 与 entries 保持同步，无孤儿条目
- 检索结果必须带路径
