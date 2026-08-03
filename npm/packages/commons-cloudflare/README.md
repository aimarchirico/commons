# commons-cloudflare

Cloudflare provisioning CLI, published as `@aimarchirico/commons-cloudflare`.
The package also exports a `./proxy` Pages Function and a `fix-assets` CLI for
web-export fixup; those are out of scope here — this README covers only the
provisioning commands below.

Every command takes no arguments, reads its inputs from `process.env`, fails
fast naming every missing variable at once, and is idempotent — a second run
makes no destructive change and reports each resource as created, updated, or
already present. Three of the four commands accept an optional
`CLOUDFLARE_ACCOUNT_ID`, derived automatically when the API token can see
exactly one account; supply it explicitly when the token has access to more
than one.

## `create-pages-project`

| Key                     | Required | Purpose                                           |
| :---------------------- | :------- | :--------------------------------------------------- |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Pages write and DNS scopes.            |
| `PAGES_PROJECT_NAME`    | Yes      | Pages project to create.                          |
| `PAGES_CUSTOM_DOMAIN`   | Yes      | Custom domain to attach.                          |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one. |

The production branch is derived from the remote's default branch, falling
back to `main` when there is no remote to ask. Creates the project and
attaches the domain, requesting automatic DNS.

## `set-pages-env`

| Key                     | Required | Purpose                                           |
| :---------------------- | :------- | :--------------------------------------------------- |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Pages write scope.                     |
| `PAGES_PROJECT_NAME`    | Yes      | Pages project to configure.                       |
| `PAGES_VARIABLES`       | Yes      | Names of the environment variables to push.       |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one. |

Always targets the `production` deployment config. Reads current values first
and reports each variable as created, updated, or already correct.

## `add-tunnel-route`

| Key                     | Required | Purpose                                              |
| :---------------------- | :------- | :------------------------------------------------------ |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with tunnel configuration write scope.         |
| `TUNNEL_ID`             | Yes      | Existing tunnel to add the rule to.                  |
| `TUNNEL_HOSTNAME`       | Yes      | Hostname to route.                                   |
| `TUNNEL_SERVICE`        | Yes      | Local service address, e.g. `http://localhost:8082`. |
| `TUNNEL_PATH`           | No       | Path to scope the rule to, e.g. `app`.               |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one.    |

A hostname with no `TUNNEL_PATH` matches every path, so one hostname can front
several backends by giving each a distinct `TUNNEL_PATH` (e.g.
`api.example.com/app` and `api.example.com/other`, each a separate invocation
with its own `TUNNEL_SERVICE`). The rule is keyed on the hostname+path pair;
inserts before the catch-all (and before any less-specific rule for the same
hostname) and preserves every existing rule. When the pair already routes to
the same service it makes no write at all.

## `create-service-token`

| Key                     | Required | Purpose                                        |
| :---------------------- | :------- | :------------------------------------------------ |
| `CLOUDFLARE_API_TOKEN`  | Yes      | Token with Access scope.                          |
| `SERVICE_TOKEN_NAME`    | Yes      | Service token to create.                          |
| `ACCESS_POLICY_ID`      | Yes      | Existing Access policy to attach the token to.    |
| `CLOUDFLARE_ACCOUNT_ID` | No       | Account. Derived when the token sees exactly one. |

Emits `CF_ACCESS_CLIENT_ID` and `CF_ACCESS_CLIENT_SECRET`. The secret is
returned only at creation, so an existing token is left alone and reported as
already present with its secret unreadable: reuse the stored value, or rotate
deliberately by deleting the token first. No Access application is created;
the account reuses one application for its APIs.

## Development

```bash
pnpm install
pnpm --filter @aimarchirico/commons-cloudflare check   # lint + typecheck + test
pnpm --filter @aimarchirico/commons-cloudflare fix      # auto-fix lint
```

Vitest enforces an 80% coverage floor on `services/`; `bin/` entrypoints are
excluded. Released by Release Please and published to the GitHub Packages npm
registry when a release touches this package's path.
