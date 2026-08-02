package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.createDirectories
import kotlin.io.path.writeText
import org.assertj.core.api.Assertions.assertThat
import org.gradle.testkit.runner.GradleRunner
import org.gradle.testkit.runner.TaskOutcome
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

/**
 * Applies the `no.chirico.commons.convention.architecture` precompiled script plugin to a
 * multi-module fixture, since its dependency-direction check only runs once a build is actually
 * evaluated.
 */
class ArchitectureConventionPluginFunctionalTest {

  /** The throwaway multi-module Gradle project the plugin is applied to. */
  @TempDir lateinit var projectDir: Path

  private fun moduleBuildFile(dependsOn: String? = null) =
    """
    plugins {
      java
      id("no.chirico.commons.convention.architecture")
    }
    ${dependsOn?.let { "dependencies { implementation(project(\"$it\")) }" } ?: ""}
    """
      .trimIndent()

  /** A dependency that follows the allowed layering direction builds without error. */
  @Test
  fun `an allowed dependency direction builds cleanly`() {
    projectDir
      .resolve("settings.gradle.kts")
      .writeText(
        """
        rootProject.name = "fixture"
        include(":app", ":impl")
        """
          .trimIndent()
      )
    projectDir.resolve("app").createDirectories()
    projectDir.resolve("app/build.gradle.kts").writeText(moduleBuildFile(dependsOn = ":impl"))
    projectDir.resolve("impl").createDirectories()
    projectDir.resolve("impl/build.gradle.kts").writeText(moduleBuildFile())

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments(":app:jar", ":impl:jar", "--stacktrace")
        .build()

    assertThat(result.task(":app:jar")?.outcome).isEqualTo(TaskOutcome.SUCCESS)
    assertThat(result.task(":impl:jar")?.outcome).isEqualTo(TaskOutcome.SUCCESS)
  }

  /**
   * A dependency that violates the allowed layering direction fails the build with a clear reason.
   */
  @Test
  fun `a disallowed dependency direction fails the build`() {
    projectDir
      .resolve("settings.gradle.kts")
      .writeText(
        """
        rootProject.name = "fixture"
        include(":app", ":other")
        """
          .trimIndent()
      )
    projectDir.resolve("app").createDirectories()
    projectDir.resolve("app/build.gradle.kts").writeText(moduleBuildFile(dependsOn = ":other"))
    projectDir.resolve("other").createDirectories()
    projectDir.resolve("other/build.gradle.kts").writeText(moduleBuildFile())

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments("help", "--stacktrace")
        .buildAndFail()

    assertThat(result.output).contains("Architecture violation: :app may not depend on :other")
  }

  /** An `:impl` module depending on `:api` follows the allowed direction. */
  @Test
  fun `impl depending on api builds cleanly`() {
    projectDir
      .resolve("settings.gradle.kts")
      .writeText(
        """
        rootProject.name = "fixture"
        include(":impl", ":api")
        """
          .trimIndent()
      )
    projectDir.resolve("impl").createDirectories()
    projectDir.resolve("impl/build.gradle.kts").writeText(moduleBuildFile(dependsOn = ":api"))
    projectDir.resolve("api").createDirectories()
    projectDir.resolve("api/build.gradle.kts").writeText(moduleBuildFile())

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments(":impl:jar", ":api:jar", "--stacktrace")
        .build()

    assertThat(result.task(":impl:jar")?.outcome).isEqualTo(TaskOutcome.SUCCESS)
  }

  /** A `:core-x` module depending on another `:core-y` module follows the allowed direction. */
  @Test
  fun `core depending on core builds cleanly`() {
    projectDir
      .resolve("settings.gradle.kts")
      .writeText(
        """
        rootProject.name = "fixture"
        include(":core-a", ":core-b")
        """
          .trimIndent()
      )
    projectDir.resolve("core-a").createDirectories()
    projectDir.resolve("core-a/build.gradle.kts").writeText(moduleBuildFile(dependsOn = ":core-b"))
    projectDir.resolve("core-b").createDirectories()
    projectDir.resolve("core-b/build.gradle.kts").writeText(moduleBuildFile())

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments(":core-a:jar", ":core-b:jar", "--stacktrace")
        .build()

    assertThat(result.task(":core-a:jar")?.outcome).isEqualTo(TaskOutcome.SUCCESS)
  }

  /** An `:impl` module depending on `:app` violates the allowed layering direction. */
  @Test
  fun `impl depending on app fails the build`() {
    projectDir
      .resolve("settings.gradle.kts")
      .writeText(
        """
        rootProject.name = "fixture"
        include(":impl", ":app")
        """
          .trimIndent()
      )
    projectDir.resolve("impl").createDirectories()
    projectDir.resolve("impl/build.gradle.kts").writeText(moduleBuildFile(dependsOn = ":app"))
    projectDir.resolve("app").createDirectories()
    projectDir.resolve("app/build.gradle.kts").writeText(moduleBuildFile())

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments("help", "--stacktrace")
        .buildAndFail()

    assertThat(result.output).contains("Architecture violation: :impl may not depend on :app")
  }
}
