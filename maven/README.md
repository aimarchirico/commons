# Maven

Kotlin backend components: the shared Gradle convention plugin and the
libraries published as Maven artifacts under the `no.chirico.commons` group.

## Install

Requires Java 25 and [Task](https://taskfile.dev).

No local `.env` is required for development. Publishing reads credentials
from the environment (injected by CI):

| Key            | Purpose                                    |
| :------------- | :----------------------------------------- |
| `GITHUB_ACTOR` | GitHub Packages (Maven) publishing user.   |
| `GITHUB_TOKEN` | GitHub Packages (Maven) publishing token.  |

To depend on a published artifact, add the GitHub Packages Maven registry
(`https://maven.pkg.github.com/aimarchirico/commons`) and the
`no.chirico.commons` group to your Gradle build.

## Usage

Run from the repository root:

- `task maven:build`: build the modules.
- `task maven:check`: run tests and checks.
- `task maven:fix`: format Kotlin with ktfmt.
- `task maven:publish MODULE=<module>`: publish a module, where `<module>` is
  one of `commons-security`, `commons-firebase-admin`, `commons-test`, or
  `commons-convention`.

The underlying commands are `./gradlew build`, `check`, and `ktfmtFormat`.

## Development

### Tech Stack

Java 25 · Kotlin 2.4.0 · Gradle 9.6.0 · Spring Boot 4.1.0 · ktfmt 0.26.0 (via
`com.ncorti.ktfmt.gradle`) · detekt 2.0.0-alpha.5 (via `dev.detekt`) ·
ArchUnit 1.4.2 (JUnit 5) · MapStruct 1.6.3 (via `org.mapstruct`) · JaCoCo
(Gradle core), MockK 1.14.11, and detekt-test 2.0.0-alpha.5 for test coverage
and rule testing.

### Folder Structure

```text
maven/
├── commons-convention/     # convention plugin (included build)
├── commons-security/       # commons-security library
├── commons-firebase-admin/ # commons-firebase-admin library
├── commons-test/           # commons-test library
└── settings.gradle.kts
```

- **`commons-convention/`**: precompiled script plugins under
  `no.chirico.commons.convention`: `kotlin` (Kotlin/JVM + ktfmt + detekt),
  `spring` (Spring Boot), `mapstruct` (MapStruct compilation/annotation
  processor), and `architecture` (module-dependency architecture
  enforcement). Wired in via `includeBuild("commons-convention")`.
- **`commons-security/`**: publishes `commons-security`; applies
  `id("no.chirico.commons.convention.kotlin")` and depends on
  `:commons-test` for its convention tests.
- **`commons-firebase-admin/`**: publishes `commons-firebase-admin`;
  Firebase authentication filter and default stateless security chain,
  auto-configured for backends that need in-JVM user identity.
- **`commons-test/`**: publishes `commons-test`; shared test/ArchUnit
  support consumed by the other modules.

### Code Quality

- **Formatting**: ktfmt formatting applied via
  `no.chirico.commons.convention.kotlin` plugin (`task maven:fix`).
- **Static Analysis**: detekt with custom rules for documentation and file
  limits (`task maven:check`).
- **Documentation & Comments**: KDoc required for public members
  (`OutdatedDocumentation`, `UndocumentedPublic*`).
- **Suppression Discipline**: `// suppressed: <reason>` comment of at least
  10 characters required for `@Suppress` (`commons/SuppressRequiresReason`).
- **Conventions**: PascalCase naming (`commons/FileNaming`) and 300-line
  per-file limit under `src/main` (`commons/FileLength`).
- **Testing & Coverage**: JaCoCo enforcing 80% line and branch coverage per
  module (`jacocoTestCoverageVerification`); modules with `src/main`
  Kotlin/Java sources must have `src/test` sources
  (`verifyTestSourcesPresent`).
- **Architecture**: ArchUnit module-dependency rules enforced at Gradle
  configuration time (`no.chirico.commons.convention.architecture`).

## Deployment

Releases are driven by Release Please (`release-type: simple`) and published
by `.github/workflows/release.yaml` when a release touches
`maven/commons-security`, `maven/commons-test`, `maven/commons-convention`,
or `maven/commons-firebase-admin`. Each module's `maven-publish`
configuration publishes to the GitHub Packages Maven registry at
`https://maven.pkg.github.com/aimarchirico/commons` under group
`no.chirico.commons`.

## Contributing

See [`.github/CONTRIBUTING.md`](../.github/CONTRIBUTING.md).

## License

[MIT](../LICENSE) © Aimár A. Chirico
