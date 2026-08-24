---
name: solve
description:
  Orchestrate the development lifecycle starting from an existing issue. Use
  when the user asks to solve or implement an issue.
argument-hint: "--issue <issue-ids> [--branch <branch-name>] [--draft] [--auto] [--skip-check]"
---

## Arguments

| Flag           | Required | Description                                                                                                                                   |
| :------------- | :------- | :-------------------------------------------------------------------------------------------------------------------------------------------- |
| `--issue`      | Yes      | The ids of the existing GitHub issues to solve, comma-separated for more than one.                                                            |
| `--branch`     | No       | Implement onto this existing branch and its worktree instead of creating one, so the pull request also carries what the branch already holds. |
| `--draft`      | No       | Create the resulting pull request as a draft.                                                                                                 |
| `--auto`       | No       | Skip the plan-approval step in this skill and the `commons:pr` skill's own approval prompt, running the full lifecycle autonomously.          |
| `--skip-check` | No       | Skip the `commons:check` verification step that `worktree-runner` would otherwise run.                                                        |

## Workflow

1. Extract `<issue-ids>` from the `--issue` flag in `$ARGUMENTS`. Prompt the
   user if it was not provided.
2. Fetch each id's full tree and assign it, once per id:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_tree.py" <issue-id>
   ```

   This recursively fetches the title, body, and linked project Type field
   for `<issue-id>` and every descendant sub-issue. Then, for every issue
   number found anywhere in the trees (the parents and all descendants, not
   just the parents), assign it to the current user:

   ```bash
   gh issue edit <n> --add-assignee @me
   ```

   Solving an issue means solving everything beneath it in one pass, and
   several ids are solved together in that same pass.
3. Resolve `<base-branch>`, running this once per id:

   ```bash
   python3 "${CLAUDE_PLUGIN_ROOT}/skills/solve/scripts/get_issue_base_branch.py" <issue-id>
   ```

   This checks `<issue-id>` and every descendant sub-issue for open blockers,
   not just `<issue-id>` itself, since solving it means solving its whole
   tree. Ignore any candidate naming a branch for an id being solved in this
   same invocation, reporting that it already has a pull request open against
   it, and resolve what remains per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#branch-setup`.
4. Without `--branch`, set up the branch per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#branch-setup`, then create it
   and its worktree per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#worktrees`.

   With `--branch <branch-name>`, use that branch and its existing worktree
   instead of creating either, and check what it was cut from
   (`git merge-base --fork-point`) against `<base-branch>`. If they differ,
   the branch predates a blocker this work depends on: rebase it onto
   `origin/<base-branch>` if it has never been pushed, and otherwise stop and
   report, rather than rewriting a branch others may already hold.
5. Delegate to the `implementation-planner` agent, passing every fetched
   issue tree and `<worktree-path>`, to draft one implementation plan
   covering them all, sequenced so an issue's blockers are implemented
   before it.
6. Present the drafted plan, and wait for explicit user approval. Skip this
   step if the `--auto` flag is set, and proceed directly with the drafted
   plan.
7. Delegate to the `worktree-runner` agent, passing the approved plan,
   `<worktree-path>`, and whether `--skip-check` was set, to implement it
   (it invokes `commons:commit` and `commons:docs` itself as it goes).
8. Open the pull request per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#opening-the-pull-request`,
   using the full list of issue numbers from the trees fetched in step 2 (the
   parents and all descendants) as the related issue IDs to close.
9. Remove the isolated worktree per
   `${CLAUDE_PLUGIN_ROOT}/shared/CONVENTIONS.md#worktrees`.

## Output

The pull request number and URL reported by `commons:pr`, so a caller that
invoked this skill can act on it.
