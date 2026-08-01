package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/** Verifies [FileLength] flags Kotlin files that exceed the configured max line count. */
class FileLengthTest {

  private fun lint(rule: FileLength, code: String) =
    rule.visitFile(compileContentForTest(code, "Sample.kt"), FakeLanguageVersionSettings())

  /** A file over the configured max line count is flagged. */
  @Test
  fun `flags files exceeding the configured max line count`() {
    val rule = FileLength(TestConfig("maxLines" to 3))
    val code = "package foo\n\nval a = 1\nval b = 2\nval c = 3\n"

    val findings = lint(rule, code)

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("File line count violation")
  }

  /** A file within the configured max line count produces no findings. */
  @Test
  fun `does not flag files within the configured max line count`() {
    val rule = FileLength(TestConfig("maxLines" to 100))

    assertThat(lint(rule, "package foo\n\nval a = 1\n")).isEmpty()
  }

  /** The max line count defaults to 300 when the rule isn't configured with one. */
  @Test
  fun `defaults the max line count to 300 when unconfigured`() {
    val rule = FileLength(TestConfig())

    assertThat(lint(rule, "package foo\n\nval a = 1\n")).isEmpty()
  }
}
