package no.chirico.commons.convention.detekt

import com.intellij.psi.PsiComment
import com.intellij.psi.PsiElement
import com.intellij.psi.PsiWhiteSpace
import dev.detekt.api.Config
import dev.detekt.api.Entity
import dev.detekt.api.Finding
import dev.detekt.api.Rule
import org.jetbrains.kotlin.psi.KtAnnotationEntry
import org.jetbrains.kotlin.psi.KtFile

/**
 * Requires every `@Suppress` annotation to be preceded by a `// suppressed: <reason>` comment
 * explaining why the suppression is necessary, mirroring the reason
 * `@eslint-community/eslint-comments/require-description` demands of a suppressing `eslint-disable`
 * comment on the TypeScript side.
 *
 * The reason must be at least 10 characters, matching this repository's
 * `ban-ts-comment`/`minimumDescriptionLength` convention for `@ts-expect-error`.
 */
class SuppressRequiresReason(config: Config) :
  Rule(
    config,
    "A `@Suppress` annotation must be preceded by a `// suppressed: <reason>` comment.",
  ) {

  override fun visitAnnotationEntry(annotationEntry: KtAnnotationEntry) {
    super.visitAnnotationEntry(annotationEntry)
    if (annotationEntry.shortName?.asString() != SUPPRESS_ANNOTATION_NAME) return

    val precedingComment = findPrecedingComment(annotationEntry)
    if (precedingComment == null || !REASON_PATTERN.containsMatchIn(precedingComment.text)) {
      report(Finding(Entity.from(annotationEntry), MESSAGE))
    }
  }

  private tailrec fun findPrecedingComment(element: PsiElement): PsiComment? {
    val sibling = element.prevSibling.skipWhitespace()
    val parent = element.parent
    return when {
      sibling is PsiComment -> sibling
      sibling != null -> null
      parent == null || parent is KtFile -> null
      else -> findPrecedingComment(parent)
    }
  }

  private tailrec fun PsiElement?.skipWhitespace(): PsiElement? =
    if (this is PsiWhiteSpace) prevSibling.skipWhitespace() else this

  private companion object {
    const val SUPPRESS_ANNOTATION_NAME = "Suppress"
    val REASON_PATTERN = Regex("""^//\s*suppressed:\s*\S.{9,}""")

    const val MESSAGE =
      "A `@Suppress` annotation must be preceded by a `// suppressed: <reason>` comment " +
        "explaining why (at least 10 characters)."
  }
}
