# Triage Reference

Render up to three tables, but only if their source list is not empty,
in this order, each pre-sorted by `collect_triage.py`'s priority order
(never re-sort): PRs to review (from `prs_to_review`), Your PRs (from
`your_prs`), and Backlog issues (from `backlog_issues`). Every table's Item
column is `` [#`<number>`](<url>) `<title>` ``, linking only the number.
Every other column is rendered verbatim from the field of the same name;
none of them need further mapping.

## PRs to review (from `prs_to_review`)

| Item                         | Reviews     | Suggestion                           |
| :--------------------------- | :---------- | :----------------------------------- |
| `[#<number>](<url>) <title>` | `<reviews>` | Review the PR with `/commons:review` |

## Your PRs (from `your_prs`)

| Item                         | Review     | Threads     | Comments     | Suggestion     |
| :--------------------------- | :--------- | :---------- | :----------- | :------------- |
| `[#<number>](<url>) <title>` | `<review>` | `<threads>` | `<comments>` | `<suggestion>` |

If `suggestion` is `null`: the entry is a draft. If it has a non-null
`linked_issue`, fetch that issue's title and body, plus the PR's own
description and diff:

```bash
gh issue view <issue-number> --json title,body
gh pr view <pr-number> --json body
gh pr diff <pr-number>
```

and judge whether the implementation looks complete against what the issue
asks for, rendering the Suggestion cell as "Continue implementing" or "Mark
ready for review". If `linked_issue` is null, say plainly that there's no
linked issue to check completeness against, rather than guessing.

## Backlog issues (from `backlog_issues`)

| Item                         | Assignee     | Priority     | Blocking     | Suggestion                            |
| :--------------------------- | :----------- | :----------- | :----------- | :------------------------------------ |
| `[#<number>](<url>) <title>` | `<assignee>` | `<priority>` | `<blocking>` | Solve the issue with `/commons:solve` |
