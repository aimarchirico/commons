package no.chirico.commons.convention.detekt

import dev.detekt.api.Config
import dev.detekt.api.Entity
import dev.detekt.api.Finding
import dev.detekt.api.Rule
import org.jetbrains.kotlin.psi.KtFile

/** Requires every Kotlin file name to match PascalCase. */
class FileNaming(config: Config) : Rule(config, "Kotlin file names must be PascalCase.") {

  override fun visitKtFile(file: KtFile) {
    super.visitKtFile(file)
    if (!PASCAL_CASE_REGEX.matches(file.name)) {
      report(
        Finding(Entity.atPackageOrFirstDecl(file), "File '${file.name}' does not follow PascalCase")
      )
    }
  }

  private companion object {
    val PASCAL_CASE_REGEX = Regex("^[A-Z][a-zA-Z0-9]*\\.kt$")
  }
}
