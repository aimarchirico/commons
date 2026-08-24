---
name: plan
description:
  Draft a design document for work that carries design risk, and open it as
  a pull request so the design is reviewed before any issues are cut. Use
  when the user asks to plan, design, or scope a project or a significant
  change.
argument-hint: "[--draft] [--auto] [--skip-check] [--no-pr]"
---

## Arguments

| Flag           | Required | Description                                                                                                                                                  |
| :------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--draft`      | No       | Create the resulting pull request as a draft.                                                                                                                |
| `--auto`       | No       | Ask the user nothing: skip the approval steps in this skill and the `commons:pr` skill's own approval prompt, drafting from context alone.                   |
| `--skip-check` | No       | Skip the `commons:check` verification step before pushing.                                                                                                   |
| `--no-pr`      | No       | Stop once the document is committed, reporting the branch and worktree instead of opening a pull request, for a caller that lands the design in a later one. |

## Workflow

### Scope

1. Identify the work to be designed from the user's prompt or context,
   asking for anything unclear. Under `--auto`, derive it from context
   instead of asking.
1. Inspect `docs/design-docs/` and decide, per the entry for it in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#documentation`, whether
   this work amends an existing document or starts a new one. When amending,
   read the document into context first and flag any conflict with new input
   instead of silently overwriting.
1. If the work carries more decisions than one review can settle, split it
   into a sub-problem per document and draft them all, including any whose
   design rests on another's.

### Draft

1. Grill the user until *Context and Scope* and *Goals and Non-Goals* can be
   written. Establish what already exists and what constrains the work, then
   press hardest on non-goals: every capability left implicit is scope that
   expands later. Under `--auto`, ask nothing: derive both sections from the
   codebase and the user's description, and state every assumption standing
   in for an unanswered question in *Context and Scope*.
1. For research on external systems, third-party integrations, or other
   technical unknowns feeding into the design, delegate per-system lookups
   to parallel `general-purpose` agents when substantial, so raw fetched
   documentation stays out of the main conversation and only distilled
   findings return, never written up as their own artifact.
1. Draft the remaining sections of each document. Spend length on what is
   genuinely uncertain, never on restating what the implementation will
   obviously do. Where one document's design rests on another's, link to it
   for context instead of restating the design it carries.
1. Present every drafted document for approval, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed
   directly with the drafted documents.

### Handoff

1. Set up the branch per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#branch-setup`, using type
   `chore` (there is no issue to key off yet) and deriving the description
   from the document's slug, or from the work the set of them covers when
   there are several. Then create the branch and its worktree per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#worktrees`.
1. Delegate to the `worktree-runner` agent, passing every approved document
   verbatim, each one's target path `docs/design-docs/<slug>.md` where
   `<slug>` names the system or change it designs, `<worktree-path>`, and
   whether `--skip-check` was set. Documents are written as approved, never
   reworded (it invokes `commons:commit` and `commons:docs` itself as it
   goes, committing one document at a time).
1. If `--no-pr` was set, stop here, leaving the branch and its worktree in
   place for the caller to build on. Nothing is pushed, since
   `commons:pr` owns pushing.
1. Open the pull request per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#opening-the-pull-request`.
1. Remove the isolated worktree per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#worktrees`.

## Output

The path of every drafted design document, plus the pull request number and
URL reported by `commons:pr`, so a caller that invoked this skill can act on
both. Under `--no-pr`, the branch name and worktree path instead of the pull
request.
