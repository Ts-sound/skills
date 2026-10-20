/**
 * Skills plugin for OpenCode.ai (V2)
 *
 * Injects skills bootstrap context via the session `context` hook.
 * - Auto-activates caveman communication mode on session start
 * - Provides skills discovery/usage guidance
 */

import path from 'node:path';
import fs from 'node:fs';
import os from 'node:os';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const extractAndStripFrontmatter = (content) => {
  const match = content.match(/^---\n([\s\S]*?)\n---\n([\s\S]*)$/);
  if (!match) return { frontmatter: {}, content };

  const frontmatterStr = match[1];
  const body = match[2];
  const frontmatter = {};
  const lines = frontmatterStr.split('\n');

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];
    // Skip indented lines: they belong to a block scalar handled below.
    if (/^\s/.test(line)) continue;
    const colonIdx = line.indexOf(':');
    if (colonIdx <= 0) continue;

    const key = line.slice(0, colonIdx).trim();
    let value = line.slice(colonIdx + 1).trim();

    // YAML block scalar (`|` or `>`): fold the indented lines into one line.
    if (value === '|' || value === '>' || value === '|-' || value === '>-') {
      const block = [];
      let j = i + 1;
      while (j < lines.length && (/^\s+/.test(lines[j]) || lines[j].trim() === '')) {
        block.push(lines[j].trim());
        j++;
      }
      i = j - 1;
      value = block.join(' ').trim();
    }

    frontmatter[key] = value.replace(/^["']|["']$/g, '');
  }

  return { frontmatter, content: body };
};

// Discover skills from the local `skills/<category>/<skill>/SKILL.md` layout.
const scanSkills = (skillsDir) => {
  if (!fs.existsSync(skillsDir)) return [];

  return fs
    .readdirSync(skillsDir, { withFileTypes: true })
    .filter((entry) => entry.isDirectory())
    .map((category) => ({
      category: category.name,
      skills: fs
        .readdirSync(path.join(skillsDir, category.name), { withFileTypes: true })
        .filter((entry) => entry.isDirectory())
        .map((entry) => {
          const skillFile = path.join(skillsDir, category.name, entry.name, 'SKILL.md');
          if (!fs.existsSync(skillFile)) return null;
          const { frontmatter } = extractAndStripFrontmatter(fs.readFileSync(skillFile, 'utf8'));
          return {
            id: entry.name,
            name: frontmatter.name || entry.name,
            description: (frontmatter.description || '').replace(/\s+/g, ' ').trim(),
          };
        })
        .filter(Boolean)
        .sort((a, b) => a.id.localeCompare(b.id)),
    }))
    .filter((entry) => entry.skills.length > 0)
    .sort((a, b) => a.category.localeCompare(b.category));
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

const buildBootstrapContent = () => {
  const homeDir = os.homedir();
  const skillsRootDir = path.resolve(__dirname, '../..');
  const skillsDir = path.join(skillsRootDir, 'skills');
  const envConfigDir = normalizePath(process.env.OPENCODE_CONFIG_DIR, homeDir);
  const configDir = envConfigDir || path.join(homeDir, '.config/opencode');

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
  const categories = scanSkills(skillsDir);
  const total = categories.reduce((sum, entry) => sum + entry.skills.length, 0);

  const availableSkills =
    total === 0
      ? '_No skills found under the skills directory._'
      : categories
          .map((entry) => {
            const items = entry.skills
              .map((skill) => {
                const desc =
                  skill.description.length > 90
                    ? `${skill.description.slice(0, 87).trimEnd()}...`
                    : skill.description;
                return desc ? `  - \`${skill.id}\` — ${desc}` : `  - \`${skill.id}\``;
              })
              .join('\n');
            return `- **${entry.category}/**\n${items}`;
          })
          .join('\n');

  const skillsInfo = `**Skills Location:**
Your skills are installed at: \`${configDir}/skills/skills/\`
Source: \`${skillsDir}\`

**Available Skills (${total} from ${categories.length} categories, scanned from \`skills/\`):**
${availableSkills}

**Using Skills:**
Skills are auto-discovered by OpenCode. Load one by id with the native \`skill\` tool.

**Skill Workflow:**
1. Before any implementation: Use \`brainstorming\` or \`systematic-debugging\`
2. During coding: Use domain-specific skills (frontend, mcp, etc.)
3. Before completion: Use \`verification-before-completion\``;

  parts.push(`<SKILLS_GUIDANCE>
${skillsInfo}
</SKILLS_GUIDANCE>`);

  return parts.join('\n\n');
};

// `Plugin.define` from `@opencode/plugin` is an identity helper; exporting the
// plain definition keeps this file resolvable from symlinked installs too
// (e.g. ~/.config/opencode/plugins/skills.js -> this file).
export default {
  id: 'skills',
  async setup(ctx) {
    const bootstrap = buildBootstrapContent();

    await ctx.session.hook('context', (event) => {
      if (!bootstrap) return;
      const system = (event.system ||= []);
      const injected = system.some(
        (part) => typeof part?.text === 'string' && part.text.includes('<SKILLS_GUIDANCE>'),
      );
      if (injected) return;
      system.push({ type: 'text', text: bootstrap });
    });
  },
};
