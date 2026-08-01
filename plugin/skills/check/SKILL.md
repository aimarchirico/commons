---
name: check
description:
  Verify the working tree against this project's own PR-gating CI checks.
  Use before committing, opening a PR, or as a pre-flight in other skills.
argument-hint: "[--path <dir>]"
---

## Arguments

| Flag     | Required | Description                                          |
| :------- | :------- | :--------------------------------------------------- |
| `--path` | No       | Restrict to this directory instead of the repo root. |

## Workflow

1. Scope to `--path` if given, otherwise the repo root plus whichever
   top-level directories `git diff --name-only` against the default
   branch touched.
2. Find the CI workflows that trigger on pull requests and extract their
   actual verification commands (lint/typecheck/build/test), skipping
   runner-setup steps (checkout, toolchain install). Respect each
   workflow's `paths:` filters against the directories in scope.
3. Run the extracted commands locally, in parallel where independent.
4. If no PR-triggering workflow exists, report that rather than guessing
   a check.

## Output

Pass/fail per directory, plus full output of any failing check.
