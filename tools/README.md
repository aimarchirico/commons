# Tools

Shared repository tooling: commit and Markdown linting, Git hooks, task
orchestration, and release automation for the monorepo. Contains no
application code.

## Tech Stack

| Technology                  | Version | Purpose                       |
| :-------------------------- | :------ | :---------------------------- |
| pnpm                        | -       | Package manager               |
| Turborepo                   | ^2.10.2 | Monorepo task pipeline        |
| commitlint                  | ^19.3.0 | Commit message linting        |
| config-conventional         | ^21.2.0 | Conventional Commits ruleset  |
| markdownlint-cli2           | ^0.23.0 | Markdown linting              |
| Husky                       | ^9.1.7  | Git hooks                     |
| @aimarchirico/commons-tools | ^1.1.2  | Shared linting config presets |

## Folder Structure

```text
tools/
├── .husky/                        # Git hooks (commit-msg → commitlint)
├── Taskfile.yaml                   # Task command definitions
├── turbo.json                     # Turborepo pipeline
├── commitlint.config.js           # commitlint config (commons-tools preset)
├── .markdownlint-cli2.cjs         # markdownlint config (commons-tools preset)
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

- **Markdown**: `markdownlint-cli2` configured in `.markdownlint-cli2.cjs`,
  extending the `@aimarchirico/commons-tools` preset.
- **Commits**: `commitlint` with the Conventional Commits ruleset via the
  `@aimarchirico/commons-tools` preset, enforced by the `.husky/commit-msg`
  hook.

## Deployment

- **Releases**: [release-please](https://github.com/googleapis/release-please)
  drives versioning and changelogs for releases via
  `release-please-config.json` and `.release-please-manifest.json`.
