# commons-expo

Shared Expo / React Native ESLint and `tsconfig.json` config, published as
`@aimarchirico/commons-expo`, plus a provisioning CLI and a `build-android`
bin.

The provisioning commands below take no arguments, read their inputs from
`process.env`, fail fast naming every missing variable at once, and are
idempotent — a second run makes no destructive change and reports each
resource as created, updated, or already present. `eas-cli` is an optional
peer dependency: the consuming repository pins it and the copy its lockfile
resolved is the one that runs, falling back to `PATH` when none is pinned.
It's optional because this package doubles as the shared lint/tsconfig config,
and a project that only wants that shouldn't be forced to carry a
provisioning CLI dependency.

## `create-project`

| Key          | Required | Purpose                                                          |
| :----------- | :------- | :--------------------------------------------------------------- |
| `EXPO_TOKEN` | No       | Expo credentials. Falls back to a `pnpm exec eas login` session. |

Emits `EAS_PROJECT_ID`. Runs `eas init`, which links the project when
`@account/slug` already exists and creates it otherwise, writing
`extra.eas.projectId` into the app config. The account is resolved by
eas-cli itself from the authenticated token; `eas init` fails naming the
choices when the token can see more than one.

## `import-keystore`

| Key                       | Required | Purpose                                                       |
| :------------------------ | :------- | :------------------------------------------------------------ |
| `ANDROID_KEYSTORE_BASE64` | No       | An already-provisioned keystore. Present means nothing to do. |

Reads credentials from `credentials.json` in the working directory and emits
`ANDROID_KEYSTORE_BASE64`, `ANDROID_KEYSTORE_PASSWORD`, `ANDROID_KEY_ALIAS`,
and `ANDROID_KEY_PASSWORD` for `set-secrets` to store.

EAS is the store of record, and the keystore is also pushed to GitHub secrets
because the build signs locally with Gradle. Keeping both means the signing
key survives losing either: GitHub secrets can't be read back, and losing an
Android signing key ends updates for every installed copy of the app.

Creating and downloading the keystore is the one step eas-cli exposes only
through its interactive menu, where the entry next to "Download existing
keystore" is "Delete your keystore", so this command does not drive that menu
unattended. When there is nothing to import it prints the exact steps and
reports `action required`, which is distinct from a failure. On a re-run it
reads the four values out of `credentials.json`, emits them, and removes both
the JSON and the `.jks` from the working tree.

`build-android` fails rather than falling back to debug signing when
`ANDROID_KEYSTORE_BASE64` is unset, so provisioning that never reached this
command cannot quietly ship a debug-signed release. Set
`ANDROID_ALLOW_UNSIGNED` to build unsigned on purpose.

## Development

```bash
pnpm install
pnpm --filter @aimarchirico/commons-expo check   # lint + typecheck + test
pnpm --filter @aimarchirico/commons-expo fix      # auto-fix lint
```

Vitest enforces an 80% coverage floor on `services/`; `bin/` entrypoints are
excluded. Released by Release Please and published to the GitHub Packages npm
registry when a release touches this package's path.
