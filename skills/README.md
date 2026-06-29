# Skills

Reusable agent skills covering the development lifecycle, consumed by downstream
repositories through a skills-capable agent runtime.

## Tech Stack

- **Markdown** `SKILL.md` definitions (name/description frontmatter plus
  execution steps).
- Consumed by skills-capable agent runtimes (e.g. Claude Code).

## Folder Structure

```text
skills/
├── commit/SKILL.md      # create logical, atomic commits
├── docs/SKILL.md        # update project documentation
├── implement/SKILL.md   # orchestrate the lifecycle from an existing issue
├── issues/SKILL.md      # create hierarchical issues
└── pr/SKILL.md          # create a standardized pull request
```

Each skill is a self-contained directory holding a single `SKILL.md`. Skills
rely on the conventions materialized by `@aimarchirico/core-docs`
(`CONTRIBUTING.md` and the GitHub templates) rather than on each other.

## Environment Variables

None.

## Local Development

Edit the relevant `SKILL.md`. Add a skill to a consumer repository with the
skills CLI:

```sh
npx skills add aimarchirico/core --skill <name>
```

## Code Quality

Markdown is linted with the shared `markdownlint` config via `task docs:check`
(and auto-fixed with `task docs:fix`) from the repository root.

## Deployment

Skills are distributed directly from this repository — there is no publish
pipeline. Consumers pull a skill on demand with the skills CLI, so changes are
available as soon as they are merged.
