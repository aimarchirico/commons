package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/**
 * Verifies [SuppressRequiresReason] requires a `// suppressed: <reason>` comment before
 * `@Suppress`.
 */
class SuppressRequiresReasonTest {

  private fun lint(code: String) =
    SuppressRequiresReason(TestConfig())
      .visitFile(compileContentForTest(code, "Sample.kt"), FakeLanguageVersionSettings())

  /** A `@Suppress` annotation preceded by a reason comment produces no findings. */
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

  /** A `@Suppress` annotation with no preceding comment is flagged. */
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

  /** A `@Suppress` annotation whose reason is under 10 characters is flagged. */
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

  /** An annotation other than `@Suppress` produces no findings. */
  @Test
  fun `ignores annotations that are not Suppress`() {
    val code =
      """
      package foo

      class Foo {
        @JvmStatic
        fun bar() = Unit
      }
      """
        .trimIndent()

    assertThat(lint(code)).isEmpty()
  }

  /**
   * A top-level `@Suppress` with no preceding sibling comment exercises the
   * `parent is KtFile` branch inside `findPrecedingComment`.
   */
  @Test
  fun `flags a top-level suppress annotation with no preceding reason comment`() {
    val code =
      """
      package foo

      @Suppress("unused")
      class Foo
      """
        .trimIndent()

    assertThat(lint(code)).hasSize(1)
  }
}
