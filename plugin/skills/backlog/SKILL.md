---
name: backlog
description:
  Chain spec drafting and issue creation into a single flow. Use when the
  user is starting a new project from scratch and wants the initial spec
  drafted and the full initial issue backlog created end-to-end.
argument-hint: "[--auto]"
---

## Arguments

| Flag     | Required | Description                                                              |
| :------- | :------- | :----------------------------------------------------------------------- |
| `--auto` | No       | Skip every sub-skill's approval step and run the full flow autonomously. |

## Workflow

1. Identify the description of the new project to spec out from the user's
   prompt or context. Ask the user for clarification if it's not already
   clear.
2. Invoke the `commons:spec` skill with the identified project description,
   passing `--auto` through if it was provided, to draft and write the file
   set under `docs/specs/` (its own approval step surfaces normally unless
   `--auto` is set).
3. Invoke the `commons:issue` skill with the initiatives in
   `docs/specs/requirements/`, plus supporting context from
   `docs/specs/decisions/`, `ARCHITECTURE.md`, and any conditional `API.md`
   or `DESIGN.md` written by `commons:spec`, as the work to turn into
   issues, one top-level Epic per initiative, passing `--auto` through if it
   was provided (its own hierarchy-approval step surfaces normally unless
   `--auto` is set).

## Output

The ids of the top-level issues `commons:issue` creates (one per
initiative), so a caller that invoked this skill can act on them.
