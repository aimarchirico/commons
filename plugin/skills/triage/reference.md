# Triage Reference

The authoritative source for how `collect_triage.py` gathers data and how
both the script and `SKILL.md` classify it. If either drifts from this
file, this file wins.

## Data Sources

| Call                                                                  | Why                                                                                                                     |
| :--------------------------------------------------------------------- | :------------------------------------------------------------------------------------------------------------------------ |
| `gh pr list --search "is:open -author:@me draft:false" --json number,title,url,author,reviewRequests` | Other authors' open, ready (non-draft) PRs, to see which need this user's review.                                     |
| `gh pr list --search "is:open author:@me" --json number,title,url,isDraft,reviewDecision,closingIssuesReferences` | This user's own open PRs, to see what needs merging, resolving, or finishing.                                          |
| GraphQL `reviewThreads(first: 50) { nodes { isResolved } }` on a PR   | REST has no equivalent field for review-thread resolution state; only the GraphQL API exposes `isResolved`.             |
| `gh project item-list <number> --owner <owner> --format json --limit 200` | Todo-status items in the repo's linked Project, already resolved to option names (status, type) rather than raw IDs. If more than one open Project is linked, the one titled to match the repo name is used to disambiguate (same rule as `issue/scripts/project_utils.py`). |
| `gh issue list --state open --json number,parent --limit 200`        | Cross-reference to drop sub-issues from the Todo survey; only root issues are worth triaging directly.                 |
| `gh api user --jq .login` (once)                                     | `gh pr list`/`gh issue list` accept the `@me` alias natively, but GraphQL queries (review threads, project ownership) do not, so the login is resolved once up front and reused. |

## Classification

### Others' open PRs (2-way)

| Condition                                   | Bucket              |
| :------------------------------------------- | :------------------- |
| User's login appears in `reviewRequests`    | `review_requested`  |
| Otherwise                                   | `not_requested`     |

Sort order: `review_requested`, then `not_requested`. Bot-authored PRs
(`author.is_bot == true`) are dropped entirely before classification.

### Own open PRs (5-way, draft checked first)

| Condition                                                     | Bucket                |
| :--------------------------------------------------------------- | :--------------------- |
| `isDraft` is true                                             | `draft`               |
| `reviewDecision == "APPROVED"` and no unresolved threads      | `ready_to_merge`       |
| `reviewDecision == "APPROVED"` and unresolved threads exist   | `resolve_then_merge`   |
| `reviewDecision != "APPROVED"` and unresolved threads exist   | `resolve`              |
| Otherwise                                                     | `get_reviewed`         |

Sort order: `ready_to_merge`, `resolve_then_merge`, `resolve`,
`get_reviewed`, `draft`.

### Root Todo issues (2-way)

| Condition                                          | Bucket        |
| :---------------------------------------------------- | :------------- |
| User's login is among the item's `assignees`       | `assigned`    |
| `assignees` is empty                               | `unassigned`  |

Sort order: `assigned`, then `unassigned`. Items assigned to someone other
than the user, any issue with a non-null `parent` (a sub-issue), and any
issue whose `Type` field isn't `Story`, `Task`, or `Bug`, are dropped
entirely. Epics are containers, not directly solvable in one pass, and
Subtasks are already excluded via the `parent` check; only root issues
actionable by this user in a single `/solve` are surveyed.

## Out of Scope Here

Judging whether a draft PR's implementation looks complete against its
linked issue, and phrasing the "assign yourself, then solve it" suggestion
for unassigned Todo issues, are both `SKILL.md`'s job at render time, not
this script's or this document's. The script only classifies; it never
reads issue/PR bodies or renders user-facing language.
