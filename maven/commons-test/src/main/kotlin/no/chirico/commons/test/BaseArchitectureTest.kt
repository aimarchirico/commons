package no.chirico.commons.test

import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes
import com.tngtech.archunit.library.Architectures.layeredArchitecture
import org.junit.jupiter.api.Test

/**
 * Architecture rules every service inherits by extending this class.
 *
 * The rules read the package of the concrete subclass, so a service gets them by placing its own
 * empty subclass in its root package.
 */
abstract class BaseArchitectureTest {

  protected val allClasses by lazy {
    ClassFileImporter()
      .withImportOption(ImportOption.DoNotIncludeTests())
      .importPackages(javaClass.packageName)
  }

  /** Asserts that every class under a `feature` package sits in one of the role packages. */
  @Test
  fun `every feature class resides in a role package`() {
    classes()
      .that()
      .resideInAPackage("..feature..")
      .should()
      .resideInAnyPackage(
        "..controller..",
        "..service..",
        "..repository..",
        "..dto..",
        "..model..",
        "..entity..",
        "..mapper..",
        "..config..",
        "..util..",
      )
      .allowEmptyShould(true)
      .check(allClasses)
  }

  /**
   * Asserts that controllers, services, and repositories depend downwards only.
   *
   * Layers are optional so a service that omits one still passes.
   */
  @Test
  fun `dependencies only flow down`() {
    layeredArchitecture()
      .consideringOnlyDependenciesInLayers()
      .withOptionalLayers(true)
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
