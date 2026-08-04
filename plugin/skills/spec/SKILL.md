---
name: spec
description:
  Draft initial project specs (requirements, decisions, architecture) for a
  brand-new project before any issues exist. Use when the user asks to spec
  out, scope, or draft the initial design for a new project.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                                  |
| :------- | :------- | :----------------------------------------------------------- |
| `--auto` | No       | Skip the approval step and write the drafted files directly. |

## Workflow

1. Identify what's needed to draft the file set defined in
   `${CLAUDE_PLUGIN_ROOT}/skills/spec/REFERENCE.md`. Ask the user for
   anything not already clear from their prompt or context.
2. For research on external systems, third-party integrations, or technical
   unknowns feeding into `ARCHITECTURE.md`, `API.md`, or decisions, delegate
   per-system lookups to parallel `general-purpose` agents when substantial,
   so raw fetched documentation stays out of the main conversation and only
   distilled findings return. Keep requirement-gathering and drafting itself
   inline and conversational; do not delegate that part.
3. Draft the file set per `REFERENCE.md`, applying
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#documentation`'s
   applicability rules to decide whether `API.md` and `DESIGN.md` are
   included.
4. Present the drafted files for approval, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed
   directly with writing the drafted files.
5. Write the approved files under `docs/specs/`.
