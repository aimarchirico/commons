package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.createDirectories
import kotlin.io.path.writeText
import org.assertj.core.api.Assertions.assertThat
import org.gradle.testkit.runner.GradleRunner
import org.gradle.testkit.runner.TaskOutcome
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

class KotlinConventionPluginFunctionalTest {

  @TempDir lateinit var projectDir: Path

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
          "--stacktrace",
        )
        .build()

    listOf(":ktfmtCheck", ":test", ":jacocoTestReport", ":jacocoTestCoverageVerification")
      .forEach { task ->
        assertThat(result.task(task)?.outcome).`as`(task).isEqualTo(TaskOutcome.SUCCESS)
      }
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
