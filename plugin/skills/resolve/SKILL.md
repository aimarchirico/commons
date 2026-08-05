---
name: resolve
description:
  Orchestrate the development lifecycle starting from an existing pull
  request's review feedback. Use when the user asks to resolve or address
  feedback on an existing pull request.
argument-hint: "--pr <pr-number> [--auto] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                                             |
| :------------- | :------- | :------------------------------------------------------------------------------------------------------ |
| `--pr`         | Yes      | The number of the existing pull request to improve.                                                     |
| `--auto`       | No       | Skip the plan-approval and reply-approval steps in this skill, running the full lifecycle autonomously. |
| `--skip-check` | No       | Skip the `commons:check` verification step that `worktree-runner` would otherwise run.                  |

## Workflow

1. Extract `<pr-number>` from the `--pr` flag in `$ARGUMENTS`. Prompt the user
   if it was not provided.
2. Execute `gh pr view <pr-number> --json headRefName` to resolve
   `<branch-name>`, then `git fetch origin` and
   `git worktree add <worktree-path> <branch-name>` to check the pull
   request's existing branch out into an isolated worktree at its
   up-to-date remote state, where `<worktree-path>` is `../<branch-name>` (a
   sibling of the repository root).
3. Execute:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/resolve/scripts/fetch_pr_issues.py" <pr-number>
   ```

   to fetch, as one normalized JSON object (see
   `${CLAUDE_PLUGIN_ROOT}/shared/pr_feedback.py` for the checkpoint logic):

   - `threads`: unresolved review threads.
   - `comments`: comments since the last `Resolved.` checkpoint.
   - `conflicting`: whether the PR conflicts with its base branch.
   - `failing_checks`: any CI checks currently failing, with links.

4. If `conflicting` is `true`, run `git rebase origin/<base-branch>` inside
   `<worktree-path>` (`<base-branch>` from `gh pr view <pr-number> --json
   baseRefName`) to surface the actual conflicting hunks. If `failing_checks`
   is non-empty, fetch each failing run's log
   (`gh run view --log-failed <run-id>`) for diagnostic context. Delegate to
   the `implementation-planner` agent, passing the review feedback, the
   conflicting hunks (if any), the failing-check logs (if any), and
   `<worktree-path>`, to draft one fix plan mapping every item (review
   comment, conflict, or check failure) to the fix addressing it.
5. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
6. Delegate to the `worktree-runner` agent, passing the approved plan,
   `<worktree-path>`, and whether `--skip-check` was set, to implement it
   (it invokes `commons:commit` and `commons:docs` itself as it goes). If
   step 4 started a rebase, this includes completing it (`git rebase
   --continue`) as part of the plan.
7. Execute `git pull --rebase` to incorporate any commits pushed to the
   branch since the worktree was checked out, then `git push` (with
   `--force-with-lease` if step 4 rebased onto the base branch) to push the
   commits to the pull request's existing remote branch. If this rebase (as
   opposed to step 4's) hits conflicts, stop and report them to the user
   rather than resolving them unilaterally: someone else pushed to this
   branch while `worktree-runner` was working, which needs a human's
   attention.
8. Draft replies from the implementation-planner's feedback-to-fix mapping,
   covering every `threads`/`comments` item step 3's script returned exactly
   once: a concise, resolving reply for each line/file review comment, plus
   a brief conversation-level summary of what was addressed, covering any
   conversation-level comments, and, if step 4 found conflicts or failing
   checks, a one-line mention of those fixes too (they have no thread of
   their own to reply on).
9. Present the drafted replies, and wait for explicit user approval. Skip
   this step if the `--auto` flag is set, and proceed directly with posting
   them.
10. Generate a temporary `replies.json` file matching this schema from the
    approved replies, using each comment's `thread_id` from step 3's script:

    ```json
    {
      "thread_replies": [
        { "comment_id": 0, "thread_id": "string", "body": "string" }
      ],
      "conversation_summary": "string"
    }
    ```

    Then execute:

    ```bash
    python3 "${CLAUDE_PLUGIN_ROOT}/skills/resolve/scripts/post_pr_replies.py" <pr-number> replies.json
    ```

    The script resolves `{owner}/{repo}` itself. It replies to each thread
    comment, resolves that comment's review thread, then builds and posts
    the conversation-level reply from `conversation_summary` (`post_replies()`
    owns the exact format; see its docstring), then requests re-review from
    the pull request's prior reviewers, excluding the user (who can't be a
    reviewer of their own PR). It deletes the temporary file on completion.
11. Execute `git worktree remove <worktree-path>` to remove the isolated
    worktree; `<branch-name>` and its commits remain intact in the repository
    and on the remote.
