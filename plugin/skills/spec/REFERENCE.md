# Spec File Reference

This is the file set drafted under `docs/specs/`. Section content follows
`CONTRIBUTING.md#documentation`'s definitions for the corresponding real
`docs/` file, drafted rather than final. None of these files are ever
promoted verbatim into the project's real `docs/` folder or root
`README.md`; they are superseded by the real documentation once an
implementation exists, per the `docs` skill.

```text
docs/specs/
  README.md
  requirements/
    README.md
    NNNN-<slug>.md
  decisions/
    README.md
    NNNN-<slug>.md
  ARCHITECTURE.md
  API.md        (if applicable)
  DESIGN.md     (if applicable)
```

## README.md

Spec-only; never promoted to the real `docs/` folder. A narrative covering
Problem, Goals, Non-Goals, and Target Users, plus a directory map into
`requirements/`, `decisions/`, and the precursor docs below, mirroring the
dual narrative/directory-map role `CONTRIBUTING.md#documentation` assigns
the project root `README.md`, scoped to this folder.

## requirements/

Spec-only; never promoted. One numbered file per top-level initiative,
named `NNNN-<slug>.md` (zero-padded, same numbering convention as
`decisions/`), detailed enough for the `issue` skill to derive the initial
Epic → Story → Task → Subtask backlog. Each file uses its own vocabulary
(Objective, Scope, Success Criteria), deliberately not mirroring the field
names in `.github/ISSUE_TEMPLATE/epic.yaml` or `story.yaml`.

`requirements/README.md` is an index table of title, one-line objective,
and link.

## decisions/

Spec-only; never promoted. An ADR log, one file per decision, in standard
Nygard ADR format, named `NNNN-kebab-case-title.md`. Each entry has Status
(Proposed/Accepted/Rejected/Superseded), Context, Decision, and
Consequences.

`decisions/README.md` is an index table of number, title, status, and link.

## ARCHITECTURE.md

Always included. Same sections as `CONTRIBUTING.md#documentation`'s
`docs/ARCHITECTURE.md` definition, drafted rather than final.

## API.md (if applicable)

Included only when `CONTRIBUTING.md#documentation`'s applicability rules
say the project exposes an API surface. Same sections as
`CONTRIBUTING.md#documentation`'s `docs/API.md` definition, drafted rather
than final. Domain entity and schema content goes in the Data Models
section here, not in `DESIGN.md`.

## DESIGN.md (if applicable)

Included only when `CONTRIBUTING.md#documentation`'s applicability rules
say the project has a UI. Same sections as
`CONTRIBUTING.md#documentation`'s `docs/DESIGN.md` definition, drafted
rather than final. Drafted after `API.md`, matching that file's ordering
in `CONTRIBUTING.md#documentation`.
