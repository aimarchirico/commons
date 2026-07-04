# .github

Reusable GitHub Actions workflows and composite actions consumed by downstream
service repositories. The workflows own the CI/CD *orchestration* (runner setup,
caching, path filtering, secret/variable plumbing, and the deploy steps) so a
consumer repo needs no pipeline YAML beyond a thin caller. The build *commands*
stay in the consumer as `task` targets — see [Consumer Contract](#consumer-contract).

## Folder Structure

```text
.github/
├── actions/            # composite actions (setup-java, setup-node)
├── workflows/
│   ├── ci.yml                 # commons' own CI
│   ├── release.yml            # commons' own release (publishes packages)
│   ├── reusable-ci.yml        # workflow_call: consumer CI
│   ├── reusable-release.yml   # workflow_call: consumer release
│   └── reusable-deploy.yml    # workflow_call: consumer deploy
├── ISSUE_TEMPLATE/     # shared issue templates
└── PULL_REQUEST_TEMPLATE.md
```

## Reusable Workflows

| Workflow               | Trigger in consumer     | Purpose                                              |
| :--------------------- | :---------------------- | :-------------------------------------------------- |
| `reusable-ci.yml`      | `pull_request`          | Changed-path detection + backend/frontend/docs/commit checks. |
| `reusable-release.yml` | `push` to `main`        | Release Please, API image, Android APK; outputs `paths_released`. |
| `reusable-deploy.yml`  | called by consumer deploy | API → VPS over SSH, web → Cloudflare Pages.         |

`reusable-release` exposes a `paths_released` output so the consumer's `release.yml`
gates its own deploy jobs and calls `reusable-deploy` (see the service template's
`release.yml`/`deploy.yml`), keeping all three workflow files thin callers.

Consumers invoke each with `uses:` + `secrets: inherit`. Example CI caller:

```yaml
name: CI
on:
  pull_request:
    branches: [main, dev]
permissions:
  contents: read
  packages: write
jobs:
  ci:
    uses: aimarchirico/commons/.github/workflows/reusable-ci.yml@main
    secrets: inherit
```

## Consumer Contract

The reusable workflows run the consumer's own `task` targets against the
consumer's checkout. A repo that adopts them **must** expose the following
targets (see the service template's `Taskfile.yml` for a reference
implementation):

| Task target        | Used by                | Purpose                              |
| :----------------- | :--------------------- | :----------------------------------- |
| `backend:check`    | `reusable-ci`          | Lint/test/build the backend module.  |
| `frontend:check`   | `reusable-ci`          | Lint/type-check the frontend module. |
| `docs:check`       | `reusable-ci`          | Lint Markdown docs.                  |
| `commit:check`     | `reusable-ci`          | Lint commit messages in the PR range. |
| `build:android`    | `reusable-release`     | Build the release Android APK.       |
| `build:web`        | `reusable-deploy`      | Build the web export for Cloudflare Pages. |

The task *names* are the interface; each consumer implements the commands behind
them however its codebase requires. Keeping the definitions in the consumer means
build logic lives next to the code it operates on, while commons owns only the
shared orchestration.

### Inputs

Names default to the consumer repository, so most callers pass no inputs.

| Workflow               | Input              | Default                     |
| :--------------------- | :----------------- | :-------------------------- |
| `reusable-ci`          | `filters`          | template backend/frontend/docs globs |
| `reusable-release`     | `api-image-name`   | `<repo>-api`                |
| `reusable-release`     | `apk-asset-prefix` | `<repo>`                    |
| `reusable-deploy`      | `deploy-api`       | `false`                     |
| `reusable-deploy`      | `deploy-web`       | `false`                     |
| `reusable-deploy`      | `compose-dir`      | `~/docker/<repo>`           |
| `reusable-deploy`      | `service-name`     | `<repo>-api`                |
| `reusable-deploy`      | `cf-project`       | `<repo>`                    |

### Secrets and Variables

Passed through with `secrets: inherit`; repository variables are read directly.

| Kind     | Names                                                                                  |
| :------- | :------------------------------------------------------------------------------------ |
| Secrets  | `GH_PACKAGES_TOKEN`, `CF_ACCESS_CLIENT_SECRET`, `VPS_SSH_KEY`, `CLOUDFLARE_API_TOKEN` |
| Variables | `API_URL`, `APP_URL`, `CF_ACCESS_CLIENT_ID`, `VPS_HOST`, `VPS_USER`, `CLOUDFLARE_ACCOUNT_ID` |
