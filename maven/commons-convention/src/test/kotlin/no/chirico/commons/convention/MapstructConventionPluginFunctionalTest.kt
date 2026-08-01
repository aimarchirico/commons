package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.writeText
import org.gradle.testkit.runner.GradleRunner
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

/**
 * Applies the `no.chirico.commons.convention.mapstruct` precompiled script plugin to a throwaway
 * fixture project, since its kapt and dependency wiring only runs once a project applies it against
 * a real `libs` version catalog.
 */
class MapstructConventionPluginFunctionalTest {

  /** The throwaway Gradle project the plugin is applied to. */
  @TempDir lateinit var projectDir: Path

  /** Applying the plugin resolves kapt and the mapstruct dependencies cleanly. */
  @Test
  fun `applying the plugin wires kapt and the mapstruct dependencies`() {
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
              library("mapstruct", "org.mapstruct:mapstruct:1.6.3")
              library("mapstruct-processor", "org.mapstruct:mapstruct-processor:1.6.3")
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
          id("no.chirico.commons.convention.mapstruct")
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
