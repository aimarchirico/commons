# tools

Shared tooling configuration and release orchestration for the Core monorepo.
Owns the markdownlint and commitlint configs consumed by all subsystems, and
holds the Release Please config and manifest that drive versioned releases.

## Tech Stack

- **Node** 20+
- **PNPM** 11.9.0
- **markdownlint-cli2** 0.13+
- **@commitlint/cli** 19+
- **@aimarchirico/core-tools** (markdownlint + commitlint presets)

## Folder Structure

```text
tools/
├── .markdownlint-cli2.cjs         # re-exports @aimarchirico/core-tools/markdownlint
├── commitlint.config.js           # re-exports @aimarchirico/core-tools/commitlint
├── release-please-config.json     # Release Please package config for all subsystems
├── .release-please-manifest.json  # Release Please version manifest
├── Taskfile.yml                   # docs:check, docs:fix, commit:check tasks
└── package.json
```

## Environment Variables

No local `.env` is required. The CI workflows inject all needed credentials.

## Local Development

Requires Node 20+, PNPM 11.9, and [Task](https://taskfile.dev). Run from the
repository root (tasks are flattened into the root namespace):

- `task docs:check` — lint all Markdown files in the repository.
- `task docs:fix` — auto-fix Markdown issues.
- `task commit:check` — lint commit messages (`FROM_SHA`/`TO_SHA` env vars
  select the range; omit for the latest commit only).

## Code Quality

- **Markdown** — markdownlint-cli2 using the `@aimarchirico/core-tools/markdownlint`
  preset, scoped to `../**/*.md` from the `tools/` working directory.
- **Commits** — commitlint using the `@aimarchirico/core-tools/commitlint` preset,
  enforcing Conventional Commits across the monorepo.

## Deployment

This workspace is not published to any registry. It drives releases for all
other subsystems via Release Please: `tools/release-please-config.json` declares
each publishable package and `tools/.release-please-manifest.json` tracks their
current versions. The `.github/workflows/release.yml` workflow references both
files when running the `googleapis/release-please-action`.
