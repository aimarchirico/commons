# Commons

Shared building blocks for downstream software projects: published
libraries, configuration packages, provisioning CLIs, reusable GitHub
Actions, and a Claude Code plugin. Every piece encodes the same
[conventions](.github/CONTRIBUTING.md), so a downstream repository inherits
them instead of re-implementing them project by project.

## Install

Commons is not installed as a whole. Each subsystem is published separately
and pinned as a dependency downstream (or, for `plugin/`, installed
directly); its own README documents how.

To work on this repository, install [Task](https://taskfile.dev), then run
`pnpm install` in `tools/` to fetch the shared linting tooling.

Each subsystem needs its own toolchain, but only to work on that subsystem:
Java 25 for `maven/`, Node 20+ and PNPM 11.9 for `npm/`, and Python 3.13 for
`python/`.

## Usage

Run `task` from the repository root to list every available task. The
repository-wide ones:

| Command              | Description                             |
| :------------------- | :-------------------------------------- |
| `task docs:check`    | Lint Markdown files.                    |
| `task config:check`  | Lint configuration files.               |
| `task commit:check`  | Lint commit messages.                   |

Each subsystem exposes `check` and `fix` under its own namespace, such as
`task maven:check` or `task npm:fix`.

### Workspace

- [`tools/`](tools/README.md): shared linting configs and release tooling.
- [`.github/actions/`](.github/actions/README.md): shared GitHub Actions for
  CI/CD workflows.
- [`maven/`](maven/README.md): Kotlin backend modules and the convention
  plugin, published to the GitHub Packages Maven registry.
- [`npm/`](npm/README.md): frontend configuration packages and the API CLI,
  published to the GitHub Packages npm registry.
- [`python/`](python/README.md): shared Python tooling (ruff config + CLI),
  consumed as a git dependency pinned to `main`.
- [`plugin/`](plugin/README.md): the `commons` Claude Code plugin (skills
  and agents), added via `/plugin marketplace add`.

For how these fit together system-wide (release flow, infrastructure, domain
boundaries), see [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md).

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md).

## License

[MIT](LICENSE) © Aimár A. Chirico
