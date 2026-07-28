package no.chirico.commons.convention.detekt

import dev.detekt.api.RuleSet
import dev.detekt.api.RuleSetId
import dev.detekt.api.RuleSetProvider

/** Publishes the documentation rules this plugin adds on top of detekt's own rule sets. */
class CommonsRuleSetProvider : RuleSetProvider {

  override val ruleSetId = RuleSetId("commons")

  override fun instance(): RuleSet = RuleSet(ruleSetId, listOf(::NonDocComment))
}
