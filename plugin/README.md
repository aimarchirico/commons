# Plugin

The `commons` Claude Code plugin: reusable agent skills covering the
development lifecycle, the subagents they delegate to, and the bundled
Git/GitHub conventions they follow. This whole directory is the plugin
source: `.claude-plugin/marketplace.json` at the repository root points its
`source` here, so installing the plugin only fetches `plugin/`, not the rest
of the monorepo.

## Tech Stack

- **Markdown** `SKILL.md` definitions (`name`/`description`/`argument-hint`
  frontmatter, where `description` covers both what the skill does and when
  to use it, plus a `## Workflow` section) and agent `.md` definitions
  (`name`/`description` frontmatter plus free-form instructions).
- Packaged as a Claude Code plugin (`.claude-plugin/plugin.json`).
- **Python** 3.13, via `uv`, for scripts under `skills/*/scripts/`. Static
  analysis config (ruff, ty, line-length) comes from the `commons-python`
  package rather than an in-repo config.
- Self-contained: `.github/` bundles this repository's own
  `CONTRIBUTING.md` and GitHub templates, so skills reference
  `${CLAUDE_PLUGIN_ROOT}/.github/...` directly instead of depending on the
  consumer repository having materialized anything.

## Folder Structure

```text
plugin/
├── .claude-plugin/plugin.json   # plugin manifest
├── .github/                     # bundled conventions (CONTRIBUTING.md, issue/PR templates)
├── shared/                      # shared script utilities (pr_feedback.py)
├── skills/
│   ├── check/SKILL.md           # verify the tree against the project's own PR-gating CI checks
│   ├── commit/SKILL.md          # create logical, atomic commits
│   ├── docs/SKILL.md            # update project documentation
│   ├── issue/SKILL.md           # create hierarchical issues
│   ├── pr/SKILL.md              # create a standardized pull request
│   ├── resolve/SKILL.md         # orchestrate the lifecycle from PR review feedback
│   ├── review/SKILL.md          # review a pull request via parallel reviewer agents
│   ├── ship/SKILL.md            # chain issue creation and solving into a single flow
│   ├── solve/SKILL.md           # orchestrate the lifecycle from an existing issue
│   ├── spec/SKILL.md            # draft requirements/architecture/decisions for a new project
│   └── triage/SKILL.md          # survey open PRs and Backlog issues, read-only
└── agents/
    ├── compliance-reviewer.md    # reviews a diff against CONTRIBUTING.md (read-only)
    ├── implementation-planner.md # drafts an implementation plan (read-only)
    ├── logic-reviewer.md         # reviews a diff for logic errors (read-only)
    ├── performance-reviewer.md   # reviews a diff for performance regressions (read-only)
    ├── security-reviewer.md      # reviews a diff for security vulnerabilities (read-only)
    └── worktree-runner.md        # implements an approved plan unattended
```

Each skill directory contains a `SKILL.md` file defining its prompt interface
and workflow. Skills rely on the conventions bundled in [`.github/`](.github)
rather than on each other, except for:

- `solve` / `resolve` delegating to `implementation-planner` and `worktree-runner`
  in [`agents/`](agents) (which in turn invokes `check` before handing back).
- `review` delegating to `logic-reviewer`, `performance-reviewer`,
  `security-reviewer`, and `compliance-reviewer`.
- `ship` delegating to the `issue`, `solve`, `review`, and `resolve` skills.
- `spec` delegating to parallel `general-purpose` agents for external research.

Complex skills pair their `SKILL.md` prompt with deterministic Python scripts
(`skills/*/scripts/`) for GitHub API operations, state tracking, and git
worktree management.

### Shared Feedback State (`shared/pr_feedback.py`)

Shared utility dynamically loaded by script path to provide a single
authoritative definition for open PR review feedback across `triage` and
`resolve`:

- `unresolved_threads`: Identifies review threads where `isResolved` is false.
- `comments_since_checkpoint`: Tracks comments created after the most recent
  `Resolved.` checkpoint comment.

### Skill Script Mechanics

- **`review`** (`skills/review/scripts/post_review_comments.py`): Separates
  inline diff findings (with `file` and `line`) from unresolvable summary items,
  posting a single atomic GitHub PR review with a verdict (`Approved.` vs
  `Changes requested.`).
- **`resolve`** (`skills/resolve/scripts/`): `fetch_pr_issues.py` uses
  GraphQL and `pr_feedback.py` to extract open review items, plus `gh pr
  view`/`gh pr checks` for conflict and failing-check state;
  `post_pr_replies.py` replies to inline comments, resolves threads via
  GraphQL mutations (`resolveReviewThread`), posts a top-level `Resolved.`
  checkpoint, and re-requests review.
- **`triage`** (`skills/triage/scripts/`): `collect_triage.py` surveys
  assigned PRs, user PRs, and project backlog items. Uses `review_state.py` to
  compute PR action buckets (`merge`, `resolve_then_merge`, `resolve`,
  `self_review`, `draft`) and `backlog_utils.py` to filter out blocked items
  and rank tasks by priority and impact.

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
scripts (`skills/*/scripts/`) are checked with `task plugin:check` (and
fixed with `task plugin:fix`), which run ruff, ty, and the line-length
convention via the `commons-python` git dependency (see
[`python/commons-python`](../python/commons-python/README.md)) rather than
an in-repo ruff config.

## Deployment

The plugin is distributed directly from this repository, there is no
separate publish pipeline. `plugin.json` sets no `version`, so every merged
commit is a new version; consumers pick it up on their next
`/plugin marketplace update` or background auto-update.
