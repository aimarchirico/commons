package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.writeText
import org.gradle.testkit.runner.GradleRunner
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

/**
 * Applies the `no.chirico.commons.convention.spring` precompiled script plugin to a throwaway
 * fixture project, since its Spring Boot, JPA, and all-open wiring only runs once a project
 * actually applies it.
 */
class SpringConventionPluginFunctionalTest {

  /** The throwaway Gradle project the plugin is applied to. */
  @TempDir lateinit var projectDir: Path

  /** Applying the plugin resolves and applies Spring Boot, JPA, and all-open support cleanly. */
  @Test
  fun `applying the plugin wires spring boot, jpa, and all-open support`() {
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
    projectDir
      .resolve("build.gradle.kts")
      .writeText(
        """
        plugins {
          id("no.chirico.commons.convention.spring")
        }
        """
          .trimIndent()
      )

    GradleRunner.create()
      .withProjectDir(projectDir.toFile())
      .withPluginClasspath()
      .withDebug(true)
      .withArguments("help", "--stacktrace")
      .build()
  }
}
