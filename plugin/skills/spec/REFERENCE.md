# Spec File Reference

This is the file set drafted under `docs/specs/`. Precursor file content
follows `CONTRIBUTING.md#documentation`'s definitions for the corresponding
real `docs/` file, drafted rather than final. None of these files are ever
promoted verbatim into the project's real `docs/` folder or root
`README.md`; they are superseded by the real documentation once an
implementation exists, per the `commons:docs` skill.

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

### 1. docs/specs/README.md

Spec-only; never promoted. Entry point for the folder, mirroring the dual
narrative/directory-map role `CONTRIBUTING.md#documentation` assigns the
project root `README.md`, scoped here instead.

- **Problem**: What this project solves and why it matters.
- **Goals**: What the project must achieve.
- **Non-Goals**: What is deliberately out of scope.
- **Target Users**: Who the project is for.
- **Directory Map**: Links into `requirements/`, `decisions/`, and the
  precursor docs below.

### 2. docs/specs/requirements/

Spec-only; never promoted. One numbered file per top-level initiative,
detailed enough for the `commons:issue` skill to derive the initial issue backlog. 

- **README.md**: Index table of title, one-line objective, and link.
- **NNNN-\<slug\>.md**: One per initiative, zero-padded and sequenced the
  same way as `decisions/`. Uses its own vocabulary, deliberately not
  mirroring the field names in `.github/ISSUE_TEMPLATE/epic.yaml` or
  `story.yaml`:
  - **Objective**: What this initiative achieves and why it matters.
  - **Scope**: The constituent capabilities or workstreams it covers.
  - **Success Criteria**: The measurable signal it's done.

### 3. docs/specs/decisions/

Spec-only; never promoted. An ADR (Architecture Decision Record) log, one
file per decision, in standard Nygard ADR format.

- **README.md**: Index table of number, title, status, and link.
- **NNNN-kebab-case-title.md**: One per decision, zero-padded and sequenced:
  - **Status**: `Proposed` / `Accepted` / `Rejected` / `Superseded`.
  - **Context**: The question and research findings, with enough detail
    that no one has to redo the investigation.
  - **Decision**: What was chosen.
  - **Consequences**: Rationale, implications, and anything still open.

### 4. docs/specs/ARCHITECTURE.md

Always included. Same sections as `CONTRIBUTING.md#documentation`'s
`docs/ARCHITECTURE.md` definition, drafted rather than final.

### 5. docs/specs/API.md (if applicable)

Included only when `CONTRIBUTING.md#documentation`'s applicability rules say
the project exposes an API surface. Same sections as
`CONTRIBUTING.md#documentation`'s `docs/API.md` definition, drafted rather
than final. Domain entity and schema content goes in the Data Models section
here, not in `DESIGN.md`.

### 6. docs/specs/DESIGN.md (if applicable)

Included only when `CONTRIBUTING.md#documentation`'s applicability rules say
the project has a UI. Same sections as `CONTRIBUTING.md#documentation`'s
`docs/DESIGN.md` definition, drafted rather than final. Drafted after
`API.md`, matching that file's ordering in `CONTRIBUTING.md#documentation`.
