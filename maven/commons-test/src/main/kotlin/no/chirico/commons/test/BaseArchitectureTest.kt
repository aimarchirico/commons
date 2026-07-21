package no.chirico.commons.test

import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes
import com.tngtech.archunit.library.Architectures.layeredArchitecture
import org.junit.jupiter.api.Test

/**
 * Enforces the intra-module package layout: every class lives in a known role package, and
 * dependencies only flow down the controller -> service -> repository spine.
 *
 * Opt in from an app-structured consumer with `class ArchitectureTest : BaseArchitectureTest()`.
 * Core modules (concern-named building blocks) and the Spring Boot entrypoint are exempt.
 */
abstract class BaseArchitectureTest {

  protected val allClasses by lazy {
    ClassFileImporter()
      .withImportOption(ImportOption.DoNotIncludeTests())
      .importPackages(javaClass.packageName)
  }

  @Test
  fun `every class resides in a role package`() {
    classes()
      .that()
      .resideOutsideOfPackage("..core..")
      .and()
      .areNotAnnotatedWith("org.springframework.boot.autoconfigure.SpringBootApplication")
      .should()
      .resideInAnyPackage(
        // directional spine
        "..controller..",
        "..service..",
        "..repository..",
        // supporting: shapes (transport -> domain -> persistence), translator, wiring
        "..dto..",
        "..model..",
        "..entity..",
        "..mapper..",
        "..config..",
      )
      .check(allClasses)
  }

  @Test
  fun `dependencies only flow down the spine`() {
    layeredArchitecture()
      .consideringOnlyDependenciesInLayers()
      .layer("controller")
      .definedBy("..controller..")
      .layer("service")
      .definedBy("..service..")
      .layer("repository")
      .definedBy("..repository..")
      .whereLayer("controller")
      .mayNotBeAccessedByAnyLayer()
      .whereLayer("service")
      .mayOnlyBeAccessedByLayers("controller")
      .whereLayer("repository")
      .mayOnlyBeAccessedByLayers("service")
      .check(allClasses)
  }
}
