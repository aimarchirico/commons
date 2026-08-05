# Triage Reference

Render up to three tables, but only if their source list is not empty,
in this order, each pre-sorted by `collect_triage.py`'s priority order
(never re-sort): PRs to review (from `prs_to_review`), Your PRs (from
`your_prs`), and Backlog issues (from `backlog_issues`). Every table's Item
column is `` [#`<number>`](<url>) `<title>` ``, linking only the number.

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

| Item                         | Review     | Threads     | Comments     | Suggestion     |
| :--------------------------- | :--------- | :---------- | :----------- | :------------- |
| `[#<number>](<url>) <title>` | `<review>` | `<threads>` | `<comments>` | `<suggestion>` |

`review`, `threads`, and `comments` come from the fields of the same name:

| `review` value       | Rendered as         |
| :-------------------- | :------------------- |
| `approved`            | Approved             |
| `changes_requested`   | Changes requested    |
| `commented`           | Commented            |
| `none`                | None                 |
| `not_ready`           | Not ready for review |

| `threads` / `comments` value | Rendered as |
| :---------------------------- | :---------- |
| `none`                         | None        |
| `resolved`                     | Resolved    |
| `unresolved`                   | Unresolved  |

The Suggestion for each row comes from this decision procedure, evaluated
top to bottom (never re-derive it from anything other than these three
fields):

1. If `review` is `not_ready`: the completeness judgment described in
   `${CLAUDE_PLUGIN_ROOT}/skills/triage/SKILL.md`'s workflow (yields either
   "Continue implementing" or "Mark ready for review").
2. Else if `threads` is `unresolved` or `comments` is `unresolved`:
   - `review == approved` → "Resolve the unresolved review with
     `/commons:resolve`, then merge the PR"
   - else → "Resolve the unresolved review with `/commons:resolve`"
3. Else (`threads` and `comments` are both `resolved` or `none`):
   - `review == approved` → "Merge the PR"
   - else → "Self-review the PR with `/commons:review`"

Priority order used to sort `your_prs` (never re-sort): "Merge the PR" first,
then "Resolve..., then merge the PR", then "Resolve the unresolved
review...", then "Self-review the PR...", then step 1's completeness-judgment
outcomes last.

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
