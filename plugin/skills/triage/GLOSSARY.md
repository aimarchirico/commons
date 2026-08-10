# Triage Glossary

Background concepts behind the triage skill's issue-dependency
classification, referenced by
`${CLAUDE_PLUGIN_ROOT}/skills/triage/REFERENCE.md`.

- **Leaf issue**: An open issue with no open sub-issues of its own (a parent
  whose sub-issues are all closed counts as a leaf). Represents the
  smallest unit of work. Only leaves are ever listed as `<item>` in triage
  tables.
- **Parent issue**: An open issue with at least one open sub-issue. Never
  listed as its own triage row; a block placed directly on it still
  reaches all its leaf descendants (see "via parent").
- **Blocked by**: What an item still needs resolved before it unblocks.
  The underlying relationship is always issue-to-issue: GitHub's
  `blocked_by` field only ever names other issues, never PRs. For a leaf
  issue this is the union of the open issues named by its own `blocked_by`
  field and any open issue named by an ancestor's own `blocked_by` field
  (see "via parent"). Each such open issue is rendered as `PR #<n>` if it
  already has an attached open PR, or as `Issue #<n>` if it doesn't yet.
- **Via parent**: Marks a blocker inherited from an ancestor's own
  `blocked_by` rather than set directly on the issue itself. Rendered as
  `(via parent)` after the blocker reference.
- **Blocking**: What an item's resolution would unblock. Shown on both
  issue rows and PR rows, computed differently for each. On an issue row
  it's the direct, non-transitive count of open issues that issue's own
  `blocking` relationship names, rendered as `N issue(s)`. On a PR row it's
  the count of open issues the PR's closed issues directly block, with
  other open PRs that also close one of those blocked issues credited instead of
  double-counted, rendered as `N PR(s), N issue(s)`.
- **Stackable**: An open issue is stackable when every one of its blockers
  resolves to the same single open PR, one unambiguous base branch to
  build on top of.
- **Fully blocked**: An open issue with at least one blocker that isn't
  stackable (a blocker has no open PR yet, or blockers resolve to more than
  one open PR). Hidden from the Actionable Items and Unassigned Issues
  tables, counted in `fully_blocked_count`.
