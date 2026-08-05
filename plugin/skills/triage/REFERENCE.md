# Triage Reference

Start the output with a summary header:

```markdown
### Triage Survey: `<owner>/<repo>`
* **User**: `@<login>`
* **Status**: <count> active item(s) needing attention (items are priority-ranked by actionability below)
```

Followed by a divider (`---`), then render up to four tables, but only if
their source list is not empty, in this order, each pre-sorted by
`collect_triage.py`'s priority order (never re-sort): PRs to review (from
`prs_to_review`), Your open PRs (from `your_prs`), Your draft PRs (from
`your_draft_prs`), and Backlog issues (from `backlog_issues`).
Every table's Item column is `` [#`<number>`](<url>) `<title>` ``,
linking only the number. Every other column is rendered verbatim from the
field of the same name; none of them need further mapping.

## PRs to review (from `prs_to_review`)

| Item                         | State     | Suggestion                                         |
| :--------------------------- | :-------- | :------------------------------------------------- |
| `[#<number>](<url>) <title>` | `<state>` | Review the PR with `/commons:review --pr <number>` |

## Your open PRs (from `your_prs`)

| Item                         | State     | Threads     | Comments     | Conflicting     | Checks     | Suggestion     |
| :--------------------------- | :-------- | :---------- | :----------- | :-------------- | :--------- | :------------- |
| `[#<number>](<url>) <title>` | `<state>` | `<threads>` | `<comments>` | `<conflicting>` | `<checks>` | `<suggestion>` |

## Your draft PRs (from `your_draft_prs`)

| Item                         | Suggestion     |
| :--------------------------- | :------------- |
| `[#<number>](<url>) <title>` | `<suggestion>` |

`your_draft_prs` entries have no `suggestion` field of their own — compute
it per row. If the entry has a non-null `linked_issue`, fetch that issue's
title and body, plus the PR's own description and diff:

```bash
gh issue view <issue-number> --json title,body
gh pr view <pr-number> --json body
gh pr diff <pr-number>
```

and judge whether the implementation looks complete against what the issue
asks for, rendering the Suggestion cell as "Continue implementing" or "Mark
ready for review". If `linked_issue` is null, say plainly that there's no
linked issue to check completeness against, rather than guessing. Don't
factor in conflicts or CI status here — those aren't actionable until the
PR is out of draft.

## Backlog issues (from `backlog_issues`)

| Item                         | Assignee     | Priority     | Blocking     | Suggestion                                             |
| :--------------------------- | :----------- | :----------- | :----------- | :----------------------------------------------------- |
| `[#<number>](<url>) <title>` | `<assignee>` | `<priority>` | `<blocking>` | Solve the issue with `/commons:solve --issue <number>` |
