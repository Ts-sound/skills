<#
.SYNOPSIS
    将仓库的 skills/ 目录联接（junction）到客户端全局 skills 目录，例如
    %USERPROFILE%\.agents\skills\skills-tong。

.DESCRIPTION
    指向的是仓库内的 skills/ 子目录，而不是仓库根目录：客户端按
    <挂载点>/<category>/<name>/SKILL.md 扫描，多挂一层仓库根会把
    sources/、docs/ 一起暴露出去。

    mklink /J 不需要管理员权限。卸载用 -Unlink，只删除联接本身。

.PARAMETER LinkPath
    挂载点路径，默认 $env:USERPROFILE\.agents\skills\skills-tong。

.PARAMETER Unlink
    只删除联接，不重建。

.EXAMPLE
    pwsh scripts/install-agents.ps1
    pwsh scripts/install-agents.ps1 -LinkPath "$env:USERPROFILE\.agents\skills\skills-tong"
    pwsh scripts/install-agents.ps1 -Unlink
#>
[CmdletBinding()]
param(
    [string]$LinkPath = (Join-Path $env:USERPROFILE '.agents\skills\skills-tong'),
    [switch]$Unlink
)

$ErrorActionPreference = 'Stop'

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..')).Path
$Target = Join-Path $RepoRoot 'skills'

function Get-LinkTarget([string]$Path) {
    $item = Get-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    if ($null -eq $item) { return $null }
    if (-not ($item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { return $null }
    return $item.Target
}

if (-not (Test-Path -LiteralPath $Target -PathType Container)) {
    throw "缺少 skills 目录: $Target"
}

$existing = Get-LinkTarget $LinkPath

if ($Unlink) {
    if ($null -eq $existing) {
        if (Test-Path -LiteralPath $LinkPath) {
            throw "$LinkPath 不是目录联接，拒绝删除（避免误删真实目录）"
        }
        Write-Host "未安装: $LinkPath"
        return
    }
    cmd /c rmdir "$LinkPath"
    Write-Host "已移除联接: $LinkPath"
    return
}

if (Test-Path -LiteralPath $LinkPath) {
    if ($null -eq $existing) {
        throw "$LinkPath 已存在且不是目录联接，先手动确认并移走"
    }
    if ([string]::Equals($existing, $Target, [StringComparison]::OrdinalIgnoreCase)) {
        Write-Host "已就绪: $LinkPath -> $Target"
        return
    }
    Write-Host "重建联接: $existing -> $Target"
    cmd /c rmdir "$LinkPath"
}

New-Item -ItemType Directory -Force -Path (Split-Path -Parent $LinkPath) | Out-Null
cmd /c mklink /J "$LinkPath" "$Target" | Out-Null

$linked = Get-LinkTarget $LinkPath
if (-not [string]::Equals($linked, $Target, [StringComparison]::OrdinalIgnoreCase)) {
    throw "联接创建失败: 期望 $Target，实际 $linked"
}

$count = @(Get-ChildItem -LiteralPath $LinkPath -Directory |
    ForEach-Object { Get-ChildItem -LiteralPath $_.FullName -Directory } |
    Where-Object { Test-Path -LiteralPath (Join-Path $_.FullName 'SKILL.md') }).Count

Write-Host "已安装: $LinkPath -> $Target（$count 个 skill）"
