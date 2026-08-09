---
name: docs
description:
  Update or create project documentation. Use when the user asks to update
  project documentation.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                                     |
| :------- | :------- | :-------------------------------------------------------------- |
| `--auto` | No       | Skip the approval step and apply the proposed updates directly. |

## Workflow

1. Identify the details and context of the documentation changes. If the
   caller already supplied the content and context, use
   that directly. Otherwise, if these details are not already clear from the
   user's prompt or context, inspect the codebase, recent commits, and
   `git diff`, and ask the user for clarification if needed.
1. Present proposed updates strictly following the structure and conventions
   defined in `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#documentation`,
   and wait for explicit user approval. Skip this step if the `--auto` flag is
   set, and proceed directly with the proposed updates.
1. Apply the edits.
