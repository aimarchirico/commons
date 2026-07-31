# Plugin

The `commons` Claude Code plugin: reusable agent skills covering the
development lifecycle, the subagents they delegate to, and the bundled
Git/GitHub conventions they follow. This whole directory is the plugin
source — `.claude-plugin/marketplace.json` at the repository root points its
`source` here, so installing the plugin only fetches `plugin/`, not the rest
of the monorepo.

## Tech Stack

- **Markdown** `SKILL.md` definitions (`name`/`description`/`argument-hint`
  frontmatter, where `description` covers both what the skill does and when
  to use it, plus a `## Workflow` section) and agent `.md` definitions
  (`name`/`description` frontmatter plus free-form instructions).
- Packaged as a Claude Code plugin (`.claude-plugin/plugin.json`).
- **Python** 3.13, via `uv`, for scripts under `skills/issue/scripts/`.
  Static analysis config (ruff, ty, line-length) comes from the
  `commons-python` package rather than an in-repo config.
- Self-contained: `.github/` bundles this repository's own
  `CONTRIBUTING.md` and GitHub templates, so skills reference
  `${CLAUDE_PLUGIN_ROOT}/.github/...` directly instead of depending on the
  consumer repository having materialized anything.

## Folder Structure

```text
plugin/
├── .claude-plugin/plugin.json   # plugin manifest
├── .github/                     # bundled conventions (CONTRIBUTING.md, issue/PR templates)
├── skills/
│   ├── commit/SKILL.md          # create logical, atomic commits
│   ├── docs/SKILL.md            # update project documentation
│   ├── issue/SKILL.md           # create hierarchical issues
│   ├── pr/SKILL.md              # create a standardized pull request
│   ├── resolve/SKILL.md         # orchestrate the lifecycle from PR review feedback
│   ├── ship/SKILL.md            # chain issue creation and solving into a single flow
│   └── solve/SKILL.md           # orchestrate the lifecycle from an existing issue
└── agents/
    ├── planner.md                # drafts an implementation plan (read-only)
    └── worktree-runner.md        # implements an approved plan unattended
```

Each skill is a self-contained directory holding a single `SKILL.md`. Skills
rely on the conventions bundled in [`.github/`](.github) rather than on each
other, except for `solve`/`resolve` delegating to the `planner` and
`worktree-runner` agents in [`agents/`](agents), and `ship` delegating to the
`issue` and `solve` skills themselves.

`.github/` is currently a manual copy of
`npm/packages/commons-github/src/assets/` (`CONTRIBUTING.md` and the GitHub
templates) kept in sync by hand; it's copied rather than generated because
`commons-github` isn't published yet, so its `materialize-templates` command
isn't available to script the copy.

## Environment Variables

None.

## Local Development

Edit the relevant `SKILL.md` or agent `.md`. Consumers add the plugin once
and get every skill and agent in this directory:

```sh
/plugin marketplace add aimarchirico/commons
/plugin install commons@commons
```

## Code Quality

Markdown is linted with the shared `markdownlint` config via `task docs:check`
(and auto-fixed with `task docs:fix`) from the repository root. Python
scripts (`skills/issue/scripts/`) are checked with `task plugin:check` (and
fixed with `task plugin:fix`), which run ruff, ty, and the line-length
convention via the `commons-python` git dependency (see
[`python/commons-python`](../python/commons-python/README.md)) rather than
an in-repo ruff config.

## Deployment

The plugin is distributed directly from this repository, there is no
separate publish pipeline. `plugin.json` sets no `version`, so every merged
commit is a new version; consumers pick it up on their next
`/plugin marketplace update` or background auto-update.
