# Triage Reference

Bucket-to-status-to-suggestion mappings for each of the three tables
`SKILL.md` renders, plus a worked example of the final output. Buckets come
pre-sorted from `collect_triage.py`'s priority order; render them in that
order, never re-sort.

## PRs to review (from `prs_to_review`)

| Bucket             | Status            | Suggestion                        |
| :------------------ | :----------------- | :--------------------------------- |
| `review_requested` | Review requested | Review the PR with `/commons:review` |
| `not_requested`    | Not requested     | Review the PR with `/commons:review` |

## Your PRs (from `your_prs`)

| Bucket                | Status                       | Suggestion                                                             |
| :---------------------- | :----------------------------- | :--------------------------------------------------------------------- |
| `approved`             | Approved                     | Merge the PR                                                           |
| `unresolved_approved`  | Approved, unresolved feedback | Resolve the unresolved review with `/commons:resolve`, then merge the PR |
| `unresolved`           | Unresolved feedback          | Resolve the unresolved review with `/commons:resolve`                  |
| `no_unresolved`        | No unresolved feedback       | Self-review the PR with `/commons:review`                              |
| `draft`                | Draft                        | The judgment from step 2                                               |

## Backlog issues (from `backlog_issues`)

| Bucket       | Status     | Suggestion                     |
| :----------- | :---------- | :------------------------------ |
| `assigned`   | Assigned   | Solve the issue with `/commons:solve` |
| `unassigned` | Unassigned | Solve the issue with `/commons:solve` |

## Example output

Given a survey with two PRs to review, three of the user's own PRs (one
approved, one with unresolved feedback, one draft), and two backlog issues:

**PRs to review**

| PR                                       | Status            | Suggestion                            |
| :----------------------------------------- | :----------------- | :-------------------------------------- |
| #142 Fix auth token refresh              | Review requested  | Review the PR with `/commons:review`  |
| #138 Add retry backoff to fetch client   | Not requested      | Review the PR with `/commons:review`  |

**Your PRs**

| PR                              | Status                       | Suggestion                                                             |
| :--------------------------------- | :----------------------------- | :--------------------------------------------------------------------- |
| #150 Add rate limiter           | Approved                     | Merge the PR                                                           |
| #144 Migrate config loader      | Unresolved feedback          | Resolve the unresolved review with `/commons:resolve`                  |
| #151 Wire up telemetry (draft)  | Draft                        | Continuing the implementation looks right, since the diff doesn't yet cover the retry-metric requirement from #130 |

**Backlog issues**

| Issue                              | Status     | Suggestion                     |
| :------------------------------------ | :---------- | :------------------------------ |
| #130 Add retry metrics             | Assigned   | Solve the issue with `/commons:solve` |
| #128 Clean up dead feature flags   | Unassigned | Solve the issue with `/commons:solve` |
