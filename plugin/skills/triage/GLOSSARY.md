# Triage Glossary

Terms used throughout `REFERENCE.md`.

- **Leaf issue**: An issue with no sub-issues of its own. Represents the
  smallest unit of work. Only leaves are ever listed as `<item>` in triage
  tables.
- **Parent issue**: An issue with sub-issues. Never listed as its own
  triage row; a block placed directly on it still reaches all its leaf
  descendants (see "via parent").
- **Blocked by**: What an item still needs resolved before it unblocks.
  Shown on issue rows only (PR rows use "blocking" instead). For a leaf
  issue this includes its own `blocked_by` relationship plus any blocker on
  its ancestors (see "via parent"). Rendered as `PR #<n>` when the blocker
  has an attached open PR, or `Issue #<n>` otherwise.
- **Via parent**: Marks a blocker inherited from an ancestor's own
  `blocked_by` rather than set directly on the issue itself. Rendered as
  `(via parent)` after the blocker reference.
- **Blocking**: What an item's resolution would unblock. Shown on both
  issue rows and PR rows, computed differently for each. On an issue row
  it's the direct, non-transitive count of open issues that issue's own
  `blocking` relationship names, rendered as `N issue(s)`. On a PR row it's
  the count of open issues the PR's closed issues directly block, with
  other open PRs that also close one of those issues credited instead of
  double-counted, rendered as `N PR(s), N issue(s)`.
- **Stackable**: An issue is stackable when every one of its blockers
  resolves to the same single open PR, one unambiguous base branch to
  build on top of.
- **Fully blocked**: An issue with at least one blocker that isn't
  stackable (a blocker has no open PR yet, or blockers resolve to more than
  one open PR). Hidden from the Actionable Items and Unassigned Issues
  tables, counted in `fully_blocked_count`.
