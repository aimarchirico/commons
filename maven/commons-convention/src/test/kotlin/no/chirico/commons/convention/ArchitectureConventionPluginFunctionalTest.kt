package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.createDirectories
import kotlin.io.path.writeText
import org.assertj.core.api.Assertions.assertThat
import org.gradle.testkit.runner.GradleRunner
import org.gradle.testkit.runner.TaskOutcome
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

class ArchitectureConventionPluginFunctionalTest {

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
}
