# pnpm

Frontend configuration packages and tooling, published to GitHub Packages under
the `@aimarchirico` scope and managed as a pnpm workspace.

## Tech Stack

- **Node** 20+
- **pnpm** 11.9.0
- **TypeScript** 5
- **ESLint** 9
- **Turborepo** 2
- **openapi-generator-cli** 2.39 and **widdershins** 4 (used by `core-api`)

## Folder Structure

```text
pnpm/
├── packages/
│   ├── core-ts/           # shared ESLint + tsconfig (base config)
│   ├── core-expo/         # shared Expo / React Native ESLint + tsconfig
│   ├── core-tools/        # shared markdownlint + commitlint configs
│   ├── core-docs/         # documentation templates and materializer CLI
│   └── core-api/          # OpenAPI client/docs generator CLI
├── pnpm-workspace.yaml    # workspace globs (packages/*)
└── turbo.json             # check/fix task pipeline
```

| Package                          | Provides                                                                                   |
| :------------------------------- | :----------------------------------------------------------------------------------------- |
| `@aimarchirico/core-ts`          | `./eslint`, `./tsconfig.json` — base TypeScript config.                                     |
| `@aimarchirico/core-expo`        | `./eslint`, `./tsconfig.json` — Expo / React Native config.                                 |
| `@aimarchirico/core-tools`       | `./markdownlint`, `./commitlint` configs.                                                  |
| `@aimarchirico/core-docs`        | `core-docs` CLI (`bin/cli.js`) materializing `CONTRIBUTING.md` and GitHub templates.        |
| `@aimarchirico/core-api`         | `core-api` CLI (`bin/cli.js`) generating the OpenAPI client and docs.                       |

`core-expo`, `core-tools`, `core-docs`, and `core-api` extend `core-ts` as a
`workspace:*` dependency, so `core-ts` is the base every other package builds on.

## Environment Variables

No local `.env` is required. Publishing reads credentials from the environment
(injected by CI):

| Key               | Purpose                                |
| :---------------- | :------------------------------------- |
| `NODE_AUTH_TOKEN` | GitHub Packages (npm) publishing token. |

## Local Development

Requires Node 20+, pnpm 11.9, and [Task](https://taskfile.dev). Run from the
repository root:

- `pnpm install` — install workspace dependencies.
- `task pnpm:check` — lint and type-check all packages (`turbo run check`).
- `task pnpm:fix` — auto-fix all packages (`turbo run fix`).
- `task pnpm:publish PACKAGE=<name>` — publish a single package.

## Code Quality

- **Linting** — ESLint 9 flat config; every package extends the shared config
  from `core-ts`.
- **Types** — `tsc` against the shared `tsconfig.json`.
- **Caching** — Turborepo caches `check` runs (`turbo.json`).

## Deployment

Releases are driven by Release Please (`release-type: node`, separate PRs per
package) and published by `.github/workflows/release.yml` when a release touches
the matching `pnpm/packages/*` path. Publishing runs
`pnpm publish --filter <package>` against the GitHub Packages npm registry
(`https://npm.pkg.github.com`).
