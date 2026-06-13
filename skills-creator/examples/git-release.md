# Example: `git-release` skill

A complete, minimal skill demonstrating canonical structure.

## SKILL.md

````markdown
---
name: git-release
description: >
  Create a tagged GitHub release with a consistent changelog from merged PRs.
  Use when asked to "cut a release", "publish v1.2.3", or "write release notes".
  Not for: drafting PRs (use pr-draft), writing commit messages (use commit),
  or bumping version in package files manually.
  Output: a ready-to-paste `gh release create` command + rendered changelog.
license: MIT
compatibility: opencode
metadata:
  audience: maintainers
  workflow: on-demand
---

# git-release

## Overview
Produce versioned releases with human-readable changelogs derived from
merged PRs since the last tag.

## When to use
- "cut a release"
- "publish v1.2.3"
- "draft release notes"

## When NOT to use
- Writing a PR description (use `pr-draft`)
- Writing a commit message (use `commit-conventional`)
- Manually editing CHANGELOG.md without gh-cli

## Workflow
1. `git describe --tags --abbrev=0` → get previous tag
2. `gh pr list --state merged --search "merged:>=$(prev-tag-date)"`
3. Group PRs by label (`feature`, `fix`, `breaking`, `docs`)
4. Propose next version per labels (feat-minor / fix-patch / breaking-major)
5. Ask user to confirm version if ambiguous
6. Output:
   - Changelog in bullet form
   - `gh release create vX.Y.Z --notes='...'` command

## Common Mistakes

| Mistake | Effect | Fix |
|---------|--------|-----|
| Forgetting to `git fetch --tags` first | Previous tag missed → changelog includes old PRs | Fetch before `describe` |
| Using PR title verbatim as changelog entry | Leaks internal jargon ("refactor foo") into public changelog | Summarize user-facing impact |
| Not asking user to confirm version bump | Auto-bumping past a breaking change | Prompt for confirmation on any major bump |

## Related skills
- `commit-conventional` — message writing, not release writing
- `pr-draft` — PR description, not public changelog

## Next step
After release is created → `release-announcements` (if registered).
````

## Why this example is good

- Name matches folder name; hyphen-case.
- Description uses all three pieces (Use when / Not for / Output).
- Body has GOTCHAs with real fixes, not boilerplate.
- Workflow is numbered with concrete commands.
- "Related skills" disambiguates from the obvious near-misses.
- Under ~50 lines of body — easy on context.
