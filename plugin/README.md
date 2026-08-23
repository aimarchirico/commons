# Plugin

The `commons` Claude Code plugin: reusable agent skills covering the
development lifecycle, the subagents they delegate to, and the bundled
Git/GitHub conventions they follow. This whole directory is the plugin
source: `.claude-plugin/marketplace.json` at the repository root points its
`source` here, so installing the plugin only fetches `plugin/`, not the rest
of the monorepo.

## Install

```sh
/plugin marketplace add aimarchirico/commons
/plugin install commons@commons
```

No environment variables are required.

## Usage

Each skill directory contains a `SKILL.md` file defining its prompt
interface and workflow, invoked as a Claude Code slash command (e.g.
`/commons:solve`).

### Lifecycle

Which skill to run, and what hands off to what:

```mermaid
graph LR
    work["New work"] -->|design risk| plan["/commons:plan"]
    work -->|clear enough to cut| issue["/commons:issue"]
    plan -->|design document| issue

    survey["What next?"] --> triage["/commons:triage"]
    triage -->|ready issue| solve
    triage -->|pull request to review| review
    triage -->|merge blockers| resolve
    triage -->|merge ready| merge

    issue --> solve["/commons:solve"]
    solve -->|pull request| review["/commons:review"]
    review -->|changes requested| resolve["/commons:resolve"]
    resolve --> review
    review -->|approved| merge["Merge"]
```

`/commons:ship` runs that chain in one invocation, from `commons:plan`
through `commons:solve`, and through `commons:review` and `commons:resolve`
when `--review` is set. The design document and its implementation land in a
single branch and pull request.

### Composition

What each skill invokes or delegates to. Solid edges invoke another skill,
dotted edges delegate to a subagent in `agents/`:

```mermaid
graph TD
    plan["/commons:plan"] -.-> research["general-purpose agents<br/>(external research)"]
    plan -.-> runner
    solve["/commons:solve"] -.-> planner["implementation-planner"]
    solve -.-> runner["worktree-runner"]
    resolve["/commons:resolve"] -.-> planner
    resolve -.-> runner
    review["/commons:review"] -.-> reviewers["logic, performance, security,<br/>and compliance reviewers"]

    runner --> commit["/commons:commit"]
    runner --> docs["/commons:docs"]
    runner --> check["/commons:check"]
    plan --> pr["/commons:pr"]
    solve --> pr
```

`commons:issue` and `commons:triage` compose with nothing; they read and
write GitHub directly through their own scripts.

## Development

### Tech Stack

- Markdown `SKILL.md` definitions (`name`/`description`/`argument-hint`
  frontmatter, where `description` covers both what the skill does and when
  to use it, plus a `## Workflow` section) and agent `.md` definitions
  (`name`/`description` frontmatter plus free-form instructions).
- Packaged as a Claude Code plugin (`.claude-plugin/plugin.json`).
- Python 3.13, via `uv`, for scripts under `skills/*/scripts/`.
- Self-contained: `.github/` bundles this repository's own
  `CONTRIBUTING.md` and GitHub templates, so skills reference
  `${CLAUDE_PLUGIN_ROOT}/.github/...` directly instead of depending on the
  consumer repository having materialized anything.

### Folder Structure

```text
plugin/
├── .claude-plugin/plugin.json   # plugin manifest
├── .github/                     # bundled conventions (CONTRIBUTING.md, issue/PR templates)
├── shared/                      # shared orchestration conventions (CONVENTIONS.md) & script utilities (pr_feedback.py)
├── skills/
│   ├── check/SKILL.md           # verify the tree against the project's own PR-gating CI checks
│   ├── commit/SKILL.md          # create logical, atomic commits
│   ├── docs/SKILL.md            # update project documentation
│   ├── issue/SKILL.md           # create hierarchical issues
│   ├── plan/SKILL.md            # draft a design document for design risk
│   ├── pr/SKILL.md              # create a standardized pull request
│   ├── resolve/SKILL.md         # orchestrate the lifecycle from PR review feedback
│   ├── review/SKILL.md          # review a pull request via parallel reviewer agents
│   ├── ship/SKILL.md            # chain design, issue creation, and solving into one flow
│   ├── solve/SKILL.md           # orchestrate the lifecycle from an existing issue
│   └── triage/SKILL.md          # survey open PRs and Backlog issues, read-only
└── agents/
    ├── compliance-reviewer.md    # reviews a diff against CONTRIBUTING.md (read-only)
    ├── implementation-planner.md # drafts an implementation plan (read-only)
    ├── logic-reviewer.md         # reviews a diff for logic errors (read-only)
    ├── performance-reviewer.md   # reviews a diff for performance regressions (read-only)
    ├── security-reviewer.md      # reviews a diff for security vulnerabilities (read-only)
    └── worktree-runner.md        # implements an approved plan unattended
```

Complex skills pair their `SKILL.md` prompt with deterministic Python scripts
(`skills/*/scripts/`) for GitHub API operations, state tracking, and git
worktree management.

**Shared Conventions** (`shared/CONVENTIONS.md`): the single definition of the
orchestration policies more than one skill depends on, referenced by anchor the
same way skills reference `CONTRIBUTING.md` sections. `.github/CONTRIBUTING.md`
governs how code and history are authored; `CONVENTIONS.md` governs how skills
run: `#branch-setup`, `#worktrees`, `#verification`, and
`#opening-the-pull-request`. Policies that must not drift between skills (the
worktree path, the check-retry count, who owns pushing) live here rather than
being restated per skill.

**Shared Feedback State** (`shared/pr_feedback.py`): dynamically loaded by
script path to provide a single authoritative definition for open PR review
feedback across `commons:triage` and `commons:resolve`:

- `unresolved_threads`: Identifies review threads where `isResolved` is false.
- `comments_since_checkpoint`: Tracks comments created after the most recent
  `Resolved.` checkpoint comment.

**Skill Script Mechanics**:

- **`commons:review`** (`skills/review/scripts/post_review_comments.py`): Separates
  inline diff findings (with `file` and `line`) from unresolvable summary
  items, posting a single atomic GitHub PR review with a verdict
  (`Approved.` vs `Changes requested.`).
- **`commons:resolve`** (`skills/resolve/scripts/`): `fetch_pr_problems.py` uses
  GraphQL and `pr_feedback.py` to extract open review items, plus `gh pr
  view`/`gh pr checks` for conflict and failing-check state;
  `post_pr_replies.py` replies to inline comments, resolves threads via
  GraphQL mutations (`resolveReviewThread`), posts a top-level `Resolved.`
  checkpoint, and re-requests review.
- **`commons:triage`** (`skills/triage/scripts/`): `collect_triage.py` surveys
  assigned PRs, user PRs, and project backlog items. Uses `review_state.py`
  to compute PR action buckets (`merge`, `resolve_then_merge`, `resolve`,
  `self_review`, `draft`) and `backlog_utils.py` to filter out blocked items
  and rank tasks by priority and impact.

### Code Quality

- **Markdown**: Linted with shared `markdownlint` config via `task docs:check`
  (auto-fixed with `task docs:fix`).
- **Python Scripts**: Checked with `task plugin:check` (auto-fixed with `task
  plugin:fix`), running ruff, ty, and line-length checks.

## Deployment

The plugin is distributed directly from this repository; there is no
separate publish pipeline. `plugin.json` sets no `version`, so every merged
commit is a new version; consumers pick it up on their next
`/plugin marketplace update` or background auto-update.

## Contributing

See [CONTRIBUTING.md](../.github/CONTRIBUTING.md).

## License

[MIT](../LICENSE) © Aimár A. Chirico
