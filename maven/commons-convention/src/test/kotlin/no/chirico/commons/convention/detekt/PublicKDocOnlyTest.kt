package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/** Verifies [PublicKDocOnly] bans every comment except KDoc on a public declaration. */
class PublicKDocOnlyTest {

  private fun lint(code: String) =
    PublicKDocOnly(TestConfig())
      .visitFile(compileContentForTest(code, "Sample.kt"), FakeLanguageVersionSettings())

  /** A KDoc block attached to a public class produces no findings. */
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

  /** A KDoc block attached to a private declaration is rejected. */
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

  /** A plain `//` line comment is always rejected. */
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

  /** The `x-release-please-version` directive comment is recognised by content and allowed. */
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

  /** A KDoc block with no following declaration to document is rejected. */
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
