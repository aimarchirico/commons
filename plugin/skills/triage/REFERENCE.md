# Triage Reference

Render exactly three tables, in this order, each pre-sorted by
`collect_triage.py`'s priority order (never re-sort): PRs to review (from
`prs_to_review`), Your PRs (from `your_prs`), and Backlog issues (from
`backlog_issues`). Each table follows this format:

| Item                  | Status     | Suggestion     |
| :-------------------- | :--------- | :------------- |
| #`<number>` `<title>` | `<status>` | `<suggestion>` |

The Status and Suggestion for each item come from its bucket, per the mappings
below.

## PRs to review (from `prs_to_review`)

| Bucket             | Status               | Suggestion                           |
| :----------------- | :------------------- | :----------------------------------- |
| `review_requested` | Review requested     | Review the PR with `/commons:review` |
| `not_requested`    | Review not requested | Review the PR with `/commons:review` |

## Your PRs (from `your_prs`)

| Bucket                | Status                          | Suggestion                                                               |
| :-------------------- | :------------------------------ | :----------------------------------------------------------------------- |
| `approved`            | Approved                        | Merge the PR                                                             |
| `unresolved_approved` | Approved with unresolved review | Resolve the unresolved review with `/commons:resolve`, then merge the PR |
| `unresolved`          | Unresolved review               | Resolve the unresolved review with `/commons:resolve`                    |
| `no_unresolved`       | No unresolved review            | Self-review the PR with `/commons:review`                                |
| `draft`               | Draft                           | The completeness judgment described in `SKILL.md`'s workflow             |

## Backlog issues (from `backlog_issues`)

| Bucket       | Status          | Suggestion                                                 |
| :----------- | :-------------- | :--------------------------------------------------------- |
| `assigned`   | Assigned to you | Solve the issue with `/commons:solve`                      |
| `unassigned` | Unassigned      | Solve the issue with `/commons:solve`                      |
| `blocked`    | Blocked         | Not actionable; list the open blocker(s) from `blocked_by` |
