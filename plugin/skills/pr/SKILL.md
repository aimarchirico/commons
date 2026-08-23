---
name: pr
description:
  Create a standardized pull request. Use when the user asks to create a
  pull request.
argument-hint: "[--draft] [--auto]"
---

## Arguments

| Flag      | Required | Description                                                            |
| :-------- | :------- | :--------------------------------------------------------------------- |
| `--draft` | No       | Submit the pull request as a draft.                                    |
| `--auto`  | No       | Skip the approval step and create the drafted PR directly.             |
| `--base`  | No       | Target base branch for the PR (defaults to repo's default branch).     |

## Workflow

1. Verify GitHub CLI (`gh`) authentication (`gh auth status`). If not logged in,
   provide instructions for `gh auth login` and exit.
2. Resolve `<base-branch>`: the `--base` flag if it was provided, otherwise
   the repository default branch from
   `gh repo view --json defaultBranchRef`. Everything below is scoped to it,
   so resolve it before analyzing anything.
3. Check whether the branch already has an open pull request:

   ```bash
   gh pr view --json number,url,state
   ```

   If it does, run only step 7 to push the commits it is missing, then
   report it as this skill's output. Nothing is drafted, approved, or
   created: a caller invoking this skill repeatedly on one branch is adding
   to that pull request, not opening another.

4. Analyze the current branch against `<base-branch>`:

   - **Branch Naming**: Extract the type and issue ID from the branch name
     according to `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#branching`.
   - **PR Title**: Format the PR title according to
     `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#pull-requests`.
   - **PR Commits**: `git log <base-branch>..HEAD` for the commits this
     branch adds. Scope to the base branch rather than listing recent
     commits generally, which would include commits already on the base.
   - **PR Changes**: `git diff <base-branch>...HEAD --stat` for the shape of
     the change, then the diff itself for its substance. Three dots, so the
     comparison is against the merge base and excludes changes that landed
     on the base branch after this one started.

   Describe the pull request from the diff, not from the commit messages
   alone: messages state intent, and anything a message glossed over is
   still in the PR.

5. Request related issue IDs if they were not successfully extracted in the
   previous step. If the branch's issue has sub-issues, close every one of
   them explicitly.
6. Draft the PR description by populating
   `${CLAUDE_PLUGIN_ROOT}/.github/PULL_REQUEST_TEMPLATE.md` using the
   gathered context.
7. Verify remote state. This skill owns pushing, so callers invoke it without
   pushing first:

   - Execute `git status --porcelain`. If the working tree is dirty, those
     changes will not be in the pull request. Report the uncommitted paths
     and ask whether to continue or to commit them first via
     `commons:commit`. Under `--auto`, continue, but report the omission in
     the output. Never commit them as a side effect of opening a PR: what
     belongs in which commit is `commons:commit`'s decision.
   - If the branch has no upstream, execute `git push -u origin <branch-name>`
     to set it.
   - Otherwise, if the branch has commits the remote does not, execute
     `git push`. An existing upstream does not imply the branch is current.

8. Present the proposed PR Title and Body, and wait for explicit user approval.
   Skip this step if the `--auto` flag is set, and proceed directly with the
   drafted title and body.
9. Create the pull request:

   ```bash
   gh pr create --title "<title>" --body "<body>"
   ```

   Pass `--draft` if the `--draft` flag was set, and `--base <base-branch>`
   if `<base-branch>` differs from the repository default branch.

## Output

The pull request's number and URL, parsed from `gh pr create`'s output or
from the existing pull request found in step 3, so a caller that invoked
this skill can act on it.
