# Commons

Commons is a monorepo of shared building blocks for downstream software
projects: published Kotlin/Maven libraries, TypeScript/npm configuration
packages and provisioning CLIs, Python tooling, reusable GitHub Actions, and
a Claude Code agent-skill plugin covering the development lifecycle. Every
piece encodes the same conventions (see CONTRIBUTING.md), so a downstream
repository, such as the service template, inherits them instead of
re-implementing them project by project. The audience is developers building
or maintaining projects on top of it.

## Install

Commons is not installed as a whole; contributing to it requires
[Task](https://taskfile.dev), and each subsystem is instead consumed
individually, as an independently published unit that a downstream
repository pins as a dependency (or, for `plugin/`, installs directly). See
Usage below for the install method and prerequisites of each.

## Usage

Commons has no runnable UI of its own: it is a collection of published
libraries, configuration packages, and agent skills. What each subsystem
provides, how to install it, and how to consume it is documented in its own
README:

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

For how these pieces fit together system-wide (release flow, infrastructure,
domain boundaries), see [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Contributing

See [CONTRIBUTING.md](.github/CONTRIBUTING.md) for principles, documentation,
issue, branch, commit, and pull request conventions.

## License

[MIT](LICENSE)
