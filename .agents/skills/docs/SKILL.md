---
description: Update project documentation
metadata:
    github-path: skills/docs
    github-ref: refs/heads/main
    github-repo: https://github.com/aimarchirico/core
    github-tree-sha: e2d9a0a88ce9657e0e291540afbfe84c8a0852db
name: docs
---
## When to Use

Use when the user asks to update project documentation.

## Execution Steps

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root. If it is missing, run `npx @aimarchirico/core-docs` to materialize the documentation.
2. Identify the details and context of the documentation changes. If these details are not already clear from the user's prompt or context, inspect the codebase, recent commits, and `git diff` and ask the user for clarification if needed.
3. Present proposed updates strictly following the structure and conventions defined in `CONTRIBUTING.md#documentation`, and wait for explicit user approval.
4. Apply the edits.
