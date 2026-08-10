# Triage Reference

Start the output with a summary header:

```markdown
**Triage Survey**: `<owner>/<repo>`

* **User**: `@<login>`
* **Status**: <active_count> active item/items needing attention
  (<assigned_to_others_count> issue/issues assigned to others, and
  <fully_blocked_count> blocked issue/issues hidden)
```

`<active_count>` is rendered verbatim from the script's `active_count` field.

Use "item" when `<active_count>` is 1, "items" otherwise. Apply the same
singular/plural rule to "issue/issues" in the parenthetical note.

If `assigned_to_others_count` or `fully_blocked_count` are greater than 0,
include them in parenthetical notes after `<count> active item/items needing
attention` (joining non-zero items cleanly with ", and "). If both are 0, omit
the parenthetical note entirely.

Only leaf issues (no children of their own) are ever listed as `<item>`: a
Story with open Subtasks isn't itself an actionable row, since it isn't the
thing that gets its own PR. A leaf's blockers include its own `blocked_by`
plus any blocker on its ancestors (a block directly on the containing Story
or Epic blocks every leaf beneath it too), each rendered as
`PR #<n>`/`Issue #<n>`, with `(via parent)` appended when inherited from an
ancestor rather than set directly on the leaf.

`fully_blocked_count` covers leaves blocked by more than one open PR, or by
any open issue that lacks an attached open PR — stacking only works against
one unambiguous base branch, so anything short of "every blocker resolves to
the same single open PR" doesn't qualify. They remain tracked (so PRs
closing one of their blockers still get credited in `<blocking>`), but are
hidden from the Actionable Items and Unassigned Issues tables below because
they are not yet stackable.

Followed by a divider (`---`), then render up to three categories,
their descriptions, their tables, and each table's description,
omitting empty categories or tables. Every table column (including
`<item>`) is rendered verbatim from the field of the same name.

---

## Actionable Items

Work that is currently blocked by you or requires your immediate input to move
forward. Ordered by unblocking teammates first, then pipeline completion.

### Review Requests

These PRs are authored by others and are waiting to be approved.

| Item | Review | Priority | Blocking | Suggestion |
| :--- | :----- | :------- | :------- | :--------- |
| `<item>` | `<review>` | `<priority>` | `<blocking>` | Review the PR with `/commons:review --pr <number>` |

### Merge Ready

These are your approved PRs targeting the default branch and they are ready to merge.

| Item | Priority | Blocking | Suggestion |
| :--- | :------- | :------- | :--------- |
| `<item>` | `<priority>` | `<blocking>` | Merge the PR |

### Merge Blockers

These are your PRs with blockers to resolve before merging.

| Item | Technical Blockers | Review Blockers | Priority | Blocking | Suggestion |
| :--- | :----------------- | :-------------- | :------- | :------- | :--------- |
| `<item>` | `<technical_blockers>` | `<review_blockers>` | `<priority>` | `<blocking>` | Resolve problems with `/commons:resolve --pr <number>` |

### Draft PRs

These are your PRs currently marked as Draft.

| Item | Priority | Blocking | Suggestion |
| :--- | :------- | :------- | :--------- |
| `<item>` | `<priority>` | `<blocking>` | `<suggestion>` |

`draft_prs` entries compute `<suggestion>` per row. If the entry has a non-null
`linked_issue`, fetch that issue's title and body, plus the PR's description and
diff:

```bash
gh issue view <issue-number> --json title,body
gh pr view <pr-number> --json body
gh pr diff <pr-number>
```

Judge whether the implementation looks complete against what the issue asks
for, rendering Suggestion as "Continue implementing" or "Mark ready for
review". If `linked_issue` is null, say plainly that there is no linked issue
to check completeness against.

### In Progress

These are issues assigned to you marked In Progress with no open PR yet.

| Item | Priority | Blocking | Suggestion |
| :--- | :------- | :------- | :--------- |
| `<item>` | `<priority>` | `<blocking>` | Continue implementing or open PR |

### Assigned Ready

These are issues assigned to you and not blocked by anything.

| Item | Priority | Blocking | Suggestion |
| :--- | :------- | :------- | :--------- |
| `<item>` | `<priority>` | `<blocking>` | Solve issue with `/commons:solve --issue <number>` |

### Assigned Stackable

These are issues assigned to you, all of whose blockers resolve to the same
single open PR.

| Item | Blocked by | Priority | Blocking | Suggestion |
| :--- | :--------- | :------- | :------- | :--------- |
| `<item>` | `<blocked_by>` | `<priority>` | `<blocking>` | Solve issue with `/commons:solve --issue <number>` |

---

## Pending PRs

Work you own but cannot advance until reviewers finish their tasks.

### Pending Approval

These are your PRs targeting the default branch, but they are waiting to be approved.

| Item | Priority | Blocking | Suggestion |
| :--- | :------- | :------- | :--------- |
| `<item>` | `<priority>` | `<blocking>` | Self-review the PR with `/commons:review --pr <number>` |

### Stacked Queue

These are your PRs targeting a branch that still has an open PR.

| Item | Stacked on | Priority | Blocking | Suggestion |
| :--- | :--------- | :------- | :------- | :--------- |
| `<item>` | `<stacked_on>` | `<priority>` | `<blocking>` | Self-review the PR with `/commons:review --pr <number>` |

---

## Unassigned Issues

The open pool of available issues ready to be claimed and started.

### Available Ready

These are unassigned issues not blocked by anything.

| Item | Priority | Blocking | Suggestion |
| :--- | :------- | :------- | :--------- |
| `<item>` | `<priority>` | `<blocking>` | Solve issue with `/commons:solve --issue <number>` |

### Available Stackable

These are unassigned issues, all of whose blockers resolve to the same
single open PR.

| Item | Blocked by | Priority | Blocking | Suggestion |
| :--- | :--------- | :------- | :------- | :--------- |
| `<item>` | `<blocked_by>` | `<priority>` | `<blocking>` | Solve issue with `/commons:solve --issue <number>` |
