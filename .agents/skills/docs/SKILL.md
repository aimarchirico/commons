---
description: Update project documentation
metadata:
  github-path: skills/docs
  github-ref: refs/tags/commons-docs-v1.2.0
  github-repo: https://github.com/aimarchirico/commons
  github-tree-sha: b7ba286febc5c669071f1d1409bfa06ad9120ca2
name: docs
---

## When to Use

Use when the user asks to update project documentation.

## Execution Steps

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root. If it
   is missing, run `npx @aimarchirico/commons-docs materialize-templates` to materialize the
   documentation.
2. Identify the details and context of the documentation changes. If these
   details are not already clear from the user's prompt or context, inspect the
   codebase, recent commits, and `git diff` and ask the user for clarification
   if needed.
3. Present proposed updates strictly following the structure and conventions
   defined in `CONTRIBUTING.md#documentation`, and wait for explicit user
   approval.
4. Apply the edits.
