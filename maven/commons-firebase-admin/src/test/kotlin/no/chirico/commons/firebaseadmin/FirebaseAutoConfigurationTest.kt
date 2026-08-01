package no.chirico.commons.firebaseadmin

import com.google.auth.oauth2.GoogleCredentials
import com.google.firebase.FirebaseApp
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import java.io.FileNotFoundException
import java.nio.file.Files
import java.nio.file.Path
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.Test
import org.junit.jupiter.api.assertThrows
import org.junit.jupiter.api.io.TempDir
import org.springframework.boot.autoconfigure.AutoConfigurations
import org.springframework.boot.test.context.runner.WebApplicationContextRunner
import org.springframework.security.web.SecurityFilterChain

class FirebaseAutoConfigurationTest {

  @TempDir lateinit var tempDir: Path

  private val configuration = FirebaseAutoConfiguration()

  @AfterEach
  fun tearDown() {
    unmockkStatic(GoogleCredentials::class)
    unmockkStatic(FirebaseApp::class)
  }

  @Test
  fun `firebaseApp fails fast when the credentials file is missing`() {
    val properties = FirebaseProperties(credentialsPath = tempDir.resolve("missing.json").toString())

    assertThrows<FileNotFoundException> { configuration.firebaseApp(properties) }
  }

  @Test
  fun `firebaseApp initialises the admin sdk from the credentials file`() {
    val credentialsFile = Files.createFile(tempDir.resolve("service-account.json"))
    val properties = FirebaseProperties(credentialsPath = credentialsFile.toString())

    mockkStatic(GoogleCredentials::class)
    mockkStatic(FirebaseApp::class)
    val credentials = mockk<GoogleCredentials>()
    val app = mockk<FirebaseApp>()
    every { GoogleCredentials.fromStream(any()) } returns credentials
    every { FirebaseApp.initializeApp(any()) } returns app

    val result = configuration.firebaseApp(properties)

    assertThat(result).isSameAs(app)
  }

  @Test
  fun `firebaseAuthenticationFilter bean wraps the given properties`() {
    val properties = FirebaseProperties(allowedEmails = listOf("a@example.com"))

    val filter = configuration.firebaseAuthenticationFilter(properties)

    assertThat(filter).isNotNull
  }

  @Test
  fun `security filter chain locks down every request except the public paths`() {
    WebApplicationContextRunner()
      .withConfiguration(AutoConfigurations.of(FirebaseAutoConfiguration::class.java))
      .withBean(FirebaseApp::class.java) { mockk<FirebaseApp>(relaxed = true) }
      .run { context ->
        assertThat(context).hasSingleBean(SecurityFilterChain::class.java)
        assertThat(context).hasSingleBean(FirebaseAuthenticationFilter::class.java)
      }
  }
}
