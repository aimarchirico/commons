package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/** Verifies [FileNaming] requires Kotlin file names to be PascalCase. */
class FileNamingTest {

  private fun lint(fileName: String) =
    FileNaming(TestConfig())
      .visitFile(compileContentForTest("package foo\n", fileName), FakeLanguageVersionSettings())

  /** A file name that isn't PascalCase is flagged. */
  @Test
  fun `flags file names that are not PascalCase`() {
    val findings = lint("lowerCase.kt")

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("does not follow PascalCase")
  }

  /** A PascalCase file name produces no findings. */
  @Test
  fun `does not flag PascalCase file names`() {
    assertThat(lint("GoodName.kt")).isEmpty()
  }
}
