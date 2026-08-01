package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.writeText
import org.gradle.testkit.runner.GradleRunner
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

class MapstructConventionPluginFunctionalTest {

  @TempDir lateinit var projectDir: Path

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
