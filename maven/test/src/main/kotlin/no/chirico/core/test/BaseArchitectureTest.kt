package no.chirico.core.test

import com.tngtech.archunit.core.domain.JavaClasses
import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import com.tngtech.archunit.library.Architectures.layeredArchitecture
import com.tngtech.archunit.library.dependencies.SlicesRuleDefinition.slices
import org.junit.jupiter.api.Test

abstract class BaseArchitectureTest {

  private val basePackage by lazy { javaClass.packageName }

  private val classes: JavaClasses by lazy {
    ClassFileImporter()
      .withImportOption(ImportOption.DoNotIncludeTests())
      .importPackages(basePackage)
  }

  @Test
  fun `modules depend downward`() {
    layeredArchitecture()
      .consideringAllDependencies()
      .optionalLayer("App")
      .definedBy("..${basePackage}..app..")
      .optionalLayer("Feature")
      .definedBy("..${basePackage}..feature..")
      .optionalLayer("Core")
      .definedBy("..${basePackage}..core..")
      .whereLayer("App")
      .mayNotBeAccessedByAnyLayer()
      .whereLayer("Feature")
      .mayOnlyBeAccessedByLayers("App")
      .whereLayer("Core")
      .mayOnlyBeAccessedByLayers("App", "Feature")
      .check(classes)
  }

  @Test
  fun `feature isolation`() {
    slices()
      .matching("..${basePackage}..feature.(*)..")
      .should()
      .notDependOnEachOther()
      .check(classes)
  }

  @Test
  fun `layers depend downward`() {
    layeredArchitecture()
      .consideringAllDependencies()
      .optionalLayer("Controller")
      .definedBy("..${basePackage}..controller..")
      .optionalLayer("Service")
      .definedBy("..${basePackage}..service..")
      .optionalLayer("Repository")
      .definedBy("..${basePackage}..repository..")
      .optionalLayer("Model")
      .definedBy("..${basePackage}..model..")
      .whereLayer("Controller")
      .mayNotBeAccessedByAnyLayer()
      .whereLayer("Service")
      .mayOnlyBeAccessedByLayers("Controller")
      .whereLayer("Repository")
      .mayOnlyBeAccessedByLayers("Controller", "Service")
      .whereLayer("Model")
      .mayOnlyBeAccessedByLayers("Controller", "Service", "Repository")
      .check(classes)
  }
}
