---
name: ship
description:
  Chain issue creation and solving into a single flow. Use when the user
  describes work to do and wants it turned into an issue and implemented
  end-to-end.
argument-hint: "[--draft] [--auto] [--review]"
---

## Arguments

| Flag       | Required | Description                                                                                       |
| :--------- | :------- | :--------------------------------------------------------------------------------------------------- |
| `--draft`  | No       | Passed through to the `solve` skill (and its `pr` skill) to open the resulting PR as a draft.       |
| `--auto`   | No       | Skip all approval checkpoints across every sub-skill invoked, including an `--review` pass if set, running the full lifecycle autonomously. |
| `--review` | No       | After the pull request is opened, run one review-and-fix pass over it via the `review` and `resolve` skills. |

## Workflow

1. Identify the description of work to ship from the user's prompt or
   context. Ask the user for clarification if it's not already clear.
2. Invoke the `commons:issue` skill with the identified work, passing
   `--auto` through if it was provided, to draft and create the issue
   hierarchy (its own hierarchy-approval step surfaces normally unless
   `--auto` is set).
3. Capture the top-level issue id created by `commons:issue` (the id of the
   root item in the created hierarchy).
4. Invoke the `commons:solve` skill with `--issue <issue-id>`, passing
   `--auto` and `--draft` through if they were provided, to implement the
   issue end-to-end and open a pull request (its own plan-approval and the
   `commons:pr` approval steps surface normally unless `--auto` is set).
5. If `--review` was not provided, stop here. Otherwise, capture the pull
   request number that `commons:pr` reported creating (surfaced through
   `commons:solve`).
6. Invoke the `commons:review` skill with `--pr <pr-number>`, passing
   `--auto` through if it was provided, to get findings on the opened pull
   request and, on approval (or automatically under `--auto`), post them as
   PR review comments.
7. If `commons:review` posted any findings, invoke the `commons:resolve`
   skill with `--pr <pr-number>`, passing `--auto` through if it was
   provided, to fix them and reply on the pull request. Run at most this
   one review-and-fix pass; do not re-invoke `commons:review` afterward.
