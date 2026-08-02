package no.chirico.commons.convention

import java.nio.file.Path
import kotlin.io.path.writeText
import org.gradle.testkit.runner.GradleRunner
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.io.TempDir

/**
 * Applies the `no.chirico.commons.convention.web` precompiled script plugin to a throwaway fixture
 * project, since its REST API dependency wiring only runs once a project actually applies it.
 */
class WebConventionPluginFunctionalTest {

  /** The throwaway Gradle project the plugin is applied to. */
  @TempDir lateinit var projectDir: Path

  /** Applying the plugin resolves and applies the REST API dependency stack cleanly. */
  @Test
  fun `applying the plugin wires the rest api dependency stack`() {
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
              library("springdoc-openapi", "org.springdoc:springdoc-openapi-starter-webmvc-ui:3.0.3")
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
          id("no.chirico.commons.convention.web")
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
