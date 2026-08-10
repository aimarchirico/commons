---
name: plan
description:
  Draft a project's planning and system design artifacts under docs/plan/.
  Use when the user asks to plan, design, or scope a project, or to add a
  new requirement to an already-planned one.
argument-hint: "[--draft] [--auto] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                           |
| :------------- | :------- | :------------------------------------------------------------------------------------ |
| `--draft`      | No       | Create the resulting pull request as a draft.                                         |
| `--auto`       | No       | Skip approval steps in this skill and the `commit`/`pr` skills' own approval prompts. |
| `--skip-check` | No       | Skip the `commons:check` verification step before pushing.                            |

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

1. Identify the product concept from the user's prompt or context, asking
   for anything unclear. Draft `docs/plan/PRD.md` per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
1. Extract actionable requirements (from the PRD, or from the user's prompt
   directly when adding new requirements) and draft
   `docs/plan/requirements/index.md` and the individual
   `docs/plan/requirements/NNNN-slug.md` files per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
1. Present the Phase 1 files for approval, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed
   directly with the drafted files.

### Phase 2: System Design

1. For research on external systems, third-party integrations, or other
   technical unknowns feeding into the design, delegate per-system lookups
   to parallel `general-purpose` agents when substantial, so raw fetched
   documentation stays out of the main conversation and only distilled
   findings return. Log findings in `docs/plan/research/`, per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
1. Record architectural choices in `docs/plan/decisions/`, per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`.
1. Invoke the `commons:docs` skill, passing `--auto` through if it was
   provided, to draft the applicable system-level documentation directly in
   its final location (its own approval step surfaces normally unless
   `--auto` is set).
1. Draft `docs/plan/specifications/index.md` and the individual
   `docs/plan/specifications/NNNN-slug.md` files per
   `${CLAUDE_PLUGIN_ROOT}/skills/plan/REFERENCE.md`, each
   referencing the requirement(s) it fulfills.
1. Present the `research/`, `decisions/`, and `specifications/` files for
   approval, and wait for explicit user approval. Skip this step if the
   `--auto` flag is set, and proceed directly with the drafted files.
1. Write the approved files under `docs/plan/`.

### Handoff

1. Ask the user whether to commit, push, and open a pull request for the
   drafted files now, or leave them uncommitted for later. Skip this
   question if the `--auto` flag is set, and proceed directly with the rest
   of this phase. If the user declines, stop here: the files remain written
   under `docs/plan/` but uncommitted.
2. Determine `<branch-name>` following the naming rules in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md` (type `chore`, since
   there is no issue to key off yet; derive the description from the PRD's
   project name, or from the scoped requirement(s) when adding to an
   already-planned project), and resolve `<base-branch>` (the repository's
   default branch). Skip this step if already on a branch this skill
   created in an earlier, resumed run for the same plan; otherwise create
   and check out the branch:

   ```bash
   git fetch origin
   git checkout -b <branch-name> origin/<base-branch>
   ```

3. Invoke the `commons:commit` skill, passing `--auto` through if it was
   provided, to commit the files written under `docs/plan/` (and any files
   written by `commons:docs`) as logical units.
4. Unless `--skip-check` was set, invoke the `commons:check` skill. If it
   fails, fix the reported failures, commit the fix via `commons:commit`
   (passing `--auto` through if it was provided), and run `commons:check`
   once more. If it still fails after that one retry, stop retrying, and
   report the failure to the user instead of fabricating a pass.
5. Push commits and open the pull request:

   ```bash
   git push -u origin <branch-name>
   ```

   Next, invoke the `commons:pr` skill to open a pull request (its own
   title/body approval is the final review), passing `--base <base-branch>`
   if it differs from the default branch, along with `--draft` and
   `--auto` flags if provided by the user.
6. Ask the user whether to derive the initial issue backlog from
   `docs/plan/specifications/` now. If so, invoke the `commons:issue`
   skill, instructing it to make each resulting issue self-contained:
   include all the relevant information and concrete steps for all
   specifications so the issues stand on their own once created. Pass
   `--auto` through if it was provided.

## Output

The pull request number and URL reported by `commons:pr`, plus the issue(s)
created by `commons:issue` if that step ran, so a caller that invoked this
skill can act on both.
