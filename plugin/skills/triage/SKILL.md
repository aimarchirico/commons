---
name: triage
description:
  Survey open PRs and Backlog issues relevant to the user and report a
  priority-ranked, read-only list of suggested next steps. Never invokes
  other skills or takes any action. Use when the user asks what to work
  on next or wants a status survey of open work.
---

## Workflow

1. Execute:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/triage/scripts/collect_triage.py"
   ```

   and parse its JSON output.
1. Render the three tables per
   `${CLAUDE_PLUGIN_ROOT}/skills/triage/REFERENCE.md`.
