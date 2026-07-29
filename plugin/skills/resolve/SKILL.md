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

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root. If it
   is missing, run `npx @aimarchirico/commons-docs materialize-templates` to
   materialize the documentation.
2. Extract `<pr-number>` from the `--pr` flag in `$ARGUMENTS`. Prompt the user
   if it was not provided.
3. Execute `gh pr view <pr-number> --json headRefName` to resolve
   `<branch-name>`, then `git worktree add <worktree-path> <branch-name>` to
   check the pull request's existing branch out into an isolated worktree,
   where `<worktree-path>` is `../<branch-name>` (a sibling of the repository
   root).
4. Delegate to the `planner` agent, passing `<pr-number>` and
   `<worktree-path>`, to fetch the pull request's feedback (conversation and
   line/file comments) and draft a fix plan mapping each piece of feedback to
   the fix addressing it.
5. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
6. Delegate to the `worktree-runner` agent, passing the approved plan and
   `<worktree-path>`, to implement it (it invokes `commons:commit` and
   `commons:docs` itself as it goes).
7. Execute `git push` to push the commits to the pull request's existing
   remote branch.
8. Draft a concise, resolving reply for each resolved line/file review
   comment, and a single summarizing reply for the pull request's
   conversation thread incorporating any conversation-level (non-line)
   comments, using the planner's feedback-to-fix mapping.
9. Present the drafted replies, and wait for explicit user approval. Skip
   this step if the `--auto` flag is set, and proceed directly with posting
   them.
10. Post each approved line/file reply, then post the approved summarizing
    reply on the conversation thread.
11. Execute `git worktree remove <worktree-path>` to remove the isolated
    worktree; `<branch-name>` and its commits remain intact in the repository
    and on the remote.
