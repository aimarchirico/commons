# Core

## Introduction

Core is the reusable foundation for Chirico services. It centralizes the shared
backend modules, frontend configuration packages, and agent skills that
downstream repositories — such as the service template — depend on, so every
project inherits the same conventions instead of re-implementing them. The
audience is developers building or maintaining Chirico services.

## Demo

_Not applicable — Core is a collection of published libraries, configuration
packages, and agent skills with no runnable UI. Released artifacts are available
on GitHub Packages._

## Features

- **Backend libraries** — published Maven artifacts for security and test
  support, plus a shared Gradle/Kotlin convention plugin.
- **Frontend configs** — shared ESLint and TypeScript configuration for
  TypeScript and Expo / React Native projects.
- **Project conventions** — shared Markdown and commit lint rules, the
  contributing guide, and GitHub issue/PR templates.
- **API tooling** — a CLI that generates the OpenAPI client and docs.
- **Agent skills** — reusable skills covering the development lifecycle.

## Getting Started

Implementation-level setup and usage live in each subsystem's README:

- [`maven/`](maven/README.md) — Kotlin backend modules and the convention plugin.
- [`npm/`](npm/README.md) — frontend configuration packages and the API CLI.
- [`tools/`](tools/README.md) — shared linting configs and release tooling.
- [`skills/`](skills/README.md) — agent skills.

## Documentation

Extended, system-level documentation lives in [`docs/`](docs):

- [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md) — data flow, infrastructure
  overview, and project structure.

## Workflow

See [CONTRIBUTING.md](CONTRIBUTING.md) for documentation, issue, branch, commit,
and pull request conventions.
