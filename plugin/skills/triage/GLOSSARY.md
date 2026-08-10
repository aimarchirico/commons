# Triage Glossary

Terms used throughout `REFERENCE.md`.

- **Leaf issue**: An issue with no sub-issues of its own. Represents the
  smallest unit of work. Only leaves are ever listed as `<item>` in triage
  tables.
- **Parent issue**: An issue with sub-issues. Never listed as its own
  triage row; a block placed directly on it still reaches all its leaf
  descendants (see "via parent").
- **Blocked by**: An issue's own `blocked_by` relationship, plus - for a
  leaf - any blocker on its ancestors (see "via parent"). Rendered as
  `PR #<n>` when the blocker has an attached open PR, or `Issue #<n>`
  otherwise.
- **Via parent**: Marks a blocker inherited from an ancestor's own
  `blocked_by` rather than set directly on the issue itself. Rendered as
  `(via parent)` after the blocker reference.
- **Blocking**: The direct, non-transitive count of open issues an issue's
  own `blocking` relationship names. Rendered as `N issue(s)` on issue
  rows. On PR rows it also credits other open PRs that close a blocked
  issue instead of double-counting it, rendered as `N PR(s), N issue(s)`.
- **Stackable**: An issue is stackable when every one of its blockers
  resolves to the same single open PR; one unambiguous base branch to
  build on top of.
- **Fully blocked**: An issue with at least one blocker that isn't
  stackable (a blocker has no open PR yet, or blockers resolve to more than
  one open PR). Hidden from the Actionable Items and Unassigned Issues
  tables, counted in `fully_blocked_count`.
