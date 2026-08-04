---
name: spec
description:
  Draft initial project specs (requirements, architecture, decisions) for a
  brand-new project before any issues exist. Use when the user asks to spec
  out, scope, or draft the initial design for a new project.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                                  |
| :------- | :------- | :----------------------------------------------------------- |
| `--auto` | No       | Skip the approval step and write the drafted files directly. |

## Workflow

1. Identify the problem, goals, non-goals, target users, and scope of the new
   project. If these details are not already clear from the user's prompt or
   context, ask the user for clarification.
2. For research on external systems, third-party integrations, or technical
   unknowns feeding into `ARCHITECTURE.md`, `API.md`, or decisions, delegate
   per-system lookups to parallel `general-purpose` agents when substantial,
   so raw fetched documentation stays out of the main conversation and only
   distilled findings return. Keep requirement-gathering and drafting itself
   inline and conversational; do not delegate that part.
3. Draft the file set defined in
   `${CLAUDE_PLUGIN_ROOT}/skills/spec/REFERENCE.md`, applying
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#documentation`'s
   applicability rules to decide whether `API.md` and `DESIGN.md` are
   included.
4. Present the drafted files for approval, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed
   directly with writing the drafted files.
5. Write the approved files under `docs/specs/`.

## Out of Scope

The root `README.md` and module READMEs are out of scope for this skill —
those belong to the `docs` skill once an implementation exists to document.
