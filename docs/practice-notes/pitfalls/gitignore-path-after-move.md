---
title: 移动被 .gitignore 忽略的目录后，忽略规则会失效
category: pitfalls
tags: [git, gitignore, move]
created: 2026-11-12
updated: 2026-11-12
source: 2026-11-12 会话，learning 分类改名 knowledge
---

## 场景

目录被 `.gitignore` 按完整路径忽略，之后因为重构、改分类或改命名把它移动到新路径。

## 做法

1. 忽略规则尽量用通配，不绑定会变动的上级路径：

   ```gitignore
   skills/*/kbase/notes
   skills/*/kbase/notes.config
   ```

2. 移动目录后、`git add -A` 之前先看规模：

   ```bash
   git add -A --dry-run
   git diff --cached --name-only | wc -l
   ```

3. 已经误暂存时，先保留改动再重提：

   ```bash
   git reset --soft HEAD~1
   git rm -r --cached <误入目录>
   git add -A
   git commit
   ```

## 原因

`.gitignore` 的模式按仓库内路径匹配。规则写的是 `skills/productivity/kbase/notes`，目录移到 `skills/knowledge/kbase/notes` 后就不再命中，原本被忽略的运行时数据会重新变成「未跟踪文件」，被 `git add -A` 一并收进提交。

## 反例

把 `kbase` 从 `productivity` 移到 `knowledge` 后直接 `git add -A && git commit`，提交里混入 406 个文件、约 18.7 万行笔记库（含 PDF、图片）。用 `git reset --soft HEAD~1` 撤回，改通配规则并 `git rm -r --cached` 后重新提交，最终只有 4 个目录重命名、15 个文件变更。
