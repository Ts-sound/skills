# Installing Skills for OpenCode

## Prerequisites

- [OpenCode.ai](https://opencode.ai) installed
- Git installed

## Installation

### 1. Clone Skills Repository

```bash
git clone https://github.com/your-org/skills.git ~/skills-repo
cd ~/skills-repo
```

### 2. Run Installation Script

```bash
bash scripts/install-opencode.sh
```

This will:
- Create symlink: `~/.config/opencode/plugins/skills.js` -> `~/skills-repo/.opencode/plugins/skills.js`
- Create symlink: `~/.config/opencode/skills/skills` -> `~/skills-repo/skills/`

### 3. Restart OpenCode

Restart OpenCode. The plugin will automatically:
- Activate caveman mode on session start
- Provide skills discovery guidance in system prompt

## Verification

Ask opencode: "caveman active?"
Should respond in terse caveman mode.

## Uninstall

```bash
bash scripts/install-opencode.sh --uninstall
```

## Manual Installation (Alternative)

```bash
# Plugin symlink
mkdir -p ~/.config/opencode/plugins
rm -f ~/.config/opencode/plugins/skills.js
ln -s ~/skills-repo/.opencode/plugins/skills.js ~/.config/opencode/plugins/skills.js

# Skills symlink
mkdir -p ~/.config/opencode/skills
rm -rf ~/.config/opencode/skills/skills
ln -s ~/skills-repo/skills ~/.config/opencode/skills/skills
```

## Updating

```bash
cd ~/skills-repo
git pull
```

Restart OpenCode to apply changes.