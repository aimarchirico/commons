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
1. For each PR in `your_prs` with `status == "draft"`: if it has a non-null
   `linked_issue`, fetch that issue's title and body, plus the PR's own
   description and diff:

   ```bash
   gh issue view <issue-number> --json title,body
   gh pr view <pr-number> --json body
   gh pr diff <pr-number>
   ```

   and judge whether the implementation looks complete against what the
   issue asks for; suggest either continuing the implementation or marking
   it ready for review, based on that judgment. If `linked_issue` is null,
   say plainly that there's no linked issue to check completeness against,
   rather than guessing.
1. Render the three tables per
   `${CLAUDE_PLUGIN_ROOT}/skills/triage/REFERENCE.md`.
