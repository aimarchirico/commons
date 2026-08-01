package no.chirico.commons.convention.detekt

import com.intellij.psi.PsiComment
import com.intellij.psi.PsiElement
import dev.detekt.api.Config
import dev.detekt.api.Entity
import dev.detekt.api.Finding
import dev.detekt.api.Rule
import org.jetbrains.kotlin.kdoc.psi.api.KDoc
import org.jetbrains.kotlin.lexer.KtTokens
import org.jetbrains.kotlin.psi.KtDeclaration
import org.jetbrains.kotlin.psi.KtFile
import org.jetbrains.kotlin.psi.KtPsiUtil
import org.jetbrains.kotlin.psi.psiUtil.visibilityModifierTypeOrDefault

/**
 * Bans every comment except KDoc blocks that document a public declaration, plus a small set of
 * content-recognised tooling directives, mirroring exactly what
 * `UndocumentedPublicClass`/`UndocumentedPublicFunction`/`UndocumentedPublicProperty` require:
 * documentation is either required and therefore the only thing allowed, or not required and
 * therefore banned outright. There is no optional middle ground.
 *
 * In a file where those rules require documentation, a line comment, a plain block comment, a KDoc
 * block with no attached declaration, or a KDoc block on a non-public declaration is always a
 * violation; a KDoc block on a public declaration is the only thing allowed. "Public" mirrors the
 * visibility check those rules already apply: not `private`/`internal`/`protected`, and not local
 * to a function body.
 *
 * In a file those rules exempt from requiring documentation (test sources, and a project's own
 * `build.gradle.kts`, not a precompiled script plugin like `kotlin.gradle.kts`, which is real
 * shipped source and stays subject to the normal rule), every comment is banned outright, KDoc
 * included, since nothing there is required to carry one.
 *
 * A directive comment such as `// x-release-please-version` or `// suppressed: <reason>` is
 * recognised by content rather than by file path, so it stays legal everywhere, including test
 * sources and build scripts (for example in a `build.gradle.kts` version line, or immediately above
 * a `@Suppress` annotation in a test).
 *
 * Comments are matched as lexer tokens rather than as text, so delimiters appearing inside string
 * literals, such as a URL or a glob path pattern, are never mistaken for comments.
 */
class PublicKDocOnly(config: Config) :
  Rule(config, "Only KDoc blocks documenting public declarations are allowed as comments.") {

  private var docsRequired = true

  override fun visitKtFile(file: KtFile) {
    docsRequired = file.virtualFile?.path?.let { !isDocsExemptPath(it) } ?: true
    super.visitKtFile(file)
  }

  /**
   * `KDocImpl.accept` dispatches straight to `visitElement` rather than `visitComment`, unlike
   * plain comments, so this rule has to hook the generic catch-all to see both.
   */
  override fun visitElement(element: PsiElement) {
    super.visitElement(element)
    if (element !is PsiComment) return
    checkComment(element)
  }

  private fun checkComment(comment: PsiComment) {
    if (DIRECTIVE_PATTERN.containsMatchIn(comment.text)) return
    when {
      !docsRequired -> report(Finding(Entity.from(comment), NOT_REQUIRED_MESSAGE))
      comment is KDoc -> checkKDoc(comment)
      else -> report(Finding(Entity.from(comment), MESSAGE))
    }
  }

  private fun checkKDoc(kdoc: KDoc) {
    val owner = kdoc.owner
    when {
      owner == null -> report(Finding(Entity.from(kdoc), ORPHANED_MESSAGE))
      isNonPublic(owner) -> report(Finding(Entity.from(kdoc), NON_PUBLIC_MESSAGE))
    }
  }

  private fun isNonPublic(declaration: KtDeclaration): Boolean =
    KtPsiUtil.isLocal(declaration) ||
      declaration.visibilityModifierTypeOrDefault() != KtTokens.PUBLIC_KEYWORD

  private fun isDocsExemptPath(path: String): Boolean {
    val normalized = path.replace('\\', '/')
    return normalized.contains("/src/test/") ||
      normalized.substringAfterLast('/') == "build.gradle.kts"
  }

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
    const val NOT_REQUIRED_MESSAGE =
      "Documentation isn't required in test sources or build scripts, so it can't be optional " +
        "either: comments, KDoc included, aren't allowed here. Delete this comment."
  }
}
