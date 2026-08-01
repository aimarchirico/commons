package no.chirico.commons.convention.detekt

import dev.detekt.test.FakeLanguageVersionSettings
import dev.detekt.test.TestConfig
import dev.detekt.test.utils.compileContentForTest
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

class FileNamingTest {

  private fun lint(fileName: String) =
    FileNaming(TestConfig())
      .visitFile(compileContentForTest("package foo\n", fileName), FakeLanguageVersionSettings())

  @Test
  fun `flags file names that are not PascalCase`() {
    val findings = lint("lowerCase.kt")

    assertThat(findings).hasSize(1)
    assertThat(findings.single().message).contains("does not follow PascalCase")
  }

  @Test
  fun `does not flag PascalCase file names`() {
    assertThat(lint("GoodName.kt")).isEmpty()
  }
}
