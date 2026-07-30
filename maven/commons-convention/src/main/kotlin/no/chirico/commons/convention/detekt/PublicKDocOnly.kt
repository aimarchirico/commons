package no.chirico.commons.convention.detekt

import com.intellij.psi.PsiComment
import dev.detekt.api.Config
import dev.detekt.api.Entity
import dev.detekt.api.Finding
import dev.detekt.api.Rule
import org.jetbrains.kotlin.kdoc.psi.api.KDoc
import org.jetbrains.kotlin.lexer.KtTokens
import org.jetbrains.kotlin.psi.KtDeclaration
import org.jetbrains.kotlin.psi.KtPsiUtil
import org.jetbrains.kotlin.psi.psiUtil.visibilityModifierTypeOrDefault

/**
 * Bans every comment except KDoc blocks that document a public declaration, plus a small set of
 * content-recognised tooling directives.
 *
 * Explanation belongs in a KDoc block attached to the public declaration it describes. A line
 * comment, a plain block comment, a KDoc block with no attached declaration, or a KDoc block on a
 * non-public declaration is therefore always a violation. "Public" mirrors the visibility check
 * `UndocumentedPublicClass`/`UndocumentedPublicFunction`/`UndocumentedPublicProperty` already
 * apply: not `private`/`internal`/`protected`, and not local to a function body.
 *
 * A directive comment such as `// x-release-please-version` or `// suppressed: <reason>` is
 * recognised by content rather than by file path, so it stays legal wherever it appears (for
 * example in a `build.gradle.kts` version line, or immediately above a `@Suppress` annotation).
 *
 * Comments are matched as lexer tokens rather than as text, so delimiters appearing inside string
 * literals, such as a URL or a glob path pattern, are never mistaken for comments.
 */
class PublicKDocOnly(config: Config) :
  Rule(config, "Only KDoc blocks documenting public declarations are allowed as comments.") {

  override fun visitComment(comment: PsiComment) {
    super.visitComment(comment)
    if (comment is KDoc) {
      val owner = comment.owner
      when {
        owner == null -> report(Finding(Entity.from(comment), ORPHANED_MESSAGE))
        isNonPublic(owner) -> report(Finding(Entity.from(comment), NON_PUBLIC_MESSAGE))
      }
      return
    }
    if (DIRECTIVE_PATTERN.containsMatchIn(comment.text)) return
    report(Finding(Entity.from(comment), MESSAGE))
  }

  private fun isNonPublic(declaration: KtDeclaration): Boolean =
    KtPsiUtil.isLocal(declaration) ||
      declaration.visibilityModifierTypeOrDefault() != KtTokens.PUBLIC_KEYWORD

  private companion object {
    val DIRECTIVE_PATTERN = Regex("""^//\s*(x-release-please-version\b|suppressed:\s*\S.{9,})""")

    const val MESSAGE =
      "Only KDoc blocks are allowed. Attach the explanation to the declaration it " +
        "describes, or delete it."
    const val ORPHANED_MESSAGE =
      "This KDoc block does not document any declaration. Attach it to one, or delete it."
    const val NON_PUBLIC_MESSAGE =
      "KDoc blocks are reserved for public declarations. Make the declaration public, or " +
        "delete this comment."
  }
}
