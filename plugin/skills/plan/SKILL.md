---
name: plan
description:
  Draft a design doc for work that carries design risk, and open it as a
  pull request so the design is reviewed before any issues are cut. Use
  when the user asks to plan, design, or scope a project or a significant
  change.
argument-hint: "[--draft] [--auto] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                                           |
| :------------- | :------- | :---------------------------------------------------------------------------------------------------- |
| `--draft`      | No       | Create the resulting pull request as a draft.                                                         |
| `--auto`       | No       | Skip approval steps in this skill and the `commons:commit`/`commons:pr` skills' own approval prompts. |
| `--skip-check` | No       | Skip the `commons:check` verification step before pushing.                                            |

## Workflow

### Warrant

1. Identify the work to be designed from the user's prompt or context,
   asking for anything unclear. Then establish whether it warrants a design
   doc at all, counting how many of these hold:

   - The right design approach is uncertain.
   - Getting the design wrong would be expensive to unwind.
   - The design is ambiguous or contentious.
   - It touches cross-cutting concerns (security, privacy, observability)
     that would otherwise be skipped.
   - High-level documentation of an existing or legacy system is needed.

   Fewer than three means the design is not ambiguous enough to be worth
   documenting. Report which ones do not hold, recommend the
   `commons:issue` skill instead, and stop.

2. Inspect `docs/design-docs/` for a doc already covering this work. If one
   exists and its system has not shipped, read it into context and amend it
   rather than starting a new doc, flagging any conflict with new input
   instead of silently overwriting. A doc whose system has shipped is never
   edited; design that changes it belongs in a new doc.

### Draft

1. Grill the user until **Context and Scope** and **Goals and Non-Goals**
   can be written. Establish what already exists and what genuinely
   constrains the work, then press hardest on non-goals: every capability
   left implicit is scope that expands later.
2. For research on external systems, third-party integrations, or other
   technical unknowns feeding into the design, delegate per-system lookups
   to parallel `general-purpose` agents when substantial, so raw fetched
   documentation stays out of the main conversation and only distilled
   findings return. Findings feed the design and its alternatives; they are
   never written up as their own artifact.
3. Draft the remaining sections, following the `docs/design-docs/` entry in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#documentation`. Target 1
   to 3 pages for a change to an existing system and 10 to 20 for a whole
   new one. Spend that length where the design is genuinely uncertain, and
   never on restating what the implementation will obviously do.
4. Present the drafted doc for approval, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed
   directly with the drafted doc.
5. Write the approved doc to `docs/design-docs/<slug>.md`, where `<slug>`
   names the system or change being designed.

### Handoff

1. Set up the branch per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#branch-setup`, using type
   `chore` (there is no issue to key off yet) and deriving the description
   from the doc's slug. This skill works in the current tree rather than a
   worktree, so check the branch out directly:

   ```bash
   git checkout -b <branch-name> origin/<base-branch>
   ```

2. Invoke the `commons:commit` skill, passing `--auto` through if it was
   provided, to commit the drafted doc.
3. Unless `--skip-check` was set, verify per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#verification`.
4. Open the pull request per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#opening-the-pull-request`.

This skill creates no issues. Decomposition happens through the
`commons:issue` skill once the pull request has merged, so the design is
agreed before any work is committed to the tracker, and the issues it
creates stand on their own rather than referencing the doc.

## Output

The path of the drafted design doc, plus the pull request number and URL
reported by `commons:pr`, so a caller that invoked this skill can act on
both.
