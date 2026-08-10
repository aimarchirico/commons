# Triage Glossary

Terms used throughout `REFERENCE.md`.

- **Leaf issue**: An issue with no children (sub-issues) of its own - the
  actual unit that gets its own PR. Usually a Subtask, or a Story/Task/Bug
  with no Subtasks. Only leaves are ever listed as `<item>` in triage
  tables.
- **Container issue**: An issue with children (e.g. a Story with open
  Subtasks). Never listed as its own triage row; a block placed directly on
  it still reaches all its leaf descendants (see "via parent").
- **Via parent**: Marks a blocker inherited from an ancestor's own
  `blocked_by` rather than set directly on the issue itself. Rendered as
  `(via parent)` after the blocker reference, e.g. `Issue #50 (via parent)`.
- **Stackable**: An issue is stackable when every one of its blockers
  resolves to the same single open PR - one unambiguous base branch to
  build on top of.
- **Fully blocked**: An issue with at least one blocker that isn't
  stackable (a blocker has no open PR yet, or blockers resolve to more than
  one open PR). Hidden from the Actionable Items and Unassigned Issues
  tables, counted in `fully_blocked_count`.
