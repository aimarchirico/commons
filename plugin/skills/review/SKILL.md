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
   - Render each finding into a comment body using this template:

     ```markdown
     **<summary>**

     <failure_scenario>

     _category: <category>_
     ```

   - Build a `comments` array (`path`, `line`, `body`) from findings with a
     resolvable file and line, using the rendered template as `body`.
   - Build the summary `body`. Let `n` be the total merged finding count
     (step 4) and `k` be the number placed in `comments`. The first
     substantive line (ignoring any markdown header before it) is always an
     explicit verdict, verbatim: `Approved.` if `n` is 0, otherwise
     `Requesting changes.` (the self-review-signal GitHub Action matches on
     this exact text to submit a real review on the user's behalf, since
     the user can't approve or request changes on their own PR).
     - If `n` is 0, the verdict line is the entire body.
     - Otherwise, follow the verdict line with a blank line, then
       `## Review summary`, then a summary line stating `n` and `k`. If
       `n` > `k`, append the unresolvable findings below it, e.g.:

       ```markdown
       Requesting changes.

       ## Review summary

       <n> findings across logic, compliance, performance, and security — <k>
       posted as inline comments on the diff. The remainder, listed below,
       have no resolvable file/line:

       <rendered unresolvable findings, if any>
       ```

   - Generate a temporary `review.json` file matching this schema:

     ```json
     {
       "body": "string",
       "comments": [
         { "path": "string", "line": 0, "body": "string" }
       ]
     }
     ```

   - Execute:

     ```bash
     python3 "${CLAUDE_PLUGIN_ROOT}/skills/review/scripts/post_review_comments.py" <pr-number> review.json
     ```

     (the script resolves `{owner}/{repo}` itself and deletes the temporary
     file upon completion).

## Output

The merged findings, and whether any were posted as PR review comments, so
a caller that invoked this skill can act on it.
