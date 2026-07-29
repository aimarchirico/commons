---
name: resolve
description:
  Orchestrate the development lifecycle starting from an existing pull
  request's review feedback. Use when the user asks to resolve or address
  feedback on an existing pull request.
---

## Workflow

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root. If it
   is missing, run `npx @aimarchirico/commons-docs materialize-templates` to
   materialize the documentation.
2. Extract `<pr-number>` from the `--pr` flag. Prompt the user if it was not
   provided.
3. Execute `gh pr view <pr-number> --json headRefName` to resolve
   `<branch-name>`, then `git worktree add <worktree-path> <branch-name>` to
   check the pull request's existing branch out into an isolated worktree (see
   `skills/README.md#conventions` for the `<worktree-path>` naming rule).
   Perform every subsequent step within `<worktree-path>`.
4. Fetch the pull request's feedback:

   - Conversation comments via `gh pr view <pr-number> --json comments`.
   - Line/file review comments via
     `gh api repos/{owner}/{repo}/pulls/<pr-number>/comments`.

5. Investigate and draft a solution addressing each piece of feedback.
6. Present the proposed changes to the user, and wait for explicit user
   approval. Skip this step if the `--auto` flag is set, and proceed directly
   with the proposed changes.
7. Apply the approved fixes, executing the `commit` skill iteratively as each
   fix is completed, passing the `--auto` flag through if it was provided by
   the user.
8. Execute `git push` to push the commits to the pull request's existing
   remote branch.
9. Reply to each resolved line/file review comment with a concise, resolving
   reply.
10. Post a single summarizing reply on the pull request's conversation thread,
    incorporating any conversation-level (non-line) comments.

## Supported Flags

- `--pr`: The number of the existing pull request to improve.
- `--auto`: Skip every approval prompt in this skill and the `commit` skill it
  invokes, running the full lifecycle autonomously.
