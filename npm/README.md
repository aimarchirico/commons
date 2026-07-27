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
│   ├── commons-cloudflare/   # Cloudflare Pages proxy, web-export fixup + provisioning CLI
│   ├── commons-project/      # project rename CLI + shared provisioning helpers
│   ├── commons-github/       # GitHub repository provisioning CLI
│   ├── commons-firebase-client/ # Firebase client initialization and CLI
│   └── commons-google-signin/   # Google Sign-In React hooks and context
├── pnpm-workspace.yaml    # workspace globs (packages/*)
└── turbo.json             # check/fix task pipeline
```

| Package                                 | Provides                                                                                                           |
| :-------------------------------------- | :----------------------------------------------------------------------------------------------------------------- |
| `@aimarchirico/commons-ts`              | `./eslint`, `./tsconfig.json` — base TypeScript config.                                                            |
| `@aimarchirico/commons-expo`            | `./eslint`, `./tsconfig.json` config + `commons-expo build-android` and `create-keystore` bins.                    |
| `@aimarchirico/commons-project`         | root exports (`env`, `report`, `outputs` helpers) + `commons-project rename-project` bin.                          |
| `@aimarchirico/commons-github`          | `commons-github create-project`, `create-environments`, `sync-variables`, `set-secrets` bins.                      |
| `@aimarchirico/commons-tools`           | `./markdownlint`, `./commitlint` configs.                                                                          |
| `@aimarchirico/commons-docs`            | `commons-docs materialize-templates` bin (`dist/bin/cli.js`) materializing `CONTRIBUTING.md` and GitHub templates. |
| `@aimarchirico/commons-openapi`         | `commons-openapi generate-client` bin (`dist/bin/cli.js`) generating the OpenAPI client and docs.                  |
| `@aimarchirico/commons-cloudflare`      | `./proxy` Pages Function + `commons-cloudflare fix-assets` and provisioning bins.                                  |
| `@aimarchirico/commons-firebase-client` | Firebase client config and `commons-firebase-client decode-google-services` bin.                                   |
| `@aimarchirico/commons-google-signin`   | Google Sign-In React context and authentication hooks.                                                             |

`commons-expo`, `commons-tools`, `commons-docs`, and `commons-openapi` extend
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

Run them with `npx`, for example:

```bash
npx @aimarchirico/commons-github sync-variables
```

Commands that produce values other steps consume write them as `KEY=value`
lines to the file named by `OUTPUT_FILE`, or print them with sensitive values
masked when it is unset.

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

Copies the project linked to the repository this one was generated from and
links the copy.

| Key                     | Required | Purpose                                                              |
| :---------------------- | :------- | :------------------------------------------------------------------- |
| `PROJECT_TITLE`         | Yes      | Title of the project to find or create.                              |
| `GITHUB_REPOSITORY`     | No       | Target `owner/repo`. Defaults to the working directory's repository. |
| `PROJECT_SOURCE_OWNER`  | No       | Overrides the source owner instead of resolving the template.        |
| `PROJECT_SOURCE_NUMBER` | No       | Overrides the source project number.                                 |

On a re-run it reports the already-linked project. If a project with the title
exists but is unlinked it links it; the template relationship it would
otherwise resolve is only readable for a freshly generated repository, which is
what the overrides are for.

### `commons-github create-environments`

| Key                   | Required | Purpose                                      |
| :-------------------- | :------- | :------------------------------------------- |
| `GITHUB_ENVIRONMENTS` | Yes      | Environment names, comma or space separated. |
| `GITHUB_REPOSITORY`   | No       | Target `owner/repo`.                         |

Creates each environment, skipping any that already exists.

### `commons-github sync-variables`

| Key                            | Required | Purpose                                              |
| :----------------------------- | :------- | :--------------------------------------------------- |
| `GITHUB_VARIABLES`             | No       | Names of repository-level variables to push.         |
| `GITHUB_ENVIRONMENT_VARIABLES` | No       | Environment-scoped names, `env=NAME,NAME;env2=NAME`. |
| `GITHUB_REPOSITORY`            | No       | Target `owner/repo`.                                 |

Both variables name *other* environment variables, whose values are the values
pushed. Current values are read first, so each variable is reported as created,
updated, or already correct. Variables the caller did not mention are never
removed, and a name absent from the environment is skipped.

### `commons-github set-secrets`

| Key                          | Required | Purpose                                              |
| :--------------------------- | :------- | :--------------------------------------------------- |
| `GITHUB_SECRETS`             | No       | Names of repository-level secrets to push.           |
| `GITHUB_ENVIRONMENT_SECRETS` | No       | Environment-scoped names, `env=NAME,NAME;env2=NAME`. |
| `GITHUB_REPOSITORY`          | No       | Target `owner/repo`.                                 |

Same naming convention as `sync-variables`. A secret's current value cannot be
read back, so each is reported as written rather than unchanged; a name absent
from the environment is skipped rather than blanking a working value.

### `commons-cloudflare create-pages-project`

| Key                       | Required | Purpose                                |
| :------------------------ | :------- | :------------------------------------- |
| `CLOUDFLARE_ACCOUNT_ID`   | Yes      | Account owning the Pages project.      |
| `CLOUDFLARE_API_TOKEN`    | Yes      | Token with Pages write and DNS scopes. |
| `PAGES_PROJECT_NAME`      | Yes      | Pages project to create.               |
| `PAGES_CUSTOM_DOMAIN`     | Yes      | Custom domain to attach.               |
| `PAGES_PRODUCTION_BRANCH` | No       | Production branch. Defaults to `main`. |

Creates the project and attaches the domain, requesting automatic DNS, and
reports each as created or already present.

### `commons-cloudflare set-pages-env`

| Key                     | Required | Purpose                                                |
| :---------------------- | :------- | :----------------------------------------------------- |
| `CLOUDFLARE_ACCOUNT_ID` | Yes      | Account owning the Pages project.                      |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Pages write scope.                          |
| `PAGES_PROJECT_NAME`    | Yes      | Pages project to configure.                            |
| `PAGES_VARIABLES`       | Yes      | Names of the environment variables to push.            |
| `PAGES_ENVIRONMENT`     | No       | Deployment config to target. Defaults to `production`. |

Reads current values first and reports each variable as created, updated, or
already correct.

### `commons-cloudflare add-tunnel-route`

| Key                     | Required | Purpose                                              |
| :---------------------- | :------- | :--------------------------------------------------- |
| `CLOUDFLARE_ACCOUNT_ID` | Yes      | Account owning the tunnel.                           |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with tunnel configuration write scope.         |
| `TUNNEL_ID`             | Yes      | Existing tunnel to add the rule to.                  |
| `TUNNEL_HOSTNAME`       | Yes      | Hostname to route.                                   |
| `TUNNEL_SERVICE`        | Yes      | Local service address, e.g. `http://localhost:8082`. |

Inserts the rule before the catch-all and preserves every existing rule. When
the hostname already routes to the same service it makes no write at all.

### `commons-cloudflare create-service-token`

| Key                     | Required | Purpose                                        |
| :---------------------- | :------- | :--------------------------------------------- |
| `CLOUDFLARE_ACCOUNT_ID` | Yes      | Account owning the Access token.               |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Access scope.                       |
| `SERVICE_TOKEN_NAME`    | Yes      | Service token to create.                       |
| `ACCESS_POLICY_ID`      | Yes      | Existing Access policy to attach the token to. |

Emits `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET`. The secret is
returned only at creation, so an existing token is left alone and reported as
already present with its secret unreadable — reuse the stored value, or rotate
deliberately by deleting the token first. No Access application is created; the
account reuses one application for its APIs.

### `commons-expo create-keystore`

| Key                              | Required | Purpose                                                        |
| :------------------------------- | :------- | :------------------------------------------------------------- |
| `EAS_PROJECT_ID`                 | Yes      | EAS project (app) the keystore belongs to.                     |
| `ANDROID_APPLICATION_ID`         | Yes      | Android package the credentials apply to.                      |
| `EXPO_TOKEN`                     | No       | Expo credentials. Falls back to the local `eas login` session. |
| `ANDROID_BUILD_CREDENTIALS_NAME` | No       | Build credentials to use. Defaults to `production`.            |
| `ANDROID_KEY_ALIAS`              | No       | Key alias for a new keystore. Defaults to `release`.           |
| `ANDROID_KEYSTORE_PASSWORD`      | No       | Store password. Generated when creating a new keystore.        |
| `ANDROID_KEY_PASSWORD`           | No       | Key password. Defaults to the store password.                  |
| `ANDROID_KEY_DNAME`              | No       | Certificate subject. Defaults to `CN=<alias>`.                 |

Emits `ANDROID_KEY_ALIAS`, `ANDROID_KEYSTORE_BASE64`,
`ANDROID_KEYSTORE_PASSWORD`, and `ANDROID_KEY_PASSWORD`.

EAS is the store of record. The keystore is generated with `keytool` and stored
through the Expo API as the named build credentials for the app, so no signing
key is left on disk — the temporary file `keytool` requires is removed
immediately. Later runs read the stored keystore back and report it as already
present. An existing keystore is never regenerated, since replacing signing keys
breaks updates for every installed copy of the app.

These are the same records the interactive `eas credentials` flow creates, so a
keystore created either way is visible and downloadable through the other. The
CLI cannot be used here: `eas credentials` hardcodes interactive mode and exposes
no keystore flags.

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
