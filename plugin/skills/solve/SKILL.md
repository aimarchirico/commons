---
name: solve
description:
  Orchestrate the development lifecycle starting from an existing issue. Use
  when the user asks to solve or implement an issue.
argument-hint: "--issue <issue-id> [--draft] [--auto] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                                                                          |
| :------------- | :------- | :----------------------------------------------------------------------------------------------------------------------------------- |
| `--issue`      | Yes      | The ID of the existing GitHub issue.                                                                                                 |
| `--draft`      | No       | Create the resulting pull request as a draft.                                                                                        |
| `--auto`       | No       | Skip the plan-approval step in this skill and the `commons:pr` skill's own approval prompt, running the full lifecycle autonomously. |
| `--skip-check` | No       | Skip the `commons:check` verification step that `worktree-runner` would otherwise run.                                               |

## Workflow

1. Extract `<issue-id>` from the `--issue` flag in `$ARGUMENTS`. Prompt the
   user if it was not provided.
2. Fetch the issue's full tree and assign it:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_tree.py" <issue-id>
   ```

   This recursively fetches the title, body, and linked project Type field
   for `<issue-id>` and every descendant sub-issue. Then, for every issue
   number found anywhere in the tree (the parent and all descendants, not
   just the parent), assign it to the current user:

   ```bash
   gh issue edit <n> --add-assignee @me
   ```

   Solving a parent issue means solving everything beneath it in one pass.
3. Set up the branch per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#branch-setup`, resolving
   `<base-branch>` with:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_base_branch.py" <issue-id>
   ```

   This checks `<issue-id>` and every descendant sub-issue for open blockers,
   not just `<issue-id>` itself, since solving it means solving its whole
   tree. Then create the branch and its worktree per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#worktrees`.
4. Delegate to the `implementation-planner` agent, passing the full fetched
   issue tree and `<worktree-path>`, to draft an implementation plan.
5. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
6. Delegate to the `worktree-runner` agent, passing the approved plan,
   `<worktree-path>`, and whether `--skip-check` was set, to implement it
   (it invokes `commons:commit` and `commons:docs` itself as it goes).
7. Open the pull request per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#opening-the-pull-request`,
   using the full list of issue numbers from the tree fetched in step 2 (the
   parent and all descendants) as the related issue IDs to close.
8. Remove the isolated worktree per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#worktrees`.

## Output

The pull request number and URL reported by `commons:pr`, so a caller that
invoked this skill can act on it.
