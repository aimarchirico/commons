package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class PublicKDocOnlyTest {

  private fun lint(code: String) =
    PublicKDocOnly(TestConfig())
      .visitFile(compileContentForTest(code, "Sample.kt"), FakeLanguageVersionSettings())

  @Test
  fun `allows a kdoc block documenting a public class`() {
    val code =
      """
      package foo

      /** Documents Foo. */
      class Foo
      """
        .trimIndent()

    assertThat(lint(code)).isEmpty()
  }

  @Test
  fun `flags a kdoc block on a private declaration`() {
    val code =
      """
      package foo

      class Foo {
        /** Should not be here. */
        private val bar = 1
      }
      """
        .trimIndent()

    val findings = lint(code)

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("reserved for public declarations")
  }

  @Test
  fun `flags a plain line comment`() {
    val code =
      """
      package foo

      // just a note
      class Foo
      """
        .trimIndent()

    val findings = lint(code)

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("Only KDoc blocks are allowed")
  }

  @Test
  fun `allows the release-please version directive comment`() {
    val code =
      """
      package foo

      // x-release-please-version
      class Foo
      """
        .trimIndent()

    assertThat(lint(code)).isEmpty()
  }

  @Test
  fun `flags an orphaned kdoc block with no declaration to document`() {
    val code =
      """
      package foo

      class Foo

      /** trailing doc with nothing left to document */
      """
        .trimIndent()

    val findings = lint(code)

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("does not document any declaration")
  }
}
