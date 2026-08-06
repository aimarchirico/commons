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
2. Fetch the issue details and assign it:

   ```bash
   gh issue view <issue-id> --json title,body
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_type.py" <issue-id>
   gh issue edit <issue-id> --add-assignee @me
   ```

   This retrieves the title, body, and linked project Type field, and assigns
   the issue to the current user.
3. Determine `<branch-name>` following the naming rules in
   `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md`, resolve `<base-branch>`,
   and set up the worktree:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_base_branch.py" <issue-id>
   git fetch origin
   git worktree add -b <branch-name> <worktree-path> origin/<base-branch>
   ```

   If the script reports multiple candidate branches (because the issue is
   blocked by multiple open PRs), prompt the user to choose which base branch
   to stack on or use the default branch.
   This creates the branch off the up-to-date remote base branch in an isolated
   worktree, where `<worktree-path>` is `../<branch-name>` (a sibling of the
   repository root).
4. Delegate to the `implementation-planner` agent, passing the issue's title,
   body, type, and `<worktree-path>`, to draft an implementation plan.
5. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
6. Delegate to the `worktree-runner` agent, passing the approved plan,
   `<worktree-path>`, and whether `--skip-check` was set, to implement it
   (it invokes `commons:commit` and `commons:docs` itself as it goes).
7. Push commits and open the pull request:

   ```bash
   git push -u origin <branch-name>
   ```

   This pushes the commits to the remote repository. Next, invoke the
   `commons:pr` skill to open a pull request (its own title/body approval is
   the final review), passing `--base <base-branch>` (if `<base-branch>` is
   set and differs from the default branch), along with `--draft` and `--auto`
   flags if provided by the user.
8. Remove the isolated worktree:

   ```bash
   git worktree remove <worktree-path>
   ```

   This cleans up the temporary worktree while preserving `<branch-name>` and
   its commits in the repository and on the remote.

## Output

The pull request number and URL reported by `commons:pr`, so a caller that
invoked this skill can act on it.
