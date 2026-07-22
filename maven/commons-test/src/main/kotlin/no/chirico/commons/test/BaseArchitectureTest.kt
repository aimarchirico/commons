package no.chirico.commons.test

import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import com.tngtech.archunit.lang.syntax.ArchRuleDefinition.classes
import com.tngtech.archunit.library.Architectures.layeredArchitecture
import org.junit.jupiter.api.Test

abstract class BaseArchitectureTest {

  protected val allClasses by lazy {
    ClassFileImporter()
      .withImportOption(ImportOption.DoNotIncludeTests())
      .importPackages(javaClass.packageName)
  }

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
      .check(allClasses)
  }

  @Test
  fun `dependencies only flow down`() {
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
