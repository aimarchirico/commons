# Tools

Shared repository tooling: commit and Markdown linting, Git hooks, task
orchestration, and release automation for the monorepo. Contains no
application code.

## Tech Stack

| Technology          | Version | Purpose                      |
| :------------------ | :------ | :--------------------------- |
| pnpm                | -       | Package manager              |
| commitlint          | ^19.0.0 | Commit message linting       |
| config-conventional | ^19.0.0 | Conventional Commits ruleset |
| markdownlint-cli2   | ^0.23.0 | Markdown linting             |
| ESLint              | ^9.39.5 | Configuration file linting   |
| TypeScript          | ^6.0.3  | Typing support for ESLint    |
| Husky               | ^9.1.7  | Git hooks                    |

## Folder Structure

```text
tools/
├── .husky/                        # Git hooks (commit-msg → commitlint)
├── Taskfile.yaml                  # Task command definitions
├── .commitlintrc.yaml             # commitlint configuration (extends config-conventional)
├── .markdownlint-cli2.yaml        # markdownlint configuration
├── eslint.config.ts               # ESLint configuration for tool configs (YAML, TOML)
├── tsconfig.json                  # TypeScript configuration for ESLint
├── release-please-config.json     # release-please package config
├── .release-please-manifest.json  # release-please version manifest
├── pnpm-workspace.yaml            # Isolated tooling workspace
└── .npmrc                         # GitHub Packages registry
```

## Environment Variables

Installing the `@aimarchirico`-scoped dependencies
from GitHub Packages (see `.npmrc`) requires an authenticated npm token. The
Taskfile honors these runtime variables:

| Variable            | Purpose                                      |
| :------------------ | :------------------------------------------- |
| `CI`                | Gates automatic dependency install           |
| `EDIT_FILE`         | Commit-message file passed to `commit:check` |
| `FROM_SHA`/`TO_SHA` | Commit range passed to `commit:check`        |

## Local Development

Requires Node.js, pnpm, and [go-task](https://taskfile.dev). Install
dependencies with `pnpm install`. Tasks are flattened into the root Taskfile
and run from the repository root:

| Command             | Description          |
| :------------------ | :------------------- |
| `task docs:check`   | Lint Markdown files  |
| `task docs:fix`     | Fix Markdown issues  |
| `task commit:check` | Lint commit messages |
| `task skills`       | Install agent skills |

## Code Quality

- **Markdown**: `markdownlint-cli2` configured in `.markdownlint-cli2.yaml`.
- **Commits**: `commitlint` with the Conventional Commits ruleset configured
  in `.commitlintrc.yaml` (extending `@commitlint/config-conventional`),
  enforced by the `.husky/commit-msg` hook.
- **Tool Configs**: ESLint flat config defined in `eslint.config.ts` for
  validating TS, JSON, YAML and TOML tool files.

## Deployment

- **Releases**: [release-please](https://github.com/googleapis/release-please)
  drives versioning and changelogs for releases via
  `release-please-config.json` and `.release-please-manifest.json`.
