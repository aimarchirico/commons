package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class SuppressRequiresReasonTest {

  private fun lint(code: String) =
    SuppressRequiresReason(TestConfig())
      .visitFile(compileContentForTest(code, "Sample.kt"), FakeLanguageVersionSettings())

  @Test
  fun `allows a suppress annotation preceded by a reason comment`() {
    val code =
      """
      package foo

      class Foo {
        // suppressed: false positive from a library quirk
        @Suppress("unused")
        fun bar() = Unit
      }
      """
        .trimIndent()

    assertThat(lint(code)).isEmpty()
  }

  @Test
  fun `flags a suppress annotation with no preceding reason comment`() {
    val code =
      """
      package foo

      class Foo {
        @Suppress("unused")
        fun bar() = Unit
      }
      """
        .trimIndent()

    val findings = lint(code)

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("must be preceded by")
  }

  @Test
  fun `flags a suppress annotation whose reason is too short`() {
    val code =
      """
      package foo

      class Foo {
        // suppressed: no
        @Suppress("unused")
        fun bar() = Unit
      }
      """
        .trimIndent()

    assertThat(lint(code)).hasSize(1)
  }
}
