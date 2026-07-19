# NPM

Frontend configuration packages and tooling, published to GitHub Packages under
the `@aimarchirico` scope and managed as a PNPM workspace.

## Tech Stack

- **Node** 20+
- **PNPM** 11.9.0
- **TypeScript** 6
- **ESLint** 9
- **Turborepo** 2
- **openapi-generator-cli** 2.39 and **widdershins** 4 (used by
  `commons-openapi`)

## Folder Structure

```text
npm/
├── packages/
│   ├── commons-ts/           # shared ESLint + tsconfig (base config)
│   ├── commons-expo/         # shared Expo / React Native ESLint + tsconfig
│   ├── commons-tools/        # shared markdownlint + commitlint configs
│   ├── commons-docs/         # documentation templates and materializer CLI
│   ├── commons-openapi/      # OpenAPI client/docs generator CLI
│   ├── commons-cloudflare/   # Cloudflare Pages proxy + web-export fixup
│   ├── commons-firebase-client/ # Firebase client initialization and CLI
│   └── commons-google-signin/   # Google Sign-In React hooks and context
├── pnpm-workspace.yaml    # workspace globs (packages/*)
└── turbo.json             # check/fix task pipeline
```

| Package                                 | Provides                                                                                                           |
| :-------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `@aimarchirico/commons-ts`              | `./eslint`, `./tsconfig.json` — base TypeScript config.                                                            |
| `@aimarchirico/commons-expo`            | `./eslint`, `./tsconfig.json` config + `commons-expo build-android` bin.                                           |
| `@aimarchirico/commons-tools`           | `./markdownlint`, `./commitlint` configs.                                                                          |
| `@aimarchirico/commons-docs`            | `commons-docs materialize-templates` bin (`dist/bin/cli.js`) materializing `CONTRIBUTING.md` and GitHub templates. |
| `@aimarchirico/commons-openapi`         | `commons-openapi generate-client` bin (`dist/bin/cli.js`) generating the OpenAPI client and docs.                  |
| `@aimarchirico/commons-cloudflare`      | `./proxy` Pages Function + `commons-cloudflare fix-assets` bin for Expo web deploys.                               |
| `@aimarchirico/commons-firebase-client` | Firebase client config and `commons-firebase-client decode-google-services` bin.                                   |
| `@aimarchirico/commons-google-signin`   | Google Sign-In React context and authentication hooks.                                                             |

`commons-expo`, `commons-tools`, `commons-docs`, and `commons-openapi` extend
`commons-ts` as a `workspace:*` dependency, so `commons-ts` is the base every
other package builds on.

## Environment Variables

No local `.env` is required. Publishing reads credentials from the environment
(injected by CI):

| Key               | Purpose                                 |
| :---------------- | :-------------------------------------- |
| `NODE_AUTH_TOKEN` | GitHub Packages (npm) publishing token. |

## Local Development

Requires Node 20+, PNPM 11.9, and [Task](https://taskfile.dev). Run from the
repository root:

- `pnpm install` — install workspace dependencies.
- `task npm:check` — lint and type-check all packages.
- `task npm:fix` — auto-fix all packages.
- `task npm:publish PACKAGE=<name>` — publish a single package.

## Code Quality

- **Linting** — ESLint 9 flat config; every package extends the shared config
  from `commons-ts`.
- **Types** — `tsc` against the shared `tsconfig.json`.
- **Caching** — Turborepo caches `check` runs (`turbo.json`).

## Deployment

Releases are driven by Release Please (`release-type: node`, separate PRs per
package) and published by `.github/workflows/release.yaml` when a release touches
the matching `npm/packages/*` path. Publishing runs
`pnpm publish --filter <package>` against the GitHub Packages npm registry
(`https://npm.pkg.github.com`).
