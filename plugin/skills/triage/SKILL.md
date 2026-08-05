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
2. For each PR in `your_prs` with `bucket == "draft"`: if it has a non-null
   `linked_issue`, fetch that issue's title and body
   (`gh issue view <number> --json title,body`) plus the PR's own diff and
   description, and judge whether the implementation looks complete
   against what the issue asks for; suggest either continuing the
   implementation or marking it ready for review, based on that judgment.
   If `linked_issue` is null, say plainly that there's no linked issue to
   check completeness against, rather than guessing.
3. Render exactly three tables, in this order, each pre-sorted by the
   script's priority order (do not re-sort):

   PRs to review (from `prs_to_review`):

   | Bucket             | Suggestion                       |
   | :----------------- | :-------------------------------- |
   | `review_requested` | Review it with `/commons:review` |
   | `not_requested`    | Review it with `/commons:review` |

   Your PRs (from `your_prs`):

   | Bucket                 | Suggestion                                                             |
   | :---------------------- | :--------------------------------------------------------------------- |
   | `approved`              | Merge it                                                               |
   | `unresolved_approved`   | Resolve the unresolved feedback with `/commons:resolve`, then merge it |
   | `unresolved`            | Resolve the unresolved feedback with `/commons:resolve`                |
   | `no_unresolved`         | Self-review it with `/commons:review`                                  |
   | `draft`                 | The judgment from step 2                                               |

   Backlog issues (from `backlog_issues`):

   | Bucket       | Suggestion                                          |
   | :----------- | :-------------------------------------------------- |
   | `assigned`   | Solve it with `/commons:solve`                      |
   | `unassigned` | Self-assign it, then solve it with `/commons:solve` |

## Output

Three rendered tables, "PRs to review", "Your PRs", and "Backlog
issues", each row pairing an item with a plain-language suggested next
step. This is a terminal, user-facing report; its output does not feed
into another skill.
