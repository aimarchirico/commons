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
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/resolve/scripts/fetch_pr_feedback.py" <pr-number>
   ```

   to fetch the pull request's conversation comments and unresolved review
   threads as normalized JSON. Delegate to the `implementation-planner`
   agent, passing this feedback and `<worktree-path>`, to draft a fix plan
   mapping each piece of feedback to the fix addressing it.
4. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
5. Delegate to the `worktree-runner` agent, passing the approved plan,
   `<worktree-path>`, and whether `--skip-check` was set, to implement it
   (it invokes `commons:commit` and `commons:docs` itself as it goes).
6. Execute `git pull --rebase` to incorporate any commits pushed to the
   branch since the worktree was checked out, then `git push` to push the
   commits to the pull request's existing remote branch. If the rebase hits
   conflicts, stop and report them to the user rather than resolving them
   unilaterally.
7. Draft a concise, resolving reply for each resolved line/file review
   comment, using the implementation-planner's feedback-to-fix mapping;
   every item `fetch_pr_feedback.py` returned must be covered by exactly one
   of these replies in this single pass.
   - Draft a single summarizing reply for the pull request's conversation
     thread, incorporating any conversation-level (non-line) comments. Its
     first substantive line (a `## Resolution summary` header may precede
     it) must be the literal verdict `Resolved.` (this lets
     `/commons:triage` recognize the PR's conversation as resolved),
     followed by a brief description of what was addressed, e.g.:

     ```markdown
     ## Resolution summary

     Resolved. Addressed the null-check feedback in `parse.py` and added
     the missing test case for the empty-input path.
     ```
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

   (the script resolves `{owner}/{repo}` itself, requests re-review from the
   pull request's prior reviewers excluding the user, since the user can't
   be a reviewer of their own PR, and deletes the temporary file upon
   completion).
10. Execute `git worktree remove <worktree-path>` to remove the isolated
    worktree; `<branch-name>` and its commits remain intact in the repository
    and on the remote.
