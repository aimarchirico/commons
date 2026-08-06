# Triage Reference

Start the output with a summary header:

```markdown
### Triage Survey: `<owner>/<repo>`
* **User**: `@<login>`
* **Status**: <count> active item(s) needing attention [(<assigned_to_others_count> issue(s) assigned to others, and <fully_blocked_count> blocked issue(s) hidden)]
```

If `assigned_to_others_count` or `fully_blocked_count` are greater than 0,
include them in parenthetical notes after `<count> active item(s) needing
attention` (joining non-zero items cleanly with ", and "). If both are 0, omit
the parenthetical note entirely.

Followed by a divider (`---`), then render up to four tables, but only if
their source list is not empty, in this order, each pre-sorted by
`collect_triage.py`'s priority order (never re-sort): PRs to review (from
`prs_to_review`), Your open PRs (from `your_open_prs`), Your draft PRs (from
`your_draft_prs`), and Backlog issues (from `backlog_issues`).
Every table's Item column is `` [#`<number>`](<url>) `<title>` ``,
linking only the number. Every other column is rendered verbatim from the
field of the same name; none of them need further mapping.

## PRs to review (from `prs_to_review`)

| Item                         | State     | Suggestion                                         |
| :--------------------------- | :-------- | :------------------------------------------------- |
| `[#<number>](<url>) <title>` | `<state>` | Review the PR with `/commons:review --pr <number>` |

## Your open PRs (from `your_open_prs`)

| Item                         | State     | Threads     | Comments     | Conflicting     | Checks     | Suggestion     |
| :--------------------------- | :-------- | :---------- | :----------- | :-------------- | :--------- | :------------- |
| `[#<number>](<url>) <title>` | `<state>` | `<threads>` | `<comments>` | `<conflicting>` | `<checks>` | `<suggestion>` |

## Your draft PRs (from `your_draft_prs`)

| Item                         | Suggestion     |
| :--------------------------- | :------------- |
| `[#<number>](<url>) <title>` | `<suggestion>` |

`your_draft_prs` entries have no `suggestion` field of their own, so compute
it per row. If the entry has a non-null `linked_issue`, fetch that issue's
title and body, plus the PR's own description and diff:

```bash
gh issue view <issue-number> --json title,body
gh pr view <pr-number> --json body
gh pr diff <pr-number>
```

Judge whether the implementation looks complete against what the issue asks
for, rendering the Suggestion cell as "Continue implementing" or "Mark ready
for review". If `linked_issue` is null, say plainly that there's no linked
issue to check completeness against, rather than guessing.

## Backlog issues (from `backlog_issues`)

| Item                         | Assignee     | Priority     | Blocked By     | Blocking     | Suggestion                                             |
| :--------------------------- | :----------- | :----------- | :------------- | :----------- | :----------------------------------------------------- |
| `[#<number>](<url>) <title>` | `<assignee>` | `<priority>` | `<blocked_by>` | `<blocking>` | Solve the issue with `/commons:solve --issue <number>` |
