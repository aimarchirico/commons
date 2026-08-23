package no.chirico.commons.convention.detekt

import dev.detekt.api.Config
import dev.detekt.api.Entity
import dev.detekt.api.Finding
import dev.detekt.api.Rule
import org.jetbrains.kotlin.psi.KtFile

/**
 * Reports Kotlin source files that exceed the configured maximum line count.
 *
 * Configurable via `maxLines` (defaults to 300).
 */
class FileLength(config: Config) :
  Rule(config, "Kotlin files must not exceed the configured line count.") {

  private val maxLines: Int by lazy { config.valueOrDefault("maxLines", DEFAULT_MAX_LINES) }

  override fun visitKtFile(file: KtFile) {
    super.visitKtFile(file)
    val lineCount = file.text.lines().size
    if (lineCount > maxLines) {
      report(
        Finding(
          Entity.atPackageOrFirstDecl(file),
          "File line count violation: ${file.name}: $lineCount lines (max: $maxLines)",
        )
      )
    }
  }

  private companion object {
    const val DEFAULT_MAX_LINES = 300
  }
}
