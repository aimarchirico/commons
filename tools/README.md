# Tools

Shared repository tooling: commit and Markdown linting, Git hooks, task
orchestration, and release automation for the monorepo. Contains no
application code.

## Install

Requires Node.js, pnpm, and [go-task](https://taskfile.dev). Install
dependencies with `pnpm install`.

Installing the `@aimarchirico`-scoped dependencies from GitHub Packages (see
`.npmrc`) requires an authenticated npm token. The Taskfile honors these
runtime variables:

| Variable             | Purpose                                        |
| :------------------- | :--------------------------------------------- |
| `CI`                 | Gates automatic dependency install             |
| `EDIT_FILE`          | Commit-message file passed to `commit:check`   |
| `FROM_SHA`/`TO_SHA`  | Commit range passed to `commit:check`          |

## Usage

Tasks are flattened into the root Taskfile and run from the repository root:

| Command               | Description                                |
| :-------------------- | :----------------------------------------- |
| `task docs:check`     | Lint Markdown files                        |
| `task docs:fix`       | Fix Markdown issues                        |
| `task config:check`   | Lint tool config files (TS/JSON/YAML/TOML) |
| `task config:fix`     | Fix tool config file issues                |
| `task commit:check`   | Lint commit messages                       |

## Development

### Tech Stack

| Technology            | Version  | Purpose                         |
| :-------------------- | :------- | :------------------------------ |
| pnpm                  | -        | Package manager                 |
| commitlint            | ^19.0.0  | Commit message linting          |
| config-conventional   | ^19.0.0  | Conventional Commits ruleset    |
| markdownlint-cli2     | ^0.23.0  | Markdown linting                |
| ESLint                | ^9.39.5  | Configuration file linting      |
| TypeScript            | ^6.0.3   | Typing support for ESLint       |
| Husky                 | ^9.1.7   | Git hooks                       |

### Folder Structure

```text
tools/
├── .husky/                        # Git hooks (commit-msg → commitlint)
├── Taskfile.yaml                  # Task command definitions
├── .commitlintrc.yaml             # commitlint configuration (extends config-conventional)
├── .markdownlint-cli2.yaml        # markdownlint configuration
├── eslint.config.ts               # ESLint configuration for tool configs (TS, JSON, YAML, TOML)
├── tsconfig.json                  # TypeScript configuration for ESLint
├── release-please-config.json     # release-please package config
├── .release-please-manifest.json  # release-please version manifest
├── pnpm-workspace.yaml            # Isolated tooling workspace
└── .npmrc                         # GitHub Packages registry
```

### Code Quality

- **Markdown**: `markdownlint-cli2` configured in `.markdownlint-cli2.yaml`
  (`task docs:check`).
- **Commits**: `commitlint` extending `@commitlint/config-conventional` via
  `.commitlintrc.yaml` (`task commit:check`).
- **Tool configs**: ESLint 9 flat config defined in `eslint.config.ts` for
  TS, JSON, YAML, and TOML tool files (`task config:check`).

## Deployment

[release-please](https://github.com/googleapis/release-please) drives
versioning and changelogs for releases via `release-please-config.json` and
`.release-please-manifest.json`.

## Contributing

See [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md).

## License

[MIT](../LICENSE) © Aimár A. Chirico
