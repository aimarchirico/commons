---
name: triage
description:
  Survey open PRs and Todo issues relevant to the user and report a
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

   and parse its JSON output, per
   `${CLAUDE_PLUGIN_ROOT}/skills/triage/REFERENCE.md`.
2. For each PR in `own_prs` with `bucket == "draft"`: if it has a non-null
   `linked_issue`, fetch that issue's title and body
   (`gh issue view <number> --json title,body`) plus the PR's own diff and
   description, and judge whether the implementation looks complete
   against what the issue asks for; suggest either continuing the
   implementation or marking it ready for review, based on that judgment.
   If `linked_issue` is null, say plainly that there's no linked issue to
   check completeness against, rather than guessing.
3. For each issue in `todo_issues` with `bucket == "unassigned"`, phrase
   the suggestion in plain language as assigning it to yourself, then
   solving it with `/commons:solve`.
4. Render exactly three tables, in this order, each pre-sorted by the
   script's priority order (do not re-sort):
   - **Others' open PRs**: from `others_prs`, phrasing `review_requested`
     as "Review it with `/commons:review`" and `not_requested` as "Not yet
     requested, low priority" (if the user chooses to review it anyway,
     that's still `/commons:review`).
   - **Your open PRs**: from `own_prs`, phrasing each bucket in plain
     language: `resolve` as "Resolve the unresolved feedback with
     `/commons:resolve`", `resolve_then_merge` as "Resolve the unresolved
     feedback with `/commons:resolve`, then merge it", `get_reviewed` as
     "Get it reviewed with `/commons:review`", `ready_to_merge` as "Ready
     to merge", and `draft` as the judgment from step 2.
   - **Issues in Todo**: from `todo_issues`, phrasing `assigned` as
     something like "Solve it with `/commons:solve`" and `unassigned` per
     step 3.

   Never print internal bucket labels (e.g. `ready_to_merge`,
   `review_requested`) to the user, and never use em dashes anywhere in
   the output.
5. This skill is read-only: it never invokes `/review`, `/resolve`,
   `/solve`, or `/issue`, and never merges, assigns, or edits anything
   itself. It only reports suggestions for the user to act on.

## Output

Three rendered tables, "Others' open PRs", "Your open PRs", and "Issues in
Todo", each row pairing an item with a plain-language suggested next
step. This is a terminal, user-facing report; its output does not feed
into another skill.
