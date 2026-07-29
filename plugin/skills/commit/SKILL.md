---
name: commit
description:
  Analyze unstaged changes and create logical, atomic git commits. Use when
  the user explicitly asks to commit unstaged changes, analyze git diffs for
  committing, or run the commit skill.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                                  |
| :------- | :------- | :----------------------------------------------------------- |
| `--auto` | No       | Skip the approval step and commit the drafted plan directly. |

## Workflow

1. Execute `git status` and `git diff` to analyze all unstaged changes
   (including untracked files).
2. If there are no changes to commit, notify the user and exit.
3. Group the changes into logical, atomic units and draft a commit message for
   each group strictly following the rules in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#commits`.
4. Present the proposed commit plan, and wait for explicit user approval. Skip
   this step if the `--auto` flag is set, and proceed directly with the
   drafted plan.
5. For each approved unit, execute `git add` for those specific files followed
   by `git commit -m` with the approved message.
