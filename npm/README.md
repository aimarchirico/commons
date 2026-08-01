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
│   ├── commons-openapi/      # OpenAPI client/docs generator CLI
│   ├── commons-cloudflare/   # Cloudflare Pages proxy, web-export fixup + provisioning CLI
│   ├── commons-project/      # project rename CLI + shared provisioning helpers
│   ├── commons-github/       # GitHub repository provisioning + documentation materializer CLI
│   ├── commons-firebase-client/ # Firebase client initialization and CLI
│   └── commons-google-signin/   # Google Sign-In React hooks and context
├── pnpm-workspace.yaml    # workspace globs (packages/*)
└── turbo.json             # check/fix task pipeline
```

| Package                                 | Provides                                                                                                                   |
| :-------------------------------------- | :------------------------------------------------------------------------------------------------------------------------- |
| `@aimarchirico/commons-ts`              | `./eslint`, `./tsconfig.json`, `./vitest-coverage` — base TypeScript config, including a shared 80% Vitest coverage floor. |
| `@aimarchirico/commons-expo`            | `./eslint`, `./tsconfig.json` config + `commons-expo build-android`, `create-project` and `import-keystore` bins.          |
| `@aimarchirico/commons-project`         | root exports (`env`, `report`, `outputs`, `cli`, `git` helpers) + `commons-project rename-project` bin.                    |
| `@aimarchirico/commons-github`          | `commons-github create-project`, `create-environments`, `sync-variables`, `set-secrets`, `materialize-templates` bins.     |
| `@aimarchirico/commons-tools`           | `./markdownlint`, `./commitlint` configs.                                                                                  |
| `@aimarchirico/commons-openapi`         | `commons-openapi generate-client` bin (`dist/bin/cli.js`) generating the OpenAPI client and docs.                          |
| `@aimarchirico/commons-cloudflare`      | `./proxy` Pages Function + `commons-cloudflare fix-assets` and provisioning bins.                                          |
| `@aimarchirico/commons-firebase-client` | Firebase client config and `commons-firebase-client decode-google-services` bin.                                           |
| `@aimarchirico/commons-google-signin`   | Google Sign-In React context and authentication hooks.                                                                     |

`commons-expo`, `commons-tools`, and `commons-openapi` extend
`commons-ts` as a `workspace:*` dependency, so `commons-ts` is the base every
other package builds on. `commons-ts` exports raw TypeScript consumed by ESLint
and `tsc`; the runtime helpers the provisioning commands share live in
`commons-project`, which compiles to `dist`.

## Provisioning Commands

Commands that provision the external resources a newly scaffolded project
needs. They are generic: no domain, account, tunnel, policy, naming
convention, or consuming-repository path appears in any of them.

**Every command takes no arguments.** Each reads its inputs from `process.env`,
fails fast naming every missing variable at once, and is idempotent — a second
run makes no destructive change and reports each resource as already present.
A downstream repository orchestrates them and supplies the values.

The consuming repository declares these packages as devDependencies, so run
them from its lockfile rather than resolving a floating version per run:

```bash
pnpm exec commons-github sync-variables
```

This also applies to `rename-project`, which runs after `pnpm install` on a
freshly generated repository: the replacement scan ignores `node_modules`, so
installing first is safe, and it means the template's own lockfile pins the
version of the tool that rewrites it. Re-run `pnpm install` afterwards when the
manifest moved workspace directories or renamed packages, since both invalidate
the links and `importers` entries recorded at install time.

Commands that produce values other steps consume write them as `KEY=value`
lines to the file named by `OUTPUT_FILE`, or print them with sensitive values
masked when it is unset.

Each command reports how it resolved the values it derives — the repository,
the Cloudflare account, the production branch — before it reports any resource,
so a derivation made in the wrong directory is visible before its consequences
are. Every derived value has an override.

Commands that drive a vendor CLI check its version first, since the output they
parse is version-specific and a floor turns a confusing parse failure into a
message naming what to fix.

`commons-expo` declares `eas-cli` as an optional peer dependency, so the
consuming repository pins it and the copy the lockfile resolved is the one that
runs — nothing needs installing globally. It is optional because this package
is also the shared ESLint and TypeScript config, and a project that only wants
those should not carry a provisioning CLI. `commons-github` needs `gh` 2.40+ on
`PATH`: the GitHub CLI is a Go binary, and the `gh` package on npm is an
unrelated project. Any tool resolved from a dependency falls back to `PATH`
when it is absent, so a global install still works where one exists.

### `commons-project rename-project`

Rewrites a generated repository from its template placeholder values to the
project's real values.

| Key             | Required | Purpose                                             |
| :-------------- | :------- | :-------------------------------------------------- |
| `MANIFEST_PATH` | No       | Manifest to execute. Defaults to `./manifest.json`. |

The manifest holds all layout knowledge and is validated in full before
anything is written:

```json
{
  "values": {
    "backendPackage": {"from": "no.chirico.template", "to": "no.chirico.myapp"},
    "backendName": {"from": "Template", "to": "My App"}
  },
  "replacements": [
    {"value": "backendPackage", "files": ["backend/**/*.kt"]},
    {
      "value": "backendName",
      "transforms": ["pascal", "lower"],
      "files": ["backend/**/*.kt", "backend/compose.prod.yaml"]
    }
  ],
  "moves": [
    {
      "from": "backend/app/src/main/kotlin/{{backendPackage|path}}",
      "to": "backend/app/src/main/kotlin/{{backendPackage|path}}"
    }
  ],
  "deletes": ["README.md"]
}
```

- `replacements` replace each value's literal variants across the matched
  globs. `transforms` selects which variants: `identity` (the default),
  `lower`, `kebab`, `snake`, `camel`, `pascal`, `title`, and `path` (a dotted
  identifier to path segments). An unknown transform fails with it named.
- `moves` interpolate `{{value}}`, `{{value|transform}}`, and
  `{{value.from|transform}}`. An unqualified placeholder takes the side of the
  field it appears in, so a move's `from` reads source values and its `to`
  reads target values.
- Re-running a completed rename finds nothing to change and reports a no-op,
  since the source values are gone.

### `commons-github create-project`

Copies the public `aimarchirico/Commons Template` project, the source of
truth every scaffolded project's board is copied from, and links the copy.
The project's title is derived from the repository name, e.g. `my-repo`
becomes `My Repo`. The target repository is derived from the working
directory.

Takes no environment variables.

On a re-run it reports the already-linked project. If a project with the title
exists but is unlinked it links it.

### `commons-github create-environments`

| Key                   | Required | Purpose                                      |
| :-------------------- | :------- | :------------------------------------------- |
| `GITHUB_ENVIRONMENTS` | Yes      | Environment names, comma or space separated. |

Creates each environment, skipping any that already exists. The target
repository is derived from the working directory.

### `commons-github sync-variables`

| Key                            | Required | Purpose                                              |
| :----------------------------- | :------- | :--------------------------------------------------- |
| `GITHUB_VARIABLES`             | No       | Names of repository-level variables to push.         |
| `GITHUB_ENVIRONMENT_VARIABLES` | No       | Environment-scoped names, `env=NAME,NAME;env2=NAME`. |

Both variables name *other* environment variables, whose values are the values
pushed. Current values are read first, so each variable is reported as created,
updated, or already correct. Variables the caller did not mention are never
removed, and a name absent from the environment is skipped. The target
repository is derived from the working directory.

### `commons-github set-secrets`

| Key                          | Required | Purpose                                              |
| :--------------------------- | :------- | :--------------------------------------------------- |
| `GITHUB_SECRETS`             | No       | Names of repository-level secrets to push.           |
| `GITHUB_ENVIRONMENT_SECRETS` | No       | Environment-scoped names, `env=NAME,NAME;env2=NAME`. |

Same naming convention as `sync-variables`, and the target repository is
likewise derived from the working directory. A secret's current value cannot be
read back, so each is reported as written rather than unchanged; a name absent
from the environment is skipped rather than blanking a working value.

### `commons-github materialize-templates`

Takes no environment variables. Copies `CONTRIBUTING.md` and the
`ISSUE_TEMPLATE`/`PULL_REQUEST_TEMPLATE.md` templates into the working
directory's `.github/`, overwriting anything already there.

### `commons-cloudflare create-pages-project`

| Key                     | Required | Purpose                                           |
| :---------------------- | :------- | :------------------------------------------------ |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Pages write and DNS scopes.            |
| `PAGES_PROJECT_NAME`    | Yes      | Pages project to create.                          |
| `PAGES_CUSTOM_DOMAIN`   | Yes      | Custom domain to attach.                          |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one. |

The production branch is derived from the remote's default branch, falling
back to `main` when there is no remote to ask.

Creates the project and attaches the domain, requesting automatic DNS, and
reports each as created or already present.

### `commons-cloudflare set-pages-env`

| Key                     | Required | Purpose                                           |
| :---------------------- | :------- | :------------------------------------------------ |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Pages write scope.                     |
| `PAGES_PROJECT_NAME`    | Yes      | Pages project to configure.                       |
| `PAGES_VARIABLES`       | Yes      | Names of the environment variables to push.       |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one. |

Always targets the `production` deployment config. Reads current values first
and reports each variable as created, updated, or already correct.

### `commons-cloudflare add-tunnel-route`

| Key                     | Required | Purpose                                              |
| :---------------------- | :------- | :--------------------------------------------------- |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with tunnel configuration write scope.         |
| `TUNNEL_ID`             | Yes      | Existing tunnel to add the rule to.                  |
| `TUNNEL_HOSTNAME`       | Yes      | Hostname to route.                                   |
| `TUNNEL_SERVICE`        | Yes      | Local service address, e.g. `http://localhost:8082`. |
| `TUNNEL_PATH`           | No       | Path to scope the rule to, e.g. `app`.               |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one.    |

A hostname with no `TUNNEL_PATH` matches every path, so one hostname can front
several backends by giving each a distinct `TUNNEL_PATH` (e.g. `api.example.com/app`
and `api.example.com/other`, each a separate invocation with its own `TUNNEL_SERVICE`).
The rule is keyed on the hostname+path pair; inserts before the catch-all (and
before any less-specific rule for the same hostname) and preserves every
existing rule. When the pair already routes to the same service it makes no
write at all.

### `commons-cloudflare create-service-token`

| Key                     | Required | Purpose                                           |
| :---------------------- | :------- | :------------------------------------------------ |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Access scope.                          |
| `SERVICE_TOKEN_NAME`    | Yes      | Service token to create.                          |
| `ACCESS_POLICY_ID`      | Yes      | Existing Access policy to attach the token to.    |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one. |

Emits `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET`. The secret is
returned only at creation, so an existing token is left alone and reported as
already present with its secret unreadable — reuse the stored value, or rotate
deliberately by deleting the token first. No Access application is created; the
account reuses one application for its APIs.

### `commons-expo create-project`

| Key          | Required | Purpose                                                          |
| :----------- | :------- | :--------------------------------------------------------------- |
| `EXPO_TOKEN` | No       | Expo credentials. Falls back to a `pnpm exec eas login` session. |

Emits `EAS_PROJECT_ID`.

Runs `eas init`, which links the project when `@account/slug` already exists and
creates it otherwise, writing `extra.eas.projectId` into the app config. The
account is resolved by eas-cli itself from the authenticated token; `eas init`
fails naming the choices when the token can see more than one.

### `commons-expo import-keystore`

| Key                       | Required | Purpose                                                       |
| :------------------------ | :------- | :------------------------------------------------------------ |
| `ANDROID_KEYSTORE_BASE64` | No       | An already-provisioned keystore. Present means nothing to do. |

Reads credentials from `credentials.json` in the working directory.

Emits `ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`,
`ANDROID_KEY_ALIAS`, and `ANDROID_KEY_PASSWORD`, for `set-secrets` to store.

EAS is the store of record, and the keystore is also pushed to GitHub secrets
because the build signs locally with Gradle. Keeping both means the signing key
survives losing either: GitHub secrets cannot be read back, and losing an
Android signing key ends updates for every installed copy of the app.

Creating and downloading the keystore is the one step eas-cli exposes only
through its interactive menu — and the entry next to "Download existing
keystore" is "Delete your keystore", so this command does not drive that menu
unattended. When there is nothing to import it prints the exact steps and
reports `action required`, which is distinct from a failure. On the re-run it
reads the four values out of `credentials.json`, emits them, and removes both
the JSON and the `.jks` from the working tree.

`build-android` fails rather than falling back to debug signing when
`ANDROID_KEYSTORE_BASE64` is unset, so provisioning that never reached this
command cannot quietly ship a debug-signed release. Set `ANDROID_ALLOW_UNSIGNED`
to build unsigned on purpose.

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
- **Documentation** — every exported top-level function, class, interface,
  type alias, enum, and `const`/`let`/`var`, plus every public member of an
  exported class, needs a JSDoc block (`jsdoc/require-jsdoc`, configured with
  `contexts` to reach the TypeScript-only constructs beyond what its `require`
  option covers). Any JSDoc block present is checked for correctness:
  matching `@param`/`@returns` tags, valid type syntax, and known tag names
  (`jsdoc/check-param-names`, `jsdoc/check-tag-names`, `jsdoc/check-types`,
  `jsdoc/require-param`, `jsdoc/require-returns`, `jsdoc/valid-types`).
- **Comments** — only JSDoc blocks documenting one of the declarations above
  are allowed (`commons/public-jsdoc-only`). Line and block comments are
  rejected wherever they appear, on their own line or trailing code, so
  explanation stays attached to what it describes; a JSDoc block that
  documents nothing, or that sits on a non-exported/non-public declaration, is
  rejected the same way. This mirrors `jsdoc/require-jsdoc` exactly: whatever
  is required to have a doc comment is also the only thing allowed to have
  one. Tooling directives such as `eslint-disable` and `@ts-expect-error`
  remain legal, because the tools that read them recognise only the plain
  forms.
- **Suppression discipline** — `eslint-disable` comments must state why
  (`@eslint-community/eslint-comments/require-description`), may not disable
  more than the rules actually violated
  (`@eslint-community/eslint-comments/no-unlimited-disable`), and are flagged
  once they stop suppressing anything
  (`@eslint-community/eslint-comments/no-unused-disable`). `@ts-expect-error`
  requires a description of at least 10 characters
  (`@typescript-eslint/ban-ts-comment`, `minimumDescriptionLength: 10`);
  `@ts-ignore` and `@ts-nocheck` are banned outright, since they silence
  errors without requiring the compiler to confirm one exists; `@ts-check` is
  allowed.
- **Types** — `tsc` against the shared `tsconfig.json`.
- **Testing** — Vitest, with an 80% line/function/branch/statement coverage
  floor enforced by `commons-ts`'s shared `./vitest-coverage` config
  (`vitest run`, part of every package's `check` script). `bin/`
  entrypoints and declarative config/asset re-exports are excluded from the
  threshold; the coverage bar applies to `services/`/`lib/` logic.
- **Caching** — Turborepo caches `check` runs (`turbo.json`).

## Deployment

Releases are driven by Release Please (`release-type: node`, separate PRs per
package) and published by `.github/workflows/release.yaml` when a release touches
the matching `npm/packages/*` path. Publishing runs
`pnpm publish --filter <package>` against the GitHub Packages npm registry
(`https://npm.pkg.github.com`).
