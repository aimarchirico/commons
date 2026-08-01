package no.chirico.commons.convention.detekt

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/**
 * Verifies [CommonsRuleSetProvider] publishes the bundled rules under the `commons` rule set id.
 */
class CommonsRuleSetProviderTest {

  /** All four rules are published under the `commons` rule set id. */
  @Test
  fun `publishes the four commons rules under the commons rule set id`() {
    val provider = CommonsRuleSetProvider()

    assertThat(provider.ruleSetId.value).isEqualTo("commons")
    assertThat(provider.instance().rules).hasSize(4)
  }
}
