---
name: review
description:
  Reviews a given pull request by delegating to four parallel read-only
  reviewer agents (logic, compliance, performance, security), merging their
  findings, and optionally posting them as PR review comments.
  Findings-only, no fixes are applied. Use when the user asks to review a
  pull request.
argument-hint: "--pr <pr-number> [--auto]"
---

## Arguments

| Flag     | Required | Description                                                             |
| :------- | :------- | :---------------------------------------------------------------------- |
| `--pr`   | Yes      | The pull request number to review.                                      |
| `--auto` | No       | Skip the approval prompt before posting findings as PR review comments. |

## Workflow

1. Extract `<pr-number>` from the `--pr` flag in `$ARGUMENTS`. Prompt the
   user if it was not provided.
2. Fetch the diff: `gh pr diff <pr-number>`.
3. Delegate to the `logic-reviewer`, `performance-reviewer`,
   `security-reviewer`, and `compliance-reviewer` agents in parallel (a
   single message with all four delegations), passing each the diff and
   `<pr-number>`. Each reports back via `ReportFindings`.
4. Merge the four agents' findings: dedupe entries pointing at the same
   file/line, and rank the combined list most severe first.
5. Present the merged findings to the user.
6. Offer to post the findings as PR review comments. Wait for explicit user
   approval before posting, unless the `--auto` flag is set. On approval:
   - Generate a temporary `findings.json` file containing the merged
     findings list from step 4, each matching this schema:

     ```json
     {
       "file": "string",
       "line": 0,
       "summary": "string",
       "failure_scenario": "string",
       "category": "string"
     }
     ```

   - Execute:

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/skills/review/scripts/post_review_comments.py" <pr-number> findings.json
     ```

     (`build_review()` in that script owns the rendering, verdict, and
     summary rules; see its docstring. Posts everything as a single PR
     review, then deletes the temporary file.)

## Output

The merged findings, and whether any were posted as PR review comments, so
a caller that invoked this skill can act on it.
