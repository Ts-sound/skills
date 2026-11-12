---
title: submodule 未初始化时 git 命令会落到父仓库
category: pitfalls
tags: [git, submodule, automation]
created: 2026-11-12
updated: 2026-11-12
source: 2026-11-12 会话，update.py 更新 sources 失败
---

## 场景

自动化脚本遍历 `sources/<repo>/` 执行 `git rev-parse`、`git pull` 或 `git fetch`，而这些子模块从未初始化。

## 做法

1. 运行前先执行 `git submodule update --init --recursive`。
2. 代码里不要只判断目录存在，要判断它是不是独立仓库：

   ```python
   subprocess.run(
       ["git", "rev-parse", "--show-toplevel"],
       cwd=path, capture_output=True, text=True,
   ).stdout.strip() == str(path.resolve())
   ```

3. 检测失败时明确报错并跳过，例如 `Not initialized: sources/xxx (run: git submodule update --init)`，不要静默继续。

## 原因

未初始化的 submodule 目录是空目录，路径存在但里面没有 `.git`。此时在目录内执行 git 命令，git 会沿父目录向上找到主仓库的 `.git`，把主仓库当成目标：`rev-parse HEAD` 返回主仓库 HEAD，`pull`/`fetch` 打到主仓库 remote。所有源仓库的 `last_commit` 会被写成同一个父仓库提交，脚本看起来「执行成功」，实际一个源都没更新。

## 反例

`update.py` 对 4 个空 `sources/` 目录逐一执行 `git pull`，`last_commit` 全被写成主仓库的 `94970e89`；主仓库 remote 需要凭据，第一条就报 `SEC_E_NO_CREDENTIALS` 中断。修复后先检测仓库归属，再按 `origin/<branch>` 比较和 checkout。
