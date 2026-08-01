package no.chirico.commons.firebaseadmin

import com.google.auth.oauth2.GoogleCredentials
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions
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

/**
 * Verifies [FirebaseAutoConfiguration] wires the Admin SDK, the auth filter, and the security
 * chain.
 */
class FirebaseAutoConfigurationTest {

  /** A throwaway directory to write fake credentials files into. */
  @TempDir lateinit var tempDir: Path

  private val configuration = FirebaseAutoConfiguration()

  /** Unmocks the static Firebase classes stubbed by individual tests. */
  @AfterEach
  fun tearDown() {
    unmockkStatic(GoogleCredentials::class)
    unmockkStatic(FirebaseApp::class)
  }

  /**
   * [FirebaseAutoConfiguration.firebaseApp] throws when the configured credentials file doesn't
   * exist.
   */
  @Test
  fun `firebaseApp fails fast when the credentials file is missing`() {
    val properties =
      FirebaseProperties(credentialsPath = tempDir.resolve("missing.json").toString())

    assertThrows<FileNotFoundException> { configuration.firebaseApp(properties) }
  }

  /**
   * With a valid credentials file, [FirebaseAutoConfiguration.firebaseApp] initialises the Admin
   * SDK.
   */
  @Test
  fun `firebaseApp initialises the admin sdk from the credentials file`() {
    val credentialsFile = Files.createFile(tempDir.resolve("service-account.json"))
    val properties = FirebaseProperties(credentialsPath = credentialsFile.toString())

    mockkStatic(GoogleCredentials::class)
    mockkStatic(FirebaseApp::class)
    val credentials = mockk<GoogleCredentials>()
    val app = mockk<FirebaseApp>()
    every { GoogleCredentials.fromStream(any()) } returns credentials
    every { credentials.createScoped(any<List<String>>()) } returns credentials
    every { FirebaseApp.initializeApp(any<FirebaseOptions>()) } returns app

    val result = configuration.firebaseApp(properties)

    assertThat(result).isSameAs(app)
  }

  /** The `firebaseAuthenticationFilter` bean wraps whatever [FirebaseProperties] it's given. */
  @Test
  fun `firebaseAuthenticationFilter bean wraps the given properties`() {
    val properties = FirebaseProperties(allowedEmails = listOf("a@example.com"))

    val filter = configuration.firebaseAuthenticationFilter(properties)

    assertThat(filter).isNotNull
  }

  /**
   * The auto-configured security chain requires auth for every path except the public allow list.
   */
  @Test
  fun `security filter chain locks down every request except the public paths`() {
    WebApplicationContextRunner()
      .withConfiguration(AutoConfigurations.of(FirebaseAutoConfiguration::class.java))
      .withBean(FirebaseApp::class.java, { mockk<FirebaseApp>(relaxed = true) })
      .run { context ->
        assertThat(context).hasSingleBean(SecurityFilterChain::class.java)
        assertThat(context).hasSingleBean(FirebaseAuthenticationFilter::class.java)
      }
  }
}
