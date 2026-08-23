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
| `--review`     | No       | Once the pull requests are opened, run one review-and-fix pass over each via the `commons:review` and `commons:resolve` skills.                                 |
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
5. Capture the ids of the top-level issues `commons:issue` created.
6. Invoke the `commons:solve` skill once per captured id with
   `--issue <issue-id>`, in blocked-by order, passing `--auto`, `--draft`,
   and `--skip-check` through if they were provided, to implement each issue
   end-to-end and open its pull request (its own plan-approval and the
   `commons:pr` approval steps surface normally unless `--auto` is set). If
   step 3 produced a design branch, add `--branch <branch-name>` to the first
   invocation only, so the design documents land once rather than in every
   pull request.
7. If `--review` was not provided, stop here. Otherwise, capture the pull
   request number `commons:pr` reported for each invocation (surfaced through
   `commons:solve`).
8. Invoke the `commons:review` skill with `--pr <pr-number>` for each of
   those pull requests, passing `--auto` through if it was provided, to get
   findings on it and, on approval (or automatically under `--auto`), post
   them as PR review comments.
9. For each pull request `commons:review` posted findings on, invoke the
   `commons:resolve` skill with `--pr <pr-number>`, passing `--auto` and
   `--skip-check` through if they were provided, to fix them and reply on the
   pull request. Run at most this one review-and-fix pass per pull request;
   do not re-invoke `commons:review` afterward.
