#!/usr/bin/env bash
set -euo pipefail

# install-opencode.sh - Install skills as OpenCode plugin (global)
# Usage: bash scripts/install-opencode.sh [--install|--uninstall|--check]

REPO="$(cd "$(dirname "$0")/.." && pwd)"
PLUGIN_SRC="$REPO/.opencode/plugins/skills.js"
SKILLS_SRC="$REPO/skills"

PLUGIN_DST_DIR="$HOME/.config/opencode/plugins"
PLUGIN_DST="$PLUGIN_DST_DIR/skills.js"

SKILLS_DST_DIR="$HOME/.config/opencode/skills"
SKILLS_DST="$SKILLS_DST_DIR/skills"

usage() {
    echo "Usage: $0 [--install|--uninstall|--check]"
    echo "  --install   Create symlinks (default if no args)"
    echo "  --uninstall Remove symlinks"
    echo "  --check     Check installation status"
    exit 1
}

action="install"
for arg in "$@"; do
    case "$arg" in
        --install) action="install" ;;
        --uninstall) action="uninstall" ;;
        --check) action="check" ;;
        *) usage ;;
    esac
done

check_plugin() {
    if [ -L "$PLUGIN_DST" ]; then
        local resolved
        resolved="$(readlink -f "$PLUGIN_DST")"
        if [ "$resolved" = "$(readlink -f "$PLUGIN_SRC")" ]; then
            echo "✓ Plugin: $PLUGIN_DST -> $resolved"
            return 0
        else
            echo "✗ Plugin: $PLUGIN_DST points to $resolved (expected $PLUGIN_SRC)"
            return 1
        fi
    elif [ -e "$PLUGIN_DST" ]; then
        echo "✗ Plugin: $PLUGIN_DST exists but is not a symlink"
        return 1
    else
        echo "✗ Plugin: $PLUGIN_DST does not exist"
        return 1
    fi
}

check_skills() {
    if [ -L "$SKILLS_DST" ]; then
        local resolved
        resolved="$(readlink -f "$SKILLS_DST")"
        if [ "$resolved" = "$(readlink -f "$SKILLS_SRC")" ]; then
            echo "✓ Skills: $SKILLS_DST -> $resolved"
            return 0
        else
            echo "✗ Skills: $SKILLS_DST points to $resolved (expected $SKILLS_SRC)"
            return 1
        fi
    elif [ -e "$SKILLS_DST" ]; then
        echo "✗ Skills: $SKILLS_DST exists but is not a symlink"
        return 1
    else
        echo "✗ Skills: $SKILLS_DST does not exist"
        return 1
    fi
}

do_install() {
    echo "Installing skills plugin to OpenCode..."

    # Check source exists
    if [ ! -f "$PLUGIN_SRC" ]; then
        echo "Error: Plugin source not found: $PLUGIN_SRC"
        exit 1
    fi

    if [ ! -d "$SKILLS_SRC" ]; then
        echo "Error: Skills source not found: $SKILLS_SRC"
        exit 1
    fi

    # Create plugin directory
    mkdir -p "$PLUGIN_DST_DIR"

    # Remove existing (file or broken symlink)
    if [ -e "$PLUGIN_DST" ]; then
        rm -f "$PLUGIN_DST"
    fi

    # Create plugin symlink
    ln -s "$PLUGIN_SRC" "$PLUGIN_DST"
    echo "  Plugin: $PLUGIN_DST"

    # Create skills directory
    mkdir -p "$SKILLS_DST_DIR"

    # Remove existing (file or broken symlink)
    if [ -e "$SKILLS_DST" ]; then
        rm -rf "$SKILLS_DST"
    fi

    # Create skills symlink
    ln -s "$SKILLS_SRC" "$SKILLS_DST"
    echo "  Skills: $SKILLS_DST"

    echo ""
    echo "Done! Restart OpenCode to activate."
    echo "Verify by asking: 'caveman active?'"
}

do_uninstall() {
    echo "Uninstalling skills plugin from OpenCode..."

    removed=0

    if [ -L "$PLUGIN_DST" ]; then
        rm -f "$PLUGIN_DST"
        echo "  Removed: $PLUGIN_DST"
        removed=1
    fi

    if [ -L "$SKILLS_DST" ]; then
        rm -f "$SKILLS_DST"
        echo "  Removed: $SKILLS_DST"
        removed=1
    fi

    if [ $removed -eq 0 ]; then
        echo "  No symlinks found to remove."
    else
        echo ""
        echo "Done. Restart OpenCode."
    fi
}

do_check() {
    echo "Checking skills installation..."
    echo ""

    echo "Plugin:"
    check_plugin || true
    echo ""

    echo "Skills:"
    check_skills || true
    echo ""

    echo "Available skills:"
    if [ -d "$SKILLS_SRC" ]; then
        for cat in "$SKILLS_SRC"/*/; do
            [ -d "$cat" ] || continue
            cat_name="$(basename "$cat")"
            echo "  $cat_name/"
            for skill in "$cat"/*/; do
                [ -d "$skill" ] || continue
                skill_name="$(basename "$skill")"
                echo "    - $skill_name"
            done
        done
    fi
}

case "$action" in
    install) do_install ;;
    uninstall) do_uninstall ;;
    check) do_check ;;
esac