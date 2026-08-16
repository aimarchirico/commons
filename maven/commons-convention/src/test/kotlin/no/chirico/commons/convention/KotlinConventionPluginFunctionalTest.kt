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
 * Applies the `no.chirico.commons.convention.kotlin` precompiled script plugin to a throwaway
 * fixture project and runs its full `build`, since the plugin's own wiring can only be observed by
 * actually applying it, not by unit-testing the script in isolation.
 */
class KotlinConventionPluginFunctionalTest {

  /** The throwaway Gradle project the plugin is applied to. */
  @TempDir lateinit var projectDir: Path

  /**
   * detekt is excluded: TestKit splits classes/resources so the ruleset's META-INF entry never
   * reaches it here (real usage is still covered by every consumer build). `withDebug(true)` runs
   * in-process so JaCoCo can see coverage from the triggered plugin code.
   */
  @Test
  fun `applying the plugin wires formatting, linting, and coverage into build`() {
    writeSettingsFile()
    writeBuildFile()
    writeMainSource()
    writeTestSource()

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments(
          "ktfmtFormat",
          "ktfmtCheck",
          "test",
          "jacocoTestReport",
          "jacocoTestCoverageVerification",
          "verifyTestSourcesPresent",
          "--stacktrace",
        )
        .build()

    listOf(
        ":ktfmtCheck",
        ":test",
        ":jacocoTestReport",
        ":jacocoTestCoverageVerification",
        ":verifyTestSourcesPresent",
      )
      .forEach { task ->
        assertThat(result.task(task)?.outcome).`as`(task).isEqualTo(TaskOutcome.SUCCESS)
      }
  }

  @Test
  fun `applying the plugin fails when a module has main sources but no tests`() {
    writeSettingsFile()
    writeBuildFile()
    writeMainSource()

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments("verifyTestSourcesPresent", "--stacktrace")
        .buildAndFail()

    assertThat(result.output).contains("fixture").contains("no tests")
  }

  @Test
  fun `applying the plugin does not fail when a module has no main sources`() {
    writeSettingsFile()
    writeBuildFile()

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments("verifyTestSourcesPresent", "--stacktrace")
        .build()

    assertThat(result.task(":verifyTestSourcesPresent")?.outcome).isEqualTo(TaskOutcome.SUCCESS)
  }

  @Test
  fun `applying the plugin does not fail when main has only resources`() {
    writeSettingsFile()
    writeBuildFile()
    val resources = projectDir.resolve("src/main/resources")
    resources.createDirectories()
    resources.resolve("sample.properties").writeText("greeting=Hello")

    val result =
      GradleRunner.create()
        .withProjectDir(projectDir.toFile())
        .withPluginClasspath()
        .withDebug(true)
        .withArguments("verifyTestSourcesPresent", "--stacktrace")
        .build()

    assertThat(result.task(":verifyTestSourcesPresent")?.outcome).isEqualTo(TaskOutcome.SUCCESS)
  }

  private fun writeSettingsFile() {
    projectDir
      .resolve("settings.gradle.kts")
      .writeText(
        """
        pluginManagement {
          repositories {
            gradlePluginPortal()
            mavenCentral()
          }
        }
        dependencyResolutionManagement {
          repositories {
            mavenCentral()
          }
        }
        rootProject.name = "fixture"
        """
          .trimIndent()
      )
  }

  private fun writeBuildFile() {
    projectDir
      .resolve("build.gradle.kts")
      .writeText(
        """
        plugins {
          id("no.chirico.commons.convention.kotlin")
        }

        dependencies {
          testImplementation("org.junit.jupiter:junit-jupiter-api:5.11.4")
          testRuntimeOnly("org.junit.jupiter:junit-jupiter-engine:5.11.4")
          testRuntimeOnly("org.junit.platform:junit-platform-launcher:1.11.4")
        }
        """
          .trimIndent()
      )
  }

  private fun writeMainSource() {
    val mainSrc = projectDir.resolve("src/main/kotlin/sample")
    mainSrc.createDirectories()
    mainSrc
      .resolve("Greeter.kt")
      .writeText(
        """
        package sample

        /** Greets people by name. */
        class Greeter {
          /** Returns a greeting for [name]. */
          fun greet(name: String): String = "Hello, ${'$'}name!"
        }
        """
          .trimIndent()
      )
  }

  private fun writeTestSource() {
    val testSrc = projectDir.resolve("src/test/kotlin/sample")
    testSrc.createDirectories()
    testSrc
      .resolve("GreeterTest.kt")
      .writeText(
        """
        package sample

        import org.junit.jupiter.api.Assertions.assertEquals
        import org.junit.jupiter.api.Test

        class GreeterTest {
          @Test
          fun `greets by name`() {
            assertEquals("Hello, World!", Greeter().greet("World"))
          }
        }
        """
          .trimIndent()
      )
  }
}
