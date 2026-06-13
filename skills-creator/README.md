# skills-creator

Generates well-formed SKILL.md files for OpenCode / Claude Code / OhMyOpenAgent agents.

## Why

Writing a good skill is harder than it looks. The description must route correctly,
the body must respect context-window budget, and the folder must be discoverable.
This skill encodes the full OpenCode spec + Anthropic's skill-writing principles
into a repeatable generation flow.

## What's inside

```
skills-creator/
├── SKILL.md                          # The skill itself — loads via `skill({name:"skills-creator"})`
├── README.md                         # You are here
├── refs/
│   └── anthropic-principles.md       # Anthropic skill-writing canon (condensed)
└── examples/
    ├── git-release.md                # Minimal canonical example
    └── debug-typescript.md           # Boundary-heavy example (gray zones)
```

## How to install

### Option A: per-project

Copy this folder into your project root:

```bash
cp -r skills-creator  <project-root>/.opencode/skills/
# or
cp -r skills-creator  <project-root>/.claude/skills/
```

### Option B: global (all projects)

```bash
# OpenCode
cp -r skills-creator  ~/.config/opencode/skills/
# or Claude Code compatible
cp -r skills-creator  ~/.claude/skills/
# or generic agent path
cp -r skills-creator  ~/.agents/skills/
```

### Name must match the folder

OpenCode requires `name` in frontmatter to **exactly equal** the containing
folder name (`skills-creator`). Do not rename the folder without also
editing `name:` in SKILL.md.

## How to use

Ask the agent:

> "Create a skill called `foo-bar` that helps with X when Y happens."

The agent will load this skill, follow the generation checklist,
and produce a scaffold — directory + SKILL.md — you can drop into
any of the recognized paths.

## Spec compliance

- OpenCode official SKILL.md spec: <https://opencode.ai/docs/skills/>
- Description form: `Use when / Not for / Output` (three-piece, mandatory)
- Naming regex: `^[a-z0-9]+(-[a-z0-9]+)*$`
- Body budget: ≤ 150 lines (progressive disclosure via `refs/`, `examples/`)

## Contributing

If you find a new real-world mistake that should be in `Common Mistakes`,
open a PR appending it. The GOTCHAs table is a living record, not a
one-time artifact.

License: MIT
