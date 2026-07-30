package no.chirico.commons.convention.detekt

import dev.detekt.api.RuleSet
import dev.detekt.api.RuleSetId
import dev.detekt.api.RuleSetProvider

/** Publishes this plugin's custom detekt rules under the `commons` rule set ID. */
class CommonsRuleSetProvider : RuleSetProvider {

  override val ruleSetId = RuleSetId("commons")

  override fun instance(): RuleSet =
    RuleSet(ruleSetId, listOf(::PublicKDocOnly, ::SuppressRequiresReason))
}
