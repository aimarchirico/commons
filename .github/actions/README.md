# GitHub Actions

Shared, reusable GitHub Actions meant to be utilized across projects for
CI/CD.

## Install

No installation step: reference an action directly from a workflow via
`uses: aimarchirico/commons/.github/actions/<name>@main` (or a pinned release
tag). Each action's `inputs` and required secrets are declared in its own
`action.yaml`; dependencies vary per action, so check that file before
wiring one in.

## Usage

Each directory is a standalone reusable action:

- `android-release/`: Builds and releases an Android application.
- `assign-sub-issues/`: Cascades newly-added assignees to nested sub-issues.
- `close-sub-issues/`: Cascade closes nested sub-issues.
- `cloudflare-deploy/`: Deploys applications to Cloudflare.
- `docker-release/`: Builds and pushes Docker images.
- `java-task/`: Reusable Java CI tasks.
- `move-sub-issues-in-progress/`: Cascades the board's In Progress status to
  nested sub-issues.
- `node-task/`: Reusable Node.js CI tasks.
- `self-review-signal/`: Submits a real review matching a posted verdict comment.
- `vps-deploy/`: Deploys applications to a VPS.

## Development

- **Tech stack**: GitHub Actions YAML-based workflows and composite actions,
  with shell/Bash scripts for task execution.
- **Local testing**: actions run primarily in the GitHub CI environment; for
  local testing, use a tool like [act](https://github.com/nektos/act).
- **Editing**: modify the corresponding `action.yaml` and its associated
  scripts within its directory.
- **Code quality**: all YAML files and shell scripts are verified by the
  repository's root CI workflows. YAML files follow standard formatting and
  shell scripts are documented.

## Deployment

Changes to these actions take effect once merged into the `main` branch.
Downstream repositories utilizing these actions pick up the updates based on
the branch or version tag they target (e.g., `@main` or a specific release
tag).

## Contributing

See [CONTRIBUTING.md](../../.github/CONTRIBUTING.md).

## License

[MIT](../../LICENSE)
