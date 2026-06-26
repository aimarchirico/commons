---
name: bootstrap
description: Initialize project documentation and the issue backlog
---

## When to Use

Use when the user asks to bootstrap or initalize the project, initialize documentation, or set up the issue backlog.

## Execution Steps

### 1. Preflight

Check if the `init/` directory and `CONTRIBUTING.md` exist in the repository root. If they are missing, copy them from the skill's own `resources/init` and `resources/CONTRIBUTING.md` to the repository root before proceeding.

### 2. Parse Flags

Determine which initialization steps to run:

- `--no-project`: skip Project Initialization.
- `--no-docs`: skip Documentation Initialization.
- `--no-issues`: skip Issue Backlog Initialization.

### 3. Project Initialization

1. Read `init/default.json` to understand the default settings.
2. Prompt the user to customize these settings, keeping only applicable modules in the configuration.
3. Save the customized configuration to `init/config.json`.
4. Execute `python -m init`.

### 4. Documentation Initialization

1. Use any previously gathered context and inspect the codebase to supplement with additional details.
2. If any details are still unclear or ambiguous, prompt the user for clarification.
3. Execute the `docs` skill to generate documentation, supplying the full context.

### 5. Issue Backlog Initialization

1. Read `README.md`, `docs/` files, and inspect any modules and CI/CD workflows to map requirements to backlog issues.
2. Execute the `issues` skill to draft and create the hierarchical backlog issues for the identified requirements.

## Supported Flags

- `--no-project`: Skip the project initialization step.
- `--no-docs`: Skip the documentation initialization step.
- `--no-issues`: Skip the issue backlog initialization step.
