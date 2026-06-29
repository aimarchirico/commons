---
name: commit
description: Analyze unstaged changes and create logical, atomic git commits
---

## When to Use

Use when the user explicitly asks to commit unstaged changes, analyze git diffs for committing, or run the commit skill.

## Execution Steps

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root. If it is missing, run `npx @aimarchirico/core-docs` to materialize the documentation.
2. Execute `git status` and `git diff` to analyze all unstaged changes (including untracked files).
3. If there are no changes to commit, notify the user and exit.
4. Group the changes into logical, atomic units and draft a commit message for each group strictly following the rules in `CONTRIBUTING.md#commits`.
5. Present the proposed commit plan, and wait for explicit user approval.
6. For each approved unit, execute `git add` for those specific files followed by `git commit -m` with the approved message.
