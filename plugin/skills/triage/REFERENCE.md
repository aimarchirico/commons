# Triage Reference

Bucket-to-status-to-suggestion mappings for each of the three tables
`SKILL.md` renders. Buckets come pre-sorted from `collect_triage.py`'s
priority order; render them in that order, never re-sort.

## PRs to review (from `prs_to_review`)

| Bucket             | Status            | Suggestion                        |
| :------------------ | :----------------- | :--------------------------------- |
| `review_requested` | Review requested | Review the PR with `/commons:review` |
| `not_requested`    | Not requested     | Review the PR with `/commons:review` |

## Your PRs (from `your_prs`)

| Bucket                | Status                       | Suggestion                                                             |
| :---------------------- | :----------------------------- | :--------------------------------------------------------------------- |
| `approved`             | Approved                     | Merge the PR                                                           |
| `unresolved_approved`  | Approved, unresolved review | Resolve the unresolved review with `/commons:resolve`, then merge the PR |
| `unresolved`           | Unresolved review           | Resolve the unresolved review with `/commons:resolve`                  |
| `no_unresolved`        | No unresolved review       | Self-review the PR with `/commons:review`                              |
| `draft`                | Draft                        | The completeness judgment described in `SKILL.md`'s workflow           |

## Backlog issues (from `backlog_issues`)

| Bucket       | Status     | Suggestion                     |
| :----------- | :---------- | :------------------------------ |
| `assigned`   | Assigned   | Solve the issue with `/commons:solve` |
| `unassigned` | Unassigned | Solve the issue with `/commons:solve` |
