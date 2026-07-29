# Skills

Reusable agent skills covering the development lifecycle, consumed by downstream
repositories through a skills-capable agent runtime.

## Tech Stack

- **Markdown** `SKILL.md` definitions (`name`/`description` frontmatter —
  `description` covers both what the skill does and when to use it — plus a
  `## Workflow` section).
- Consumed by skills-capable agent runtimes (e.g. Claude Code).

## Conventions

- **Flags**: Parsed from the freeform arguments string passed when a skill is
  invoked (e.g. `--issue 123 --auto`). Each skill documents its own flags
  under a `## Supported Flags` section in its `SKILL.md`.
- **Worktrees**: Skills that check out a branch (`resolve`, `solve`) do so in
  a dedicated git worktree at `<worktree-path>` = `../<branch-name>` (a
  sibling of the repository root) rather than switching the caller's current
  checkout, so the invoking repo's working tree is never disturbed.

## Folder Structure

```text
skills/
├── commit/SKILL.md      # create logical, atomic commits
├── docs/SKILL.md        # update project documentation
├── issues/SKILL.md      # create hierarchical issues
├── pr/SKILL.md          # create a standardized pull request
├── resolve/SKILL.md     # orchestrate the lifecycle from PR review feedback
└── solve/SKILL.md       # orchestrate the lifecycle from an existing issue
```

Each skill is a self-contained directory holding a single `SKILL.md`. Skills
rely on the conventions materialized by `@aimarchirico/commons-docs`
(`CONTRIBUTING.md` and the GitHub templates) rather than on each other.

## Environment Variables

None.

## Local Development

Edit the relevant `SKILL.md`. Add a skill to a consumer repository with the
skills CLI:

```sh
npx skills add aimarchirico/commons --skill <name>
```

## Code Quality

Markdown is linted with the shared `markdownlint` config via `task docs:check`
(and auto-fixed with `task docs:fix`) from the repository root.

## Deployment

Skills are distributed directly from this repository — there is no publish
pipeline. Consumers pull a skill on demand with the skills CLI, so changes are
available as soon as they are merged.
