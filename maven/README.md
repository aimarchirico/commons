# Gradle

Kotlin backend components: the shared Gradle convention plugin and the libraries
published as Maven artifacts under the `no.chirico.core` group.

## Tech Stack

- **Java** 25
- **Kotlin** 2.4.0
- **Gradle** 9.6.0
- **Spring Boot** 4.1.0
- **ktfmt** 0.26.0 (via `com.ncorti.ktfmt.gradle`)
- **ArchUnit** 1.4.2 (JUnit 5)

## Folder Structure

```text
gradle/
├── build-logic/   # convention plugin (included build)
├── security/      # core-security library
├── test/          # core-test library
└── settings.gradle.kts
```

- **`build-logic/`** — precompiled script plugins under
  `no.chirico.core.buildlogic`: `kotlin` (Kotlin/JVM + ktfmt baseline) and
  `spring` (Spring Boot). Wired in via `includeBuild("build-logic")`.
- **`security/`** — publishes `core-security`; applies
  `id("no.chirico.core.buildlogic.kotlin")` and depends on `:test` for its
  architecture tests.
- **`test/`** — publishes `core-test`; shared test/ArchUnit support consumed by
  the other modules.

## Environment Variables

No local `.env` is required. Publishing reads credentials from the environment
(injected by CI):

| Key            | Purpose                                  |
| :------------- | :--------------------------------------- |
| `GITHUB_ACTOR` | GitHub Packages (Maven) publishing user. |
| `GITHUB_TOKEN` | GitHub Packages (Maven) publishing token. |

## Local Development

Requires Java 25 and [Task](https://taskfile.dev). Run from the repository root:

- `task maven:build` — build the modules.
- `task maven:check` — run tests and checks.
- `task maven:fix` — format Kotlin with ktfmt.
- `task maven:publish MODULE=<security|test|build-logic>` — publish a module.

The underlying commands are `./gradlew build`, `check`, and `ktfmtFormat`.

## Code Quality

- **Formatting** — ktfmt, applied through the convention plugin and run via
  `task gradle:fix` (`ktfmtFormat`).
- **Conventions** — file naming and length rules; modules extend
  `BaseConventionTest` from `core-test`.
- **Architecture** — ArchUnit dependency rules; modules extend
  `BaseArchitectureTest` from `core-test`.

## Deployment

Releases are driven by Release Please (`release-type: simple`) and published by
`.github/workflows/release.yml` when a release touches `maven/security`,
`maven/test`, or `maven/build-logic`. Each module's `maven-publish`
configuration publishes to the GitHub Packages Maven registry at
`https://maven.pkg.github.com/aimarchirico/core` under group `no.chirico.core`.
