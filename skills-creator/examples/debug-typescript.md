# Example: `debug-typescript` skill (gray-zone-heavy)

A skill whose value lives in its boundary definitions — useful when
the agent must distinguish "debug TS" from "debug Jest" from "debug Node runtime".

## SKILL.md

````markdown
---
name: debug-typescript
description: >
  Diagnose TypeScript compilation errors (tsc, ts-node, vite/esbuild) and type-level puzzles.
  Use when: TS2xxx/TS1xxx error codes, "type is not assignable", generic constraint confusion,
  declaration file issues, path-mapping failures, tsconfig-related errors.
  Not for: Jest runtime failures (use debug-jest), Node runtime crashes without TS involvement
  (use debug-node), React hydration issues (use debug-react), or pure ESM/CJS
  resolution (use fix-module-resolution).
  Output: root cause + minimal type-preserving fix + explanation of why it failed.
---

# debug-typescript

## Overview
Diagnose and fix TypeScript-level errors with root-cause explanation.

## When to use
- `tsc` errors (TS2xxx, TS4xxx, TS5xxx codes)
- `ts-node` won't start
- Vite / esbuild complaining about type-only imports
- `.d.ts` declaration files missing or stale
- `tsconfig.json` path mapping not resolving
- "Type 'X' is not assignable to type 'Y'" confusion

## When NOT to use
- Jest fails at runtime with `Cannot find module './x.ts'` → `debug-jest`
- Node process crashes with `ERR_REQUIRE_ESM` → `fix-module-resolution`
- React hydration mismatches → `debug-react`
- Runtime exception from `undefined.X.Y` after successful compile → `debug-javascript`

## Gray zone
- **`tsx` fails to execute a file.** First check if it's a TS compile error
  (this skill) or a Node runtime error after compile (use `debug-node`).
  Run `tsc --noEmit` — if it passes, this is not a TS skill problem.

## Workflow
1. Copy the full error text, not just the first line
2. Identify the TS error code → look up in `refs/ts-errors.md`
3. Check tsconfig (strict, paths, module resolution)
4. Find the minimal type-preserving fix (never `as any` or `@ts-ignore`)
5. Explain WHY TypeScript rejected it in ≤ 3 sentences

## Common Mistakes

| Mistake | Effect | Fix |
|---------|--------|-----|
| "Fixing" with `as any` | Silences the error permanently; real bug may lurk | Add proper type annotation at usage site |
| Ignoring error code, only reading message | Misses subtle issues like `noUncheckedIndexedAccess` | Always decode the TS code number |
| Editing `.d.ts` files in `node_modules` | Breaks on next `npm install` | Add overrides via `paths` in tsconfig or `patch-package` |
| Assuming `strict: false` is the solution | Hides type errors that will bite downstream | Keep strict on; fix the real type issue |

## Related skills
- `debug-jest`: test runtime, not TS compile
- `debug-node`: pure Node runtime
- `debug-react`: React lifecycle, not type-level
- `fix-module-resolution`: ESM/CJS, not TS

## Next step
After TS is clean → `lint-eslint` for stylistic passes.
````

## Why this example is interesting

This skill's real value is the **gray zone** and the **Not-for disambiguation**.
Most debugging skills overlap; a skill that doesn't draw crisp lines
will be mis-routed constantly. Note the "Gray zone" section — it's an
explicit decision tree for the ambiguous case.
