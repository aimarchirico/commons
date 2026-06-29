---
name: pr
description: Create a standardized pull request
---

## When to Use

Use when the user asks to create a pull request.

## Execution Steps

1. Preflight: Verify that `CONTRIBUTING.md` exists in the repository root and `.github/PULL_REQUEST_TEMPLATE.md` exists. If any are missing, run `npx @aimarchirico/core-docs` to materialize the documentation.
2. Verify GitHub CLI (`gh`) authentication (`gh auth status`). If not logged in, provide instructions for `gh auth login` and exit.
3. Analyze the current branch and recent commits:

   - **Branch Naming**: Extract the type and issue ID from the branch name according to `CONTRIBUTING.md#branching`.
   - **PR Title**: Format the PR title according to `CONTRIBUTING.md#pull-requests`.
   - **PR Commits**: Summarize recent commits on the branch using `git log`.
4. Request related issue IDs if they were not successfully extracted in the previous step.
5. Draft the PR description by populating `.github/PULL_REQUEST_TEMPLATE.md` using the gathered context.
6. Verify remote state:

   - Check if the local branch is pushed to remote. If not, execute `git push -u origin <branch-name>` to set upstream.
7. Present the proposed PR Title and Body, and wait for explicit user approval.
8. Execute `gh pr create --title "<title>" --body "<body>"` (supporting `--draft` to create a draft PR).

## Supported Flags

- `--draft`: Submit the pull request as a draft.
