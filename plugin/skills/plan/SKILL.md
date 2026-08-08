---
name: plan
description:
  Draft a project's planning and system design artifacts under docs/plan/.
  Use when the user asks to plan, design, or scope a project, or to add a
  new requirement to an already-planned one.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                           |
| :------- | :------- | :---------------------------------------------------- |
| `--auto` | No       | Skip approval steps and write drafted files directly. |

## Workflow

### Resume

1. Inspect `docs/plan/` for existing files to determine where to resume, and
   read whatever is found into context to treat as the current draft rather
   than a blank slate; flag any conflict between it and new input instead of
   silently overwriting:

   - No `PRD.md`: this is a new plan. Start at **Phase 1**.
   - `PRD.md` exists, but the user is introducing one or more new
     requirements to an already-planned project: skip step 2 (`PRD.md` is
     written once and never revisited) and start at step 3, scoped to just
     those requirements.
   - `PRD.md` exists and `requirements/` is drafted, but `decisions/`,
     `research/`, or `specifications/` are missing or incomplete: **Phase 1**
     is done, resume at **Phase 2**.
   - Everything through `specifications/` already exists for the
     requirement(s) in scope: both phases are done, skip straight to
     **Handoff**.

### Phase 1: Planning

2. Identify the product concept from the user's prompt or context, asking
   for anything unclear. Draft `docs/plan/PRD.md` per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
3. Extract actionable requirements (from the PRD, or from the user's prompt
   directly when adding new requirements) and draft
   `docs/plan/requirements/index.md` and the individual
   `docs/plan/requirements/NNNN-slug.md` files per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
4. Present the Phase 1 files for approval, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed
   directly with the drafted files.

### Phase 2: System Design

5. For research on external systems, third-party integrations, or other
   technical unknowns feeding into the design, delegate per-system lookups
   to parallel `general-purpose` agents when substantial, so raw fetched
   documentation stays out of the main conversation and only distilled
   findings return. Log findings in `docs/plan/research/`, per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
6. Record architectural choices in `docs/plan/decisions/`, per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
7. Invoke the `commons:docs` skill, passing `--auto` through if it was
   provided, to draft the applicable system-level documentation directly in
   its final location (its own approval step surfaces normally unless
   `--auto` is set).
8. Draft `docs/plan/specifications/index.md` and the individual
   `docs/plan/specifications/NNNN-slug.md` files per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`, each
   referencing the requirement(s) it fulfills.
9. Present the `research/`, `decisions/`, and `specifications/` files for
   approval, and wait for explicit user approval. Skip this step if the
   `--auto` flag is set, and proceed directly with the drafted files.
10. Write the approved files under `docs/plan/`.

### Handoff

11. Ask the user whether to derive the initial issue backlog from
    `docs/plan/specifications/` now. If so, invoke the `commons:issue`
    skill scoped to that content, passing `--auto` through if it was
    provided.