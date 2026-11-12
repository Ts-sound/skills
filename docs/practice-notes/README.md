# 实践笔记

从实际工作中沉淀的可复用经验：流程约定、工具排障、易踩的坑。每条包含场景、做法、原因和反例，目标是下次遇到同类任务少走弯路。

| 标题 | 分类 | tags | 路径 | 更新时间 |
|------|------|------|------|----------|
| 工作区外与安全敏感操作先报备再执行 | workflow | permissions, ssh, safety, agent | [workflow/confirm-outside-workspace-ops.md](workflow/confirm-outside-workspace-ops.md) | 2026-11-12 |
| Git 推送失败的排查顺序（HTTPS 凭据 / SSH 端口） | tools | git, ssh, credentials, windows | [tools/git-push-auth-troubleshooting.md](tools/git-push-auth-troubleshooting.md) | 2026-11-12 |
| submodule 未初始化时 git 命令会落到父仓库 | pitfalls | git, submodule, automation | [pitfalls/git-submodule-uninitialized.md](pitfalls/git-submodule-uninitialized.md) | 2026-11-12 |
| 移动被 .gitignore 忽略的目录后，忽略规则会失效 | pitfalls | git, gitignore, move | [pitfalls/gitignore-path-after-move.md](pitfalls/gitignore-path-after-move.md) | 2026-11-12 |
