# GitHub Actions

This directory contains shared, reusable GitHub Actions meant to be utilized
across Chirico services for CI/CD.

## Tech Stack

- **GitHub Actions**: YAML-based workflows and composite actions.
- **Shell / Bash**: Underlying scripts for task execution.

## Folder Structure

Each directory represents a standalone reusable action:

- `android-release/` — Builds and releases an Android application.
- `close-issues/` — Automatically closes stale issues.
- `cloudflare-deploy/` — Deploys applications to Cloudflare.
- `docker-release/` — Builds and pushes Docker images.
- `java-task/` — Reusable Java CI tasks.
- `node-task/` — Reusable Node.js CI tasks.
- `vps-deploy/` — Deploys applications to a VPS.

## Environment Variables

Dependencies on environment variables or secrets (e.g., `GITHUB_TOKEN`,
deployment keys) vary per action. Refer to the `action.yml` within each
subdirectory for specific `inputs` and required secrets.

## Local Development

Actions are primarily executed in the GitHub CI environment. For local testing,
you can use tools like [act](https://github.com/nektos/act).

To modify an action, edit the corresponding `action.yml` file and its associated
scripts within its directory.

## Code Quality

All YAML files and shell scripts are verified by the repository's root CI
workflows. Ensure that YAML files follow standard formatting and shell scripts
are documented.

## Deployment

Changes to these actions take effect once merged into the `main` branch.
Downstream repositories utilizing these actions will pick up the updates based
on the branch or version tag they target (e.g., `@main` or specific release tags).
