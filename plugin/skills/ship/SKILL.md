---
name: ship
description:
  Chain design, issue creation, and solving into a single flow. Use when
  the user describes work to do and wants it designed if needed, turned into
  issues, and implemented end-to-end.
argument-hint: "[--draft] [--auto] [--review] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                                                                                                     |
| :------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `--draft`      | No       | Passed through to the `commons:plan` and `commons:solve` skills (and their `commons:pr` skill) to open the resulting PRs as drafts.                             |
| `--auto`       | No       | Run the full lifecycle autonomously without prompting for approvals across every sub-skill invoked (including during a `--review` pass if set).                 |
| `--review`     | No       | After the pull request is opened, run one review-and-fix pass over it via the `commons:review` and `commons:resolve` skills.                                    |
| `--skip-check` | No       | Passed through to the `commons:plan` and `commons:solve` skills, and to `commons:resolve` during a `--review` pass if set, to skip their `commons:check` steps. |

## Workflow

1. Identify the description of work to ship from the user's prompt or
   context. Ask the user for clarification if it's not already clear.
2. Establish whether that work warrants a design document, against the
   criteria in the `docs/design-docs/` entry in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#documentation`. When they
   hold, continue to step 3. When they do not, report which ones fail and ask
   whether to design it anyway: continue to step 3 if the user confirms, and
   skip to step 4 otherwise. Under `--auto` that question goes unasked and
   its answer is taken as no, which skips the design only where it was
   already unwarranted.
3. Invoke the `commons:plan` skill with `--no-pr`, passing `--auto` and
   `--skip-check` through if they were provided, and capture the branch name
   it reports.
4. Invoke the `commons:issue` skill with the approved design documents when
   step 3 produced any, and the identified work otherwise, passing `--auto`
   through if it was provided, to draft and create the issue hierarchy (its
   own hierarchy-approval step surfaces normally unless `--auto` is set).
5. Capture the top-level issue id created by `commons:issue` (the id of the
   root item in the created hierarchy).
6. Invoke the `commons:solve` skill with `--issue <issue-id>`, adding
   `--branch <branch-name>` if step 3 produced a design branch, and passing
   `--auto`, `--draft`, and `--skip-check` through if they were provided, to
   implement the issue end-to-end and open a pull request carrying both the
   design documents and their implementation (its own plan-approval and the
   `commons:pr` approval steps surface normally unless `--auto` is set).
7. If `--review` was not provided, stop here. Otherwise, capture the pull
   request number that `commons:pr` reported creating (surfaced through
   `commons:solve`).
8. Invoke the `commons:review` skill with `--pr <pr-number>`, passing
   `--auto` through if it was provided, to get findings on the opened pull
   request and, on approval (or automatically under `--auto`), post them as
   PR review comments.
9. If `commons:review` posted any findings, invoke the `commons:resolve`
   skill with `--pr <pr-number>`, passing `--auto` and `--skip-check` through
   if they were provided, to fix them and reply on the pull request. Run at
   most this one review-and-fix pass; do not re-invoke `commons:review`
   afterward.
