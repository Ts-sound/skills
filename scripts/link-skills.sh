#!/usr/bin/env bash
set -euo pipefail

# link-skills.sh - 将仓库 skills/ 下所有 SKILL.md 扁平链接到 Claude Code / opencode
# 参照 mattpocock/skills 的扁平结构:
#   ~/.claude/skills/<skill-name> -> <repo>/skills/<category>/<skill-name>
#
# 用法: bash scripts/link-skills.sh [--opencode] [--claude]

REPO="$(cd "$(dirname "$0")/.." && pwd)"
SRC="$REPO/skills"
DEST="$HOME/.claude/skills"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --opencode) DEST="$HOME/.config/opencode/skills" ;;
        --claude)   DEST="$HOME/.claude/skills" ;;
        --unlink)
            # 删除 ~/.claude/skills/ 和 ~/.config/opencode/skills/ 中指向本仓库的链接
            for d in "$HOME/.claude/skills" "$HOME/.config/opencode/skills"; do
                if [ -d "$d" ]; then
                    for link in "$d"/*/; do
                        [ -L "$link" ] || continue
                        resolved="$(readlink -f "$link")"
                        case "$resolved" in
                            "$REPO"|"$REPO"/*)
                                rm -v "$link"
                                ;;
                        esac
                    done
                fi
            done
            exit 0
            ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
    shift
done

# 防止 ~/.claude/skills 本身是指向本仓库的符号链接
if [ -L "$DEST" ]; then
    resolved="$(readlink -f "$DEST")"
    case "$resolved" in
        "$REPO"|"$REPO"/*)
            echo "error: $DEST is a symlink into this repo ($resolved)." >&2
            echo "Remove it (rm \"$DEST\") and re-run; the script will recreate it as a real dir." >&2
            exit 1
            ;;
    esac
fi

mkdir -p "$DEST"

# 使用数组避免 subshell 问题（pipe 进 while 会丢失变量）
skill_dirs=()
while IFS= read -r -d '' skill_md; do
    skill_dirs+=("$skill_md")
done < <(find "$SRC" -name SKILL.md -not -path '*/node_modules/*' -print0)

for skill_md in "${skill_dirs[@]}"; do
    src="$(dirname "$skill_md")"
    name="$(basename "$src")"
    target="$DEST/$name"

    if [ -e "$target" ] && [ ! -L "$target" ]; then
        rm -rf "$target"
    fi

    ln -sfn "$src" "$target"
    echo "  $name -> $src"
done

echo "Linked ${#skill_dirs[@]} skills to $DEST/"
