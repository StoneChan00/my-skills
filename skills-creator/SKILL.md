---
name: skills-creator
description: >
  Generate high-quality SKILL.md files for OpenCode / Claude Code / OhMyOpenAgent agents,
  following official OpenCode spec and Anthropic's skill-writing best practices.
  Use when asked to "create a skill", "write a SKILL.md", "author a new skill",
  or when you need to scaffold a reusable agent instruction set from a prompt/idea.
  Not for: writing MCP tool descriptions (use a dedicated mcp-writer / description-standard skill),
  editing existing skills incrementally (just edit directly), or project-specific AGENTS.md / rules files.
  Output: a ready-to-drop SKILL.md + directory scaffold, with frontmatter validated against OpenCode naming rules.
---

# Skills Creator

Author well-formed, agent-usable skills (SKILL.md) for OpenCode and Claude-compatible agents.

## What a "skill" is (mental model)

A skill = a **folder containing SKILL.md** (plus optional refs/assets/scripts).
Agents discover it by `name` + `description`; they load the full content on demand via the
built-in `skill` tool. The description is a **routing signal**, not a summary — it decides
whether the agent will ever see your work.

## The Iron Rules (before writing anything)

1. **Description = routing signal.** If it's vague, the skill never gets loaded.
   Use the three-piece form: `Use when X / Not for Y / Output: Z`.
2. **Name must be directory-safe and unique.** Regex: `^[a-z0-9]+(-[a-z0-9]+)*$`, 1–64 chars,
   and must match the folder name holding `SKILL.md`.
3. **Gotchas are the most valuable content.** They are the mistakes *humans have made*.
   Every skill must have a `Common Mistakes` / `Gotchas` section.
4. **Don't surprise.** The skill's behavior must not exceed what the description promises.
   Any side effect (writes a file, sends a message, commits code) must appear in the description.
5. **Progressive disclosure.** SKILL.md body ≤ 150 lines. Move reference tables, templates,
   scripts into `refs/`, `assets/`, `scripts/` subdirectories — agents read them on demand.
6. **Show examples twice.** Put ≥ 2 positive + ≥ 2 negative + 1 gray-zone examples —
   once in the description sentence, once in the body. A "Not for" without both = fuzzy boundary.

## Official Frontmatter Spec (OpenCode)

```yaml
---
name: my-skill-name          # required, 1-64 chars, lowercase + single hyphens
description: >               # required, 1-1024 chars
  Use when ...
  Not for ...
  Output: ...
license: MIT                 # optional
compatibility: opencode      # optional
metadata:                    # optional, string→string map
  audience: developers
  workflow: on-demand
---
```

Unknown fields are ignored. `name` + `description` are the only mandatory ones.

## Where to place the skill

OpenCode scans both project-local and global paths:

| Scope | Paths (each checked) |
|-------|----------------------|
| Project | `.opencode/skills/<name>/SKILL.md` · `.claude/skills/<name>/SKILL.md` · `.agents/skills/<name>/SKILL.md` |
| Global  | `~/.config/opencode/skills/<name>/SKILL.md` · `~/.claude/skills/<name>/SKILL.md` · `~/.agents/skills/<name>/SKILL.md` |

Project-local discovery walks up from CWD until the git worktree root.

## Recommended directory layout

```
<skill-name>/
├── SKILL.md              # Required. Frontmatter + body.
├── refs/                 # Long-form reference (API tables, standards, glossaries)
├── assets/               # Templates, JSON schemas, copyable snippets
└── scripts/              # Runnable helpers the skill instructs agents to invoke
```

## Body template (start from this, adapt)

```markdown
# <Skill Title>

## Overview (1–2 sentences)
What the skill does and why it exists.

## When to use / not to use
- Use when: [2+ concrete triggers with user-phrase examples]
- Not for: [2+ concrete anti-triggers]
- Gray zone: [1 edge case with guidance]

## Quick Reference
Table or bullet list the agent can scan (no narrative).

## Workflow / Steps
Numbered steps. Each step says: input → action → output → next.

## Common Mistakes
| Mistake | Effect | Fix |
|---------|--------|-----|
| ...     | ...    | ... |

## Related skills (disambiguation)
- vs `foo-skill`: [one-line difference that prevents mis-routing]
- vs `bar-skill`: ...

## Next step
What skill/flow takes over after this one completes.
```

## Generation checklist

- [ ] `name` matches folder name and the regex
- [ ] `description` uses "Use when / Not for / Output" three-piece form
- [ ] Frontmatter has no unknown fields (only: name, description, license, compatibility, metadata)
- [ ] Body has `Common Mistakes` / `Gotchas` section — with real mistakes, not generic platitudes
- [ ] Body has ≥ 2 positive / ≥ 2 negative / ≥ 1 gray example
- [ ] Body is ≤ 150 lines; heavy material moved to `refs/`
- [ ] Side effects (if any) are declared in description
- [ ] Related similar skills are disambiguated
- [ ] Examples appear both in description and body where relevant

## Common Mistakes

| Mistake | Effect | Fix |
|---------|--------|-----|
| Description summarizes the skill ("This skill helps with X…") | Agent never loads SKILL.md → skill is dead | Rewrite as trigger: "Use when user asks X, mentions Y, sees Z error" |
| `name` has uppercase / underscores / leading `-` | OpenCode rejects the skill on load | Match `^[a-z0-9]+(-[a-z0-9]+)*$` |
| `name` differs from folder name | Skill silently never discovered | Rename folder OR frontmatter to match |
| Body > 200 lines with inline reference tables | Wastes context window on every load | Move tables to `refs/`, reference from body |
| No `Not for` in description | Mis-routed to wrong queries | Add 2+ anti-trigger phrases |
| GOTCHAs section is empty or copied from docs | Real-world mistakes not captured → repeated failures | Fill with mistakes actually observed; iterate after each failure |
| Declaring side effects only in body (not description) | Agent surprises user with writes/sends | Move to description's "Output:" clause |
| Creating skill inside project but only using it globally | Discovery won't find it if agent works outside CWD | Put in `~/.config/opencode/skills/` or project root's skill dir |
| Using emoji or marketing language in description | Adds noise, dilutes routing signal | Use terse, imperative phrases |

## Disambiguation

- vs an **MCP tool description** writer: this skill produces SKILL.md *files* (agent instructions),
  not tool-level schemas (inputSchema/output).
- vs **AGENTS.md / rules files**: this skill produces per-topic reusable skills,
  not project-wide persona/rule docs.
- vs **writing-skills (cat-cafe internal)**: this is the generic, framework-agnostic version —
  no pnpm / manifest.yaml / cat-cafe-specific tooling assumed.

## Next steps after generating

1. Drop the folder into one of the recognized paths above.
2. If using OpenCode with skills permission gating, add the new name to `opencode.json`:
   ```json
   { "permission": { "skill": { "<new-skill-name>": "allow" } } }
   ```
3. Verify discovery: ask the agent "list available skills" — the new name should appear in `<available_skills>`.
4. Smoke-test by triggering the skill with a typical prompt; confirm it loads and behavior matches description.
5. Iterate: after the first real failure, add the mistake to `Common Mistakes` and (if systemic)
   update the description's boundary clauses.

## References (read-only)

- OpenCode official spec: <https://opencode.ai/docs/skills/>
- Anthropic skill-writing principles (progressive disclosure, examples-twice, routing-description):
  see `references/anthropic-principles.md` in this folder.
