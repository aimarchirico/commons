# Triage Reference

Render exactly three tables, in this order, each pre-sorted by
`collect_triage.py`'s priority order (never re-sort): PRs to review (from
`prs_to_review`), Your PRs (from `your_prs`), and Backlog issues (from
`backlog_issues`). Every table's Item column is
`` [#`<number>`](<url>) `<title>` ``, linking only the number.

## PRs to review (from `prs_to_review`)

| Item                         | Reviews     | Suggestion                           |
| :--------------------------- | :---------- | :----------------------------------- |
| `[#<number>](<url>) <title>` | `<reviews>` | Review the PR with `/commons:review` |

`reviews` comes from the `reviews` field:

| `reviews` value            | Rendered as              |
| :------------------------- | :----------------------- |
| `awaiting_your_review`     | Awaiting your review     |
| `not_awaiting_your_review` | Not awaiting your review |

## Your PRs (from `your_prs`)

| Item                         | Status     | Reviews     | Suggestion     |
| :--------------------------- | :--------- | :---------- | :------------- |
| `[#<number>](<url>) <title>` | `<status>` | `<reviews>` | `<suggestion>` |

`status` comes from the `status` field, `reviews` from the `reviews` field.
The Suggestion for each row comes from the `(status, reviews)` pair below:

| `status` value | `reviews` value        | Rendered status | Rendered reviews     | Suggestion                                                                                           |
| :------------- | :--------------------- | :-------------- | :------------------- | :--------------------------------------------------------------------------------------------------- |
| `approved`     | `no_unresolved_review` | Approved        | No unresolved review | Merge the PR                                                                                         |
| `approved`     | `unresolved_review`    | Approved        | Unresolved review    | Resolve the unresolved review with `/commons:resolve`, then merge the PR                             |
| `not_approved` | `unresolved_review`    | Not approved    | Unresolved review    | Resolve the unresolved review with `/commons:resolve`                                                |
| `not_approved` | `no_unresolved_review` | Not approved    | No unresolved review | Request a re-review with `/commons:review`                                                           |
| `not_approved` | `not_reviewed`         | Not approved    | Not reviewed         | Self-review the PR with `/commons:review`                                                            |
| `draft`        | `not_reviewed`         | Draft           | Not reviewed         | The completeness judgment described in `SKILL.md``${CLAUDE_PLUGIN_ROOT}/skills/triage/SKILL.md`'s workflow |

## Backlog issues (from `backlog_issues`)

| Item                         | Assignee     | Priority     | Blocking     | Suggestion                            |
| :--------------------------- | :----------- | :----------- | :----------- | :------------------------------------ |
| `[#<number>](<url>) <title>` | `<assignee>` | `<priority>` | `<blocking>` | Solve the issue with `/commons:solve` |

`assignee`, `priority`, and `blocking` come from the fields of the same name:

| Field      | Source value              | Rendered as       |
| :--------- | :------------------------ | :---------------- |
| `assignee` | `you`                     | You               |
| `assignee` | `unassigned`              | Unassigned        |
| `priority` | `Low` / `Medium` / `High` | as-is             |
| `priority` | `null`                    | Unset             |
| `blocking` | non-empty array           | `#<n>, #<m>, ...` |
| `blocking` | empty array               | Not blocking      |