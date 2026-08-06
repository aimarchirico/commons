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
2. Analyze the current branch and recent commits:

   - **Branch Naming**: Extract the type and issue ID from the branch name
     according to `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#branching`.
   - **PR Title**: Format the PR title according to
     `${CLAUDE_PLUGIN_ROOT}/.github/CONTRIBUTING.md#pull-requests`.
   - **PR Commits**: Summarize recent commits on the branch using `git log`.

3. Request related issue IDs if they were not successfully extracted in the
   previous step.
4. Draft the PR description by populating
   `${CLAUDE_PLUGIN_ROOT}/.github/PULL_REQUEST_TEMPLATE.md` using the
   gathered context.
5. Verify remote state:

   - Check if the local branch is pushed to remote. If not, execute
     `git push -u origin <branch-name>` to set upstream.

6. Present the proposed PR Title and Body, and wait for explicit user approval.
   Skip this step if the `--auto` flag is set, and proceed directly with the
   drafted title and body.
7. Create the pull request:

   ```bash
   gh pr create --title "<title>" --body "<body>"
   ```

   Pass `--draft` if the `--draft` flag was set, and `--base <base-branch>` if
   `--base` was specified (otherwise defaulting to the repository default
   branch resolved via `gh repo view --json defaultBranchRef`).

## Output

The created pull request's number and URL, parsed from `gh pr create`'s
output, so a caller that invoked this skill can act on it.
