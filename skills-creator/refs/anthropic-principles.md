# Anthropic Skill-Writing Principles (Condensed)

Distilled from the Anthropic "Building effective agents" series and
the canonical "9 skill categories" taxonomy. Referenced by SKILL.md's Iron Rules.

## 1. Description is a routing signal, not an abstract

Agents use a three-layer loading model:
1. **Always-visible layer** — `name + description` (in system prompt).
2. **Loaded layer** — SKILL.md body, pulled in only if agent judges it relevant.
3. **On-demand layer** — `refs/`, `assets/`, `scripts/`, read via nested tool calls.

> If the description fails the routing test, the body is never seen.
> "The skill in the top drawer nobody opens."

### Three-piece form (mandatory)

```
Use when [user intent + trigger phrases + keywords].
Not for [anti-intents + near-misses].
Output: [concrete deliverable the agent produces].
```

All three are required. Omitting "Not for" creates a fuzzy boundary →
agent mis-routes to it when a different skill was appropriate.

## 2. Gotchas are the highest-value content

The most valuable section of any skill is `Common Mistakes` / `Gotchas`.
Not a copy-paste from docs — real mistakes humans actually made, with
concrete consequences and fixes.

**Iterate after every failure.** The skill is never "done"; every new
mistake is a new row in the Gotchas table.

## 3. Don't surprise

A skill's runtime behavior must not exceed the scope its description promises.
Any side effect — file writes, network calls, commits, messages to other agents —
must be declared in the description's `Output:` clause.

Agents (and users) must be able to predict consequences from the description alone.

## 4. Examples appear twice

Fuzzy boundaries cause mis-routing. Each skill needs:

- ≥ 2 positive examples (when to use)
- ≥ 2 negative examples (when NOT to use)
- ≥ 1 gray zone (edge case + guidance)

Each example must appear in **both** the description sentence AND the body.
"Only in description" or "only in body" = half the defense.

## 5. Skill is a folder, not just a file

Use file system for progressive disclosure:

| Content kind | Put here | Why |
|--------------|----------|-----|
| Core flow / rules / GOTCHAs | `SKILL.md` body | Loaded first |
| Long reference tables | `refs/foo.md` | Loaded only if agent needs it |
| Copyable templates | `assets/foo.md` | Copy-pasted by agent |
| Runnable helpers | `scripts/foo.sh` | Invoked by agent |

**Body budget: ≤ 150 lines.** Exceed this = over token budget per load.

## 6. The 9 canonical skill categories (Anthropic)

Use to classify what kind of skill you're writing — this shapes structure.

| Category | Example |
|----------|---------|
| Library / API Reference | SDK usage skill |
| Product Verification | Quality gate, smoke-test skill |
| Business Process & Team Automation | Feature lifecycle skill |
| Code Quality & Review | Code review checklist |
| Code Scaffolding & Templates | Project scaffolding skill |
| Runbooks | Debugging / incident response |
| CI/CD & Deployment | Release / merge skill |
| Documentation | Style guide skill |
| Workflow / Orchestration | Multi-agent handoff skill |

## 7. Description length

Anthropic/OpenCode hard cap: **1–1024 characters**.

Practical sweet spot: **200–500 characters**.
Too short = routing fails. Too long = noise dilutes signal.

## 8. Naming conventions

- Hyphen-case: `git-release`, not `GitRelease` or `git_release`.
- Verb-led when the skill performs an action: `create-release`, `review-pr`.
- Noun-led when the skill is a reference: `python-idioms`, `sql-patterns`.
- Avoid marketing words: `ultimate-`, `super-`, `amazing-`.

## 9. Anti-patterns that kill a skill

- Description as marketing copy ("The ultimate tool for X…")
- Body that re-documents the library instead of teaching when to use it
- GOTCHAs section that just quotes official docs
- Single-example "Use when" with no "Not for"
- 500-line body with inline API tables — never uses `refs/`
- Side effects only in body ("Oh, and this skill will push to main")
- Name that doesn't match the folder → silent undiscoverability
