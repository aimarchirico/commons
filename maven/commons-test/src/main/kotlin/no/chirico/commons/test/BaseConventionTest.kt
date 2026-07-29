package no.chirico.commons.test

import com.tngtech.archunit.core.importer.ClassFileImporter
import com.tngtech.archunit.core.importer.ImportOption
import java.io.File
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertAll

/**
 * File-level conventions every service inherits by extending this class.
 *
 * The checks walk the working directory rather than the classpath, so they cover sources that never
 * compile into a class.
 */
abstract class BaseConventionTest {

  protected val allClasses by lazy {
    ClassFileImporter()
      .withImportOption(ImportOption.DoNotIncludeTests())
      .importPackages(javaClass.packageName)
  }

  /** Asserts that every Kotlin file under `src/main` is named in PascalCase. */
  @Test
  fun `Kotlin files should use PascalCase naming`() {
    val rootDir = File(System.getProperty("user.dir"))
    val pascalCaseRegex = Regex("^[A-Z][a-zA-Z0-9]*\\.kt$")

    val violations =
      rootDir
        .walkTopDown()
        .filter { it.isFile && it.extension == "kt" && it.path.contains("src/main/") }
        .filter { !pascalCaseRegex.matches(it.name) }
        .map { it.relativeTo(rootDir).path }
        .toList()

    assertAll(violations.map { { throw AssertionError("File '$it' does not follow PascalCase") } })
  }

  /** Asserts that no Kotlin file under `src/main` exceeds 300 lines. */
  @Test
  fun `Kotlin files should not exceed 300 lines`() {
    val rootDir = File(System.getProperty("user.dir"))
    val maxLines = 300

    val violations =
      rootDir
        .walkTopDown()
        .filter { it.isFile && it.extension == "kt" && it.path.contains("src/main/") }
        .mapNotNull { file ->
          val lineCount = file.readLines().size
          if (lineCount > maxLines) {
            "${file.relativeTo(rootDir).path}: $lineCount lines (max: $maxLines)"
          } else {
            null
          }
        }
        .toList()

    assertAll(violations.map { { throw AssertionError("File line count violation: $it") } })
  }
}
