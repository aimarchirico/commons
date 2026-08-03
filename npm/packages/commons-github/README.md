# commons-github

GitHub repository provisioning and documentation-materializer CLI, published as
`@aimarchirico/commons-github`. Requires `gh` 2.40+ on `PATH` (the GitHub CLI
Go binary — the `gh` package on npm is an unrelated project).

Run via the consuming repository's lockfile, not a floating version:

```bash
pnpm exec commons-github sync-variables
```

Every command takes no arguments, reads its inputs from `process.env`, fails
fast naming every missing variable at once, and is idempotent — a second run
makes no destructive change and reports each resource as already present. The
target repository is always derived from the working directory. See
[`docs/ARCHITECTURE.md`](../../../docs/ARCHITECTURE.md#data-flow) for how this
fits into the wider provisioning flow.

## `create-project`

Copies the public `aimarchirico/Commons Template` project and links it to the
repository, deriving the title from the repo name (`my-repo` → `My Repo`). No
env vars. Re-running finds and links an existing unlinked project instead of
duplicating it.

## `create-environments`

| Key                   | Required | Purpose                                      |
| :-------------------- | :------- | :--------------------------------------------- |
| `GITHUB_ENVIRONMENTS` | Yes      | Environment names, comma or space separated. |

Creates each environment, skipping any that already exist.

## `sync-variables`

| Key                            | Required | Purpose                                              |
| :----------------------------- | :------- | :------------------------------------------------------ |
| `GITHUB_VARIABLES`             | No       | Names of repository-level variables to push.         |
| `GITHUB_ENVIRONMENT_VARIABLES` | No       | Environment-scoped names, `env=NAME,NAME;env2=NAME`. |

Both name *other* env vars whose values get pushed. Reads current values
first and reports created/updated/already-correct; never removes a variable
the caller didn't mention.

## `set-secrets`

| Key                          | Required | Purpose                                              |
| :----------------------------- | :------- | :--------------------------------------------------- |
| `GITHUB_SECRETS`             | No       | Names of repository-level secrets to push.           |
| `GITHUB_ENVIRONMENT_SECRETS` | No       | Environment-scoped names, `env=NAME,NAME;env2=NAME`. |

Same naming convention as `sync-variables`. Secrets can't be read back, so
each write is reported as "written" rather than "unchanged."

## `materialize-templates`

Copies `CONTRIBUTING.md` and the issue/PR templates into the working
directory's `.github/`, overwriting anything already there. No env vars.

## Development

```bash
pnpm install
pnpm --filter @aimarchirico/commons-github check   # lint + typecheck + test
pnpm --filter @aimarchirico/commons-github fix      # auto-fix lint
```

Vitest enforces an 80% coverage floor on `services/`; `bin/` entrypoints are
excluded. Released by Release Please and published to the GitHub Packages npm
registry when a release touches this package's path.
