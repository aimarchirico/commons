package no.chirico.commons.convention.detekt

import com.intellij.psi.PsiComment
import dev.detekt.api.Config
import dev.detekt.api.Entity
import dev.detekt.api.Finding
import dev.detekt.api.Rule
import org.jetbrains.kotlin.kdoc.psi.api.KDoc

/**
 * Bans every comment except KDoc blocks.
 *
 * Explanation belongs in a KDoc block attached to the declaration it describes, so a line comment
 * or a plain block comment is always a violation, whether it sits on its own line or trails code.
 *
 * Comments are matched as lexer tokens rather than as text, so delimiters appearing inside string
 * literals, such as a URL or a glob path pattern, are never mistaken for comments.
 */
class NonDocComment(config: Config) :
  Rule(config, "Only KDoc blocks are allowed as comments.") {

  override fun visitComment(comment: PsiComment) {
    super.visitComment(comment)
    if (comment is KDoc) return
    report(Finding(Entity.from(comment), MESSAGE))
  }

  private companion object {
    const val MESSAGE =
      "Only KDoc blocks are allowed. Attach the explanation to the declaration it " +
        "describes, or delete it."
  }
}
