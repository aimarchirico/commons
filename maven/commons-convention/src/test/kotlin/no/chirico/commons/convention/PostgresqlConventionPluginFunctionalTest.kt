package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.writeText
import org.gradle.testkit.runner.GradleRunner
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

/**
 * Applies the `no.chirico.commons.convention.postgresql` precompiled script plugin to a throwaway
 * fixture project, since its JPA all-open, Flyway, and PostgreSQL wiring only runs once a project
 * actually applies it.
 */
class PostgresqlConventionPluginFunctionalTest {

  /** The throwaway Gradle project the plugin is applied to. */
  @TempDir lateinit var projectDir: Path

  /** Applying the plugin resolves and applies JPA, Flyway, and PostgreSQL support cleanly. */
  @Test
  fun `applying the plugin wires jpa, flyway, and postgresql support`() {
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
          versionCatalogs {
            create("libs") {
              library("hypersistence-utils", "io.hypersistence:hypersistence-utils-hibernate-73:3.15.3")
            }
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
          id("no.chirico.commons.convention.postgresql")
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
