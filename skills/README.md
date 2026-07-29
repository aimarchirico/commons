# Skills

Reusable agent skills covering the development lifecycle, distributed to
downstream repositories as the `commons` Claude Code plugin.

## Tech Stack

- **Markdown** `SKILL.md` definitions (`name`/`description`/`argument-hint`
  frontmatter, where `description` covers both what the skill does and when
  to use it, plus a `## Workflow` section).
- Packaged as a Claude Code plugin (`.claude-plugin/plugin.json` and
  `.claude-plugin/marketplace.json` at the repository root).
- `solve` and `resolve` delegate to the `planner` and `worktree-runner`
  agents in [`../agents/`](../agents), a sibling directory auto-discovered by
  the same plugin.

## Folder Structure

```text
skills/
├── commit/SKILL.md      # create logical, atomic commits
├── docs/SKILL.md        # update project documentation
├── issue/SKILL.md       # create hierarchical issues
├── pr/SKILL.md          # create a standardized pull request
├── resolve/SKILL.md     # orchestrate the lifecycle from PR review feedback
└── solve/SKILL.md       # orchestrate the lifecycle from an existing issue
```

Each skill is a self-contained directory holding a single `SKILL.md`. Skills
rely on the conventions materialized by `@aimarchirico/commons-docs`
(`CONTRIBUTING.md` and the GitHub templates) rather than on each other, except
for `solve`/`resolve` delegating to the shared agents noted above.

## Environment Variables

None.

## Local Development

Edit the relevant `SKILL.md`. Consumers add the plugin once and get every
skill in this directory:

```sh
/plugin marketplace add aimarchirico/commons
/plugin install commons@commons
```

## Code Quality

Markdown is linted with the shared `markdownlint` config via `task docs:check`
(and auto-fixed with `task docs:fix`) from the repository root.

## Deployment

Skills are distributed directly from this repository as a Claude Code plugin,
there is no separate publish pipeline. `plugin.json` sets no `version`, so
every merged commit is a new version; consumers pick it up on their next
`/plugin marketplace update` or background auto-update.
