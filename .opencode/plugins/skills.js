/**
 * Skills plugin for OpenCode.ai
 *
 * Injects skills bootstrap context via system prompt transform.
 * - Auto-activates caveman communication mode on session start
 * - Provides skills discovery/usage guidance
 */

import path from 'path';
import fs from 'fs';
import os from 'os';
import { fileURLToPath } from 'url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatterStr = match[1];
  const body = match[2];
  const frontmatter = {};

  for (const line of frontmatterStr.split('\n')) {
    const colonIdx = line.indexOf(':');
    if (colonIdx > 0) {
      const key = line.slice(0, colonIdx).trim();
      const value = line.slice(colonIdx + 1).trim().replace(/^["']|["']$/g, '');
      frontmatter[key] = value;
    }
  }

  return { frontmatter, content: body };
};

const normalizePath = (p, homeDir) => {
  if (!p || typeof p !== 'string') return null;
  let normalized = p.trim();
  if (!normalized) return null;
  if (normalized.startsWith('~/')) {
    normalized = path.join(homeDir, normalized.slice(2));
  } else if (normalized === '~') {
    normalized = homeDir;
  }
  return path.resolve(normalized);
};

export const SkillsPlugin = async ({ client, directory }) => {
  const homeDir = os.homedir();
  const skillsRootDir = path.resolve(__dirname, '../..');
  const skillsDir = path.join(skillsRootDir, 'skills');
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');

  const getBootstrapContent = () => {
    const parts = [];

    // === CAVEMAN: Auto-activate ===
    const cavemanPath = path.join(skillsDir, 'productivity/caveman/SKILL.md');
    if (fs.existsSync(cavemanPath)) {
      const cavemanContent = fs.readFileSync(cavemanPath, 'utf8');
      const { content } = extractAndStripFrontmatter(cavemanContent);

      parts.push(`<CAVEMAN_AUTOACTIVATE>
You are now in CAVEMAN MODE. This is NOT a skill to load - it is ACTIVE by default.

${content}
</CAVEMAN_AUTOACTIVATE>`);
    }

    // === SKILLS: Discovery and usage ===
    const skillsInfo = `**Skills Location:**
Your skills are installed at: \`${configDir}/skills/skills/\`

**Available Skills:**
- \`caveman\` - Ultra-compressed communication (already active)
- \`brainstorming\` - Creative design exploration
- \`systematic-debugging\` - Bug diagnosis workflow
- \`project-structure\` - Project scaffolding
- \`frontend-design\` - UI/UX creation
- \`mermaid-diagram\` - Diagrams and visualizations
- \`skill-creator\` - Create new skills
- And more in: core/, engineering/, planning/, productivity/, project-mgmt/, learning/

**Using Skills:**
Use OpenCode's native \`skill\` tool to list and load skills:
- \`skill list\` - Show all available skills
- \`skill use <name>\` - Load a specific skill

**Skill Workflow:**
1. Before any implementation: Use \`brainstorming\` or \`systematic-debugging\`
2. During coding: Use domain-specific skills (frontend, mcp, etc.)
3. Before completion: Use \`verification-before-completion\``;

    parts.push(`<SKILLS_GUIDANCE>
${skillsInfo}
</SKILLS_GUIDANCE>`);

    return parts.join('\n\n');
  };

  return {
    'experimental.chat.system.transform': async (_input, output) => {
      const bootstrap = getBootstrapContent();
      if (bootstrap) {
        (output.system ||= []).push(bootstrap);
      }
    }
  };
};