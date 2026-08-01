---
name: review
description:
  Reviews a given pull request by delegating to four parallel read-only
  reviewer agents (logic, performance, security, compliance), merging their
  findings, and optionally posting them as PR review comments.
  Findings-only — no fixes are applied. Use when the user asks to review a
  pull request.
argument-hint: "--pr <pr-number> [--auto]"
---

## Arguments

| Flag     | Required | Description                                                              |
| :------- | :------- | :------------------------------------------------------------------------ |
| `--pr`   | Yes      | The pull request number to review.                                       |
| `--auto` | No       | Skip the approval prompt before posting findings as PR review comments.  |

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
   - Resolve `{owner}/{repo}` from the repository, e.g. via
     `gh repo view --json owner,name`; don't hardcode it.
   - Build a `comments` array (`path`, `line`, `body`) from findings with a
     resolvable file and line.
   - Post via
     `gh api repos/{owner}/{repo}/pulls/<pr-number>/reviews -f event=COMMENT`
     with one `-f "comments[]=..."` entry per finding.
   - Any findings without a precise file/line go into the review's overall
     summary `body` instead.
