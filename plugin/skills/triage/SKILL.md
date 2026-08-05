---
name: triage
description:
  Survey open PRs and Backlog issues relevant to the user and report a
  priority-ranked, read-only list of suggested next steps. Never invokes
  other skills or takes any action. Use when the user asks what to work
  on next or wants a status survey of open work.
---

## Arguments

None. This skill takes no arguments.

## Workflow

1. Execute:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/triage/scripts/collect_triage.py"
   ```

   and parse its JSON output.
2. For each PR in `own_prs` with `bucket == "draft"`: if it has a non-null
   `linked_issue`, fetch that issue's title and body
   (`gh issue view <number> --json title,body`) plus the PR's own diff and
   description, and judge whether the implementation looks complete
   against what the issue asks for; suggest either continuing the
   implementation or marking it ready for review, based on that judgment.
   If `linked_issue` is null, say plainly that there's no linked issue to
   check completeness against, rather than guessing.
3. Render exactly three tables, in this order, each pre-sorted by the
   script's priority order (do not re-sort):

   Others' open PRs (from `others_prs`):

   | Bucket             | Suggestion                                                                                                |
   | :----------------- | :-------------------------------------------------------------------------------------------------------- |
   | `review_requested` | Review it with `/commons:review`                                                                          |
   | `not_requested`    | Not yet requested, low priority (if the user chooses to review it anyway, that's still `/commons:review`) |

   Your open PRs (from `own_prs`):

   | Bucket               | Suggestion                                                             |
   | :------------------- | :--------------------------------------------------------------------- |
   | `ready_to_merge`     | Merge it                                                               |
   | `resolve_then_merge` | Resolve the unresolved feedback with `/commons:resolve`, then merge it |
   | `resolve`            | Resolve the unresolved feedback with `/commons:resolve`                |
   | `get_reviewed`       | Self-review it with `/commons:review`                                  |
   | `draft`              | The judgment from step 2                                               |

   Backlog issues (from `todo_issues`):

   | Bucket       | Suggestion                                          |
   | :----------- | :-------------------------------------------------- |
   | `assigned`   | Solve it with `/commons:solve`                      |
   | `unassigned` | Self-assign it, then solve it with `/commons:solve` |

## Output

Three rendered tables, "Others' open PRs", "Your open PRs", and "Backlog
issues", each row pairing an item with a plain-language suggested next
step. This is a terminal, user-facing report; its output does not feed
into another skill.
