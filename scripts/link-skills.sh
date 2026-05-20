#!/bin/bash
# link-skills.sh - 将本仓库的 skills 目录链接到 Claude Code / opencode
# 用法: bash scripts/link-skills.sh [--opencode] [--claude]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
REPO_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
SKILLS_SRC="$REPO_ROOT/skills"

NAMESPACE="ts-sound-skills"
DEFAULT_TARGET="$HOME/.claude/skills"
TARGET="$DEFAULT_TARGET"

while [[ $# -gt 0 ]]; do
    case "$1" in
        --opencode) TARGET="$HOME/.config/opencode/skills" ;;
        --claude)   TARGET="$HOME/.claude/skills" ;;
        --unlink)
            for t in "$HOME/.claude/skills/$NAMESPACE" "$HOME/.config/opencode/skills/$NAMESPACE"; do
                if [ -L "$t" ]; then
                    rm -v "$t"
                fi
            done
            exit 0
            ;;
        *) echo "Unknown: $1"; exit 1 ;;
    esac
    shift
done

mkdir -p "$TARGET"
LINK_PATH="$TARGET/$NAMESPACE"

rm -f "$LINK_PATH" 2>/dev/null || true
ln -s "$SKILLS_SRC" "$LINK_PATH"
echo "Linked: $LINK_PATH -> $SKILLS_SRC"
echo "Skills available at: $LINK_PATH/<category>/<skill>/SKILL.md"
