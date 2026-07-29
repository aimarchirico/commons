---
name: solve
description:
  Orchestrate the development lifecycle starting from an existing issue. Use
  when the user asks to solve or implement an issue.
---

## Workflow

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root. If it
   is missing, run `npx @aimarchirico/commons-docs materialize-templates` to
   materialize the documentation.
2. Extract `<issue-id>` from the `--issue` flag. Prompt the user if it was not
   provided.
3. Execute `gh issue view <issue-id> --json title,labels` to fetch the issue
   details.
4. Determine `<branch-name>` following the naming rules in `CONTRIBUTING.md`,
   then execute `git worktree add -b <branch-name> <worktree-path>` to create
   the branch in an isolated worktree (see `skills/README.md#conventions` for
   the `<worktree-path>` naming rule). Perform every subsequent step within
   `<worktree-path>`.
5. Analyze requirements. If sub-issues exist, implement them sequentially. If no
   sub-issues exist, break the issue down into logical technical steps.
6. Execute the `commit` skill iteratively as each sub-issue or logical step is
   completed, passing the `--auto` flag through if it was provided by the
   user.
7. Execute the `docs` skill to update project documentation once implementation
   is complete, passing the `--auto` flag through if it was provided by the
   user.
8. Execute the `commit` skill one final time to commit the documentation
   updates, passing the `--auto` flag through if it was provided by the user.
9. Execute `git push -u origin <branch-name>` to push the commits to the remote
   repository.
10. Execute the `pr` skill to open a pull request. Pass the `--draft` and
    `--auto` flags through to the `pr` skill if they were provided by the
    user.

## Supported Flags

- `--issue`: The ID of the existing GitHub issue.
- `--draft`: Create the resulting pull request as a draft.
- `--auto`: Skip every approval prompt in this skill and the `commit`, `docs`,
  and `pr` skills it invokes, running the full lifecycle autonomously.
