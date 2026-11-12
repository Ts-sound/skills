---
title: Git 推送失败的排查顺序（HTTPS 凭据 / SSH 端口）
category: tools
tags: [git, ssh, credentials, windows]
created: 2026-11-12
updated: 2026-11-12
source: 2026-11-12 会话，推送 skills 仓库
---

## 场景

`git push` 失败，报错涉及凭据、认证或连接超时；或者远程仓库明明有权限却推不上去。

## 做法

按传输协议分流，先定位再改配置：

1. `git remote -v` 确认走 HTTPS 还是 SSH。
2. **HTTPS**：
   - `could not read Username for 'https://github.com'`、`SEC_E_NO_CREDENTIALS`、`User cancelled dialog` 都是**本地缺可用凭据**，不是仓库权限问题。
   - 依次检查 `git config --get-all credential.helper`、`cmdkey /list`（找 github 条目）、`GH_TOKEN` / `GITHUB_TOKEN`、`gh auth status`。
   - 没有凭据时，要么交互登录一次让 credential manager 保存，要么改用 SSH。
3. **SSH**：
   - `ssh -T git@github.com` 验证密钥；成功会返回 `Hi <user>!`。
   - 22 端口超时可试 443：`ssh -p 443 -T git@ssh.github.com`，remote 写成 `ssh://git@ssh.github.com:443/<owner>/<repo>.git`。
   - 想保留 `git@github.com:<owner>/<repo>.git` 标准写法，可在 `~/.ssh/config` 配 Host 别名转到 443（改配置前先征得同意）。
4. 沙箱/受限环境里 git 调 ssh 报 `sh.exe: *** fatal error - couldn't create signal pipe, Win32 error 5`，是执行环境禁止管道，不是网络或密钥问题；换到普通终端验证。

## 原因

HTTPS 与 SSH 的失败原因完全不同：前者缺凭据，后者缺网络可达性或密钥授权。先分清协议能避免在错误层面反复改配置。schannel 报错只说明 TLS 后端拿不到凭据，换 `http.sslBackend=openssl` 仍会回到同一个凭据问题。

## 反例

- 为测试 443 是否可用，用 `StrictHostKeyChecking=no` + `UserKnownHostsFile=/dev/null` 关掉主机密钥校验，等于放弃中间人防护。
- 看到 `SEC_E_NO_CREDENTIALS` 就反复重试 `git pull`，没有先确认 credential helper 和已存凭据。
- 在沙箱里把 signal pipe 报错误判为网络故障。
