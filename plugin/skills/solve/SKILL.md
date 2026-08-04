---
name: solve
description:
  Orchestrate the development lifecycle starting from an existing issue. Use
  when the user asks to solve or implement an issue.
argument-hint: "--issue <issue-id> [--draft] [--auto] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                                                                  |
| :------------- | :------- | :--------------------------------------------------------------------------------------------------------------------------- |
| `--issue`      | Yes      | The ID of the existing GitHub issue.                                                                                         |
| `--draft`      | No       | Create the resulting pull request as a draft.                                                                                |
| `--auto`       | No       | Skip the plan-approval step in this skill and the `pr` skill's own approval prompt, running the full lifecycle autonomously. |
| `--skip-check` | No       | Skip the `commons:check` verification step that `worktree-runner` would otherwise run.                                       |

## Workflow

1. Extract `<issue-id>` from the `--issue` flag in `$ARGUMENTS`. Prompt the
   user if it was not provided.
2. Execute `gh issue view <issue-id> --json title,body` to fetch the issue's
   title and body, then fetch its Type field by running
   `python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_type.py" <issue-id>`.
3. Execute `gh issue edit <issue-id> --add-assignee @me` to assign the issue
   to the current user.
4. Determine `<branch-name>` following the naming rules in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md`, then execute
   `git fetch origin` and `git worktree add -b <branch-name> <worktree-path>
   origin/main` to create the branch off the up-to-date remote `main`, in
   an isolated worktree, where `<worktree-path>` is `../<branch-name>` (a
   sibling of the repository root).
5. Delegate to the `implementation-planner` agent, passing the issue's title,
   body, type, and `<worktree-path>`, to draft an implementation plan.
6. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
7. Delegate to the `worktree-runner` agent, passing the approved plan,
   `<worktree-path>`, and whether `--skip-check` was set, to implement it
   (it invokes `commons:commit` and `commons:docs` itself as it goes).
8. Execute `git push -u origin <branch-name>` to push the commits to the remote
   repository.
9. Invoke the `commons:pr` skill to open a pull request (its own title/body
   approval is the final review). Pass the `--draft` and `--auto` flags
   through if they were provided by the user.
10. Execute `git worktree remove <worktree-path>` to remove the isolated
    worktree; `<branch-name>` and its commits remain intact in the repository
    and on the remote.

## Output

The pull request number and URL reported by `commons:pr`, so a caller that
invoked this skill can act on it.
