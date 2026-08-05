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
   script's priority order (do not re-sort), per the bucket-to-status and
   bucket-to-suggestion mappings in
   `${CLAUDE_PLUGIN_ROOT}/skills/triage/REFERENCE.md`: PRs to review (from
   `prs_to_review`), Your PRs (from `your_prs`), and Backlog issues (from
   `backlog_issues`). Each table follows this format:

   | Item                    | Status       | Suggestion       |
   | :----------------------- | :------------ | :---------------- |
   | #`<number>` `<title>`   | `<status>`   | `<suggestion>`   |

## Output

Nothing; this is a terminal, user-facing report that never feeds into
another skill.
