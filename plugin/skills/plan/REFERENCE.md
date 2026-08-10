# Plan File Reference

This is the file set drafted under `docs/plan/`, covering the planning and
system design phases of a project.

## 1. docs/plan/PRD.md

Written once, during the initial planning pass. A snapshot of the product
idea at that time; unlike the files under `docs/`, it is not maintained as
scope evolves afterward.

- **Objective**: Context on the project and what it aims to achieve.
- **Success Metrics**: The metrics used to judge success.
- **Assumptions**: The premises the plan is built on.
- **Milestones**: Roadmap and project timeline.
- **Requirements**: A prioritized list of features.
- **Out of Scope**: Features explicitly excluded or delayed.
- **Open Questions**: Unresolved decisions or risks needing follow-up.

## 2. docs/plan/requirements/

Actionable requirements. Each states the problem: what is needed, not how
it gets built.

- **index.md**: Index table of number, title, priority, and link.
- **NNNN-slug.md**: One per requirement, zero-padded and sequenced:
  - **Motivation**: Why this requirement matters, tied to the PRD's
      Objective and Success Metrics.
  - **Behavior**: The specific behaviors the requirement covers.
  - **Constraints**: Operating constraints such as performance, security,
      or reliability.
  - **Acceptance Criteria**: The product-level, solution-agnostic signal
      that the requirement is satisfied.

## 3. docs/plan/research/

Domain investigations and technical benchmarks gathered before locking in a
decision.

- **index.md**: Index table of number, title, focus area, and link.
- **NNNN-slug.md**: One per investigation, zero-padded and sequenced:
  - **Context**: The uncertainty driving the investigation.
  - **Findings**: Results from framework or approach comparisons.
  - **Takeaway**: The recommendation.

## 4. docs/plan/decisions/

Architecture decision records, one per technical choice.

- **index.md**: Index table of number, title, status, and link.
- **NNNN-slug.md**: One per decision, zero-padded and sequenced:
  - **Status**: `Proposed` / `Accepted` / `Rejected` / `Superseded`.
  - **Context**: The architectural question and research findings.
  - **Decision**: What was chosen.
  - **Consequences**: Rationale, implications, and anything still open.

## 5. docs/plan/specifications/

Technical blueprints. Each states how to solve, in whole or in part, one or
more requirements: the solution, not the problem. Detailed enough to derive
an initial issue backlog.

- **index.md**: Index table of number, title, one-line approach, and link.
- **NNNN-slug.md**: One per specification, zero-padded and sequenced:
  - **Requirement**: The requirement(s) it addresses, and how much of each
      (in full or in part).
  - **Approach**: One-line summary of the technical solution.
  - **Design**: The technical scope and approach: endpoints, data model,
      interfaces, or workstreams touched.
  - **Steps**: Ordered, concrete implementation steps.
  - **Acceptance Criteria**: The measurable, technical signal that the
      implementation is done.
