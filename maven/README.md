# Gradle

Kotlin backend components: the shared Gradle convention plugin and the libraries
published as Maven artifacts under the `no.chirico.commons` group.

## Tech Stack

- **Java** 25
- **Kotlin** 2.4.0
- **Gradle** 9.6.0
- **Spring Boot** 4.1.0
- **ktfmt** 0.26.0 (via `com.ncorti.ktfmt.gradle`)
- **ArchUnit** 1.4.2 (JUnit 5)

## Folder Structure

```text
maven/
├── commons-convention/     # convention plugin (included build)
├── commons-security/       # commons-security library
├── commons-firebase-admin/ # commons-firebase-admin library
├── commons-test/           # commons-test library
└── settings.gradle.kts
```

- **`commons-convention/`** — precompiled script plugins under
  `no.chirico.commons.convention`: `kotlin` (Kotlin/JVM + ktfmt baseline),
  `spring` (Spring Boot), and `architecture` (module-dependency enforcement for
  the api/impl/core modular-monolith layout). Wired in via
  `includeBuild("commons-convention")`.
- **`commons-security/`** — publishes `commons-security`; applies
  `id("no.chirico.commons.convention.kotlin")` and depends on `:commons-test` for
  its convention tests.
- **`commons-firebase-admin/`** — publishes `commons-firebase-admin`; Firebase
  authentication filter and default stateless security chain, auto-configured for
  backends that need in-JVM user identity.
- **`commons-test/`** — publishes `commons-test`; shared test/ArchUnit support
  consumed by the other modules.

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
- `task maven:publish MODULE=<commons-security|commons-firebase-admin|commons-test|commons-convention>` — publish a module.

The underlying commands are `./gradlew build`, `check`, and `ktfmtFormat`.

## Code Quality

- **Formatting** — ktfmt, applied through the convention plugin and run via
  `task maven:fix` (`ktfmtFormat`).
- **Conventions** — file naming and length rules; modules extend
  `BaseConventionTest` from `commons-test`.
- **Architecture** — module-dependency rules for the api/impl/core layout,
  enforced at Gradle configuration time by the
  `no.chirico.commons.convention.architecture` plugin (`:app → :*:impl | :core`,
  `:*:impl → :*:api | :core`, `:*:api → :core`, `:core → :core`).

## Deployment

Releases are driven by Release Please (`release-type: simple`) and published by
`.github/workflows/release.yml` when a release touches `maven/commons-security`,
`maven/commons-test`, or `maven/commons-convention`. Each module's `maven-publish`
configuration publishes to the GitHub Packages Maven registry at
`https://maven.pkg.github.com/aimarchirico/commons` under group `no.chirico.commons`.
