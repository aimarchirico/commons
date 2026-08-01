# Maven

Kotlin backend components: the shared Gradle convention plugin and the libraries
published as Maven artifacts under the `no.chirico.commons` group.

## Tech Stack

- **Java** 25
- **Kotlin** 2.4.0
- **Gradle** 9.6.0
- **Spring Boot** 4.1.0
- **ktfmt** 0.26.0 (via `com.ncorti.ktfmt.gradle`)
- **detekt** 2.0.0-alpha.5 (via `dev.detekt`)
- **ArchUnit** 1.4.2 (JUnit 5)
- **MapStruct** 1.6.3 (via `org.mapstruct`)
- **JaCoCo** (via Gradle core), MockK 1.14.11, and detekt-test 2.0.0-alpha.5
  for test coverage and rule testing

## Folder Structure

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
  processor), and `architecture` (module-dependency architecture enforcement).
  Wired in via `includeBuild("commons-convention")`.
- **`commons-security/`**: publishes `commons-security`; applies
  `id("no.chirico.commons.convention.kotlin")`
  and depends on `:commons-test` for
  its convention tests.
- **`commons-firebase-admin/`**: publishes `commons-firebase-admin`; Firebase
  authentication filter and default stateless security chain,
  auto-configured for
  backends that need in-JVM user identity.
- **`commons-test/`**: publishes `commons-test`; shared test/ArchUnit support
  consumed by the other modules.

## Environment Variables

No local `.env` is required. Publishing reads credentials from the environment
(injected by CI):

| Key            | Purpose                                   |
| :------------- | :---------------------------------------- |
| `GITHUB_ACTOR` | GitHub Packages (Maven) publishing user.  |
| `GITHUB_TOKEN` | GitHub Packages (Maven) publishing token. |

## Local Development

Requires Java 25 and [Task](https://taskfile.dev). Run from the repository root:

- `task maven:build`: build the modules.
- `task maven:check`: run tests and checks.
- `task maven:fix`: format Kotlin with ktfmt.
- `task maven:publish MODULE=<module>`: publish a module, where
  `<module>` is one of `commons-security`, `commons-firebase-admin`,
  `commons-test`, or `commons-convention`.

The underlying commands are `./gradlew build`, `check`, and `ktfmtFormat`.

## Code Quality

- **Formatting**: ktfmt, applied through the convention plugin and run via
  `task maven:fix` (`ktfmtFormat`).
- **Static analysis**: detekt, applied through the convention plugin and run as
  part of `task maven:check` (`detekt`). The plugin layers its own configuration
  onto detekt's defaults, so consuming builds need no detekt configuration of
  their own.
- **Test coverage**: JaCoCo enforces 80% line coverage per module, applied
  through the convention plugin and run as part of `task maven:check`
  (`jacocoTestCoverageVerification`). The threshold is a whole-build ratio, not
  a per-class one, so a handful of thin, hard-to-test classes (a
  `@ConfigurationProperties` holder, a Spring `@AutoConfiguration`) don't force
  pointless tests as long as the module's tested code carries the average.
  `commons-convention` cannot apply its own convention plugin (it's the
  `kotlin-dsl` project that defines it), so it wires JaCoCo by hand in its own
  `build.gradle.kts` and is checked separately via `task maven:check`
  (`gradlew -p commons-convention check`), since `includeBuild` never attaches
  it to the root build's `check` task graph.
- **Documentation**: every public class, function, and property needs a KDoc
  block, test sources included. Overridden and protected members are exempt,
  so an implementation never has to repeat its supertype. Nested and inner
  declarations count too, since they are public by default in Kotlin. Any
  KDoc present is also checked against the actual signature
  (`OutdatedDocumentation`), so a stale `@param` is caught even on members
  that were never required to be documented.
- **Comments**: only KDoc blocks documenting a public declaration are allowed
  (`commons/PublicKDocOnly`), mirroring the documentation rule above exactly:
  whatever is required to have a KDoc block is also the only thing allowed to
  have one. Line comments, block comments, a KDoc block that documents nothing,
  and a KDoc block on a non-public declaration are all rejected, wherever they
  appear, on their own line or trailing code. The rule reads lexer tokens
  rather than text, so delimiters inside string literals are never mistaken
  for comments. A directive comment such as `// x-release-please-version` or
  `// suppressed: <reason>` is recognised by content, so it stays legal
  wherever it's written.
- **Suppression discipline**: every `@Suppress` annotation must be preceded by
  a `// suppressed: <reason>` comment of at least 10 characters
  (`commons/SuppressRequiresReason`), mirroring this repository's
  `commons-ts` convention of requiring a reason on suppressing comments.
- **Conventions**: file naming and length rules, enforced by the same detekt
  rule set as documentation and comments (`commons/FileNaming`,
  `commons/FileLength`). Kotlin files under `src/main` must be PascalCase-named
  and stay under 300 lines.
- **Architecture**: module-dependency rules for the api/impl/core layout,
  enforced at Gradle configuration time by the
  `no.chirico.commons.convention.architecture` plugin.

## Deployment

Releases are driven by Release Please (`release-type: simple`) and published by
`.github/workflows/release.yaml` when a release touches `maven/commons-security`,
`maven/commons-test`, `maven/commons-convention`, or
`maven/commons-firebase-admin`. Each module's `maven-publish`
configuration publishes to the GitHub Packages Maven registry at
`https://maven.pkg.github.com/aimarchirico/commons` under group
`no.chirico.commons`.
