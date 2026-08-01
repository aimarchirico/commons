---
name: resolve
description:
  Orchestrate the development lifecycle starting from an existing pull
  request's review feedback. Use when the user asks to resolve or address
  feedback on an existing pull request.
argument-hint: "--pr <pr-number> [--auto]"
---

## Arguments

| Flag     | Required | Description                                                                                             |
| :------- | :------- | :------------------------------------------------------------------------------------------------------ |
| `--pr`   | Yes      | The number of the existing pull request to improve.                                                     |
| `--auto` | No       | Skip the plan-approval and reply-approval steps in this skill, running the full lifecycle autonomously. |

## Workflow

1. Extract `<pr-number>` from the `--pr` flag in `$ARGUMENTS`. Prompt the user
   if it was not provided.
2. Execute `gh pr view <pr-number> --json headRefName` to resolve
   `<branch-name>`, then `git worktree add <worktree-path> <branch-name>` to
   check the pull request's existing branch out into an isolated worktree,
   where `<worktree-path>` is `../<branch-name>` (a sibling of the repository
   root).
3. Execute:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/resolve/scripts/fetch_pr_feedback.py" <pr-number>
   ```

   to fetch the pull request's conversation comments and unresolved review
   threads as normalized JSON. Delegate to the `planner` agent, passing this
   feedback and `<worktree-path>`, to draft a fix plan mapping each piece of
   feedback to the fix addressing it.
4. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
5. Delegate to the `worktree-runner` agent, passing the approved plan and
   `<worktree-path>`, to implement it (it invokes `commons:commit` and
   `commons:docs` itself as it goes).
6. Execute `git push` to push the commits to the pull request's existing
   remote branch.
7. Draft a concise, resolving reply for each resolved line/file review
   comment, and a single summarizing reply for the pull request's
   conversation thread incorporating any conversation-level (non-line)
   comments, using the planner's feedback-to-fix mapping.
8. Present the drafted replies, and wait for explicit user approval. Skip
   this step if the `--auto` flag is set, and proceed directly with posting
   them.
9. Generate a temporary `replies.json` file matching this schema from the
   approved replies:

   ```json
   {
     "thread_replies": [
       { "comment_id": 0, "body": "string" }
     ],
     "conversation_reply": "string"
   }
   ```

   Then execute:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/resolve/scripts/post_pr_replies.py" <pr-number> replies.json
   ```

   (the script resolves `{owner}/{repo}` itself and deletes the temporary
   file upon completion).
10. Execute `git worktree remove <worktree-path>` to remove the isolated
    worktree; `<branch-name>` and its commits remain intact in the repository
    and on the remote.
