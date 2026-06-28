# Core

Reusable foundation for Chirico services: shared backend modules, frontend
packages, and agent skills consumed by downstream repositories such as the
service template.

## What's Inside

The repository is a monorepo with three roots:

- **`kotlin/`** — Gradle/Kotlin backend components published as Maven
  artifacts (`core-security`, `core-test`) plus the shared convention plugin
  (`core-build-logic`, applied as `id("core.kotlin")`).
- **`typescript/packages/`** — npm packages published to GitHub Packages. Each
  is an atomic CLI that owns its tooling logic and bundles its config, so
  consumers call a single command instead of re-spelling long invocations:
  - `@aimarchirico/core-ts` — `core-ts check`/`fix` (ESLint + TypeScript);
    also exports the shared `eslint` config and `tsconfig.json`.
  - `@aimarchirico/core-api` — `core-api` generates the OpenAPI client and docs.
  - `@aimarchirico/core-docs` — `core-docs check`/`fix`/`init` (Markdown lint
    plus the contributing guide and GitHub templates); also exports the shared
    `markdownlint` config. Each package ships a `Taskfile.yml` that consumers
    include from `node_modules` for cross-repo Task reuse.
- **`skills/`** — agent skills (`commit`, `docs`, `implement`, `issues`,
  `pr`) added to a consumer via `npx skills add aimarchirico/core --skill
  <name>`.

## Usage

Backend modules apply the convention plugin and depend on the libraries:

```kotlin
plugins { id("core.kotlin") }

dependencies {
  implementation("no.chirico.core:core-security")
  testImplementation("no.chirico.core:core-test")
}
```

Frontend packages expose configs (extended in eslint/tsconfig/markdownlint)
and CLIs:

```sh
npx core-ts check    # lint and type-check (strict when CI=1)
npx core-api         # generate the OpenAPI client and docs
npx core-docs check  # lint Markdown
npx core-docs init   # write CONTRIBUTING.md and .github templates into the repo
```

## Development

Requires Java 25, Node 20+, and [Task](https://taskfile.dev).

```sh
npm install
task check
```

- `task build` — build the backend modules.
- `task check` — run module tests, quality checks, and Markdown lint.
- `task fix` — format and auto-fix.

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md).
