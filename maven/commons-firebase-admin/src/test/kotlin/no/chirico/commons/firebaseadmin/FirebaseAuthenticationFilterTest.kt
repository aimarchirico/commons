package no.chirico.commons.firebaseadmin

import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseAuthException
import com.google.firebase.auth.FirebaseToken
import io.mockk.every
import io.mockk.mockk
import io.mockk.mockkStatic
import io.mockk.unmockkStatic
import jakarta.servlet.http.HttpServletResponse
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.AfterEach
import org.junit.jupiter.api.BeforeEach
import org.junit.jupiter.api.Test
import org.springframework.mock.web.MockFilterChain
import org.springframework.mock.web.MockHttpServletRequest
import org.springframework.mock.web.MockHttpServletResponse
import org.springframework.security.core.context.SecurityContextHolder

/**
 * Verifies [FirebaseAuthenticationFilter] authenticates requests bearing a valid Firebase token.
 */
class FirebaseAuthenticationFilterTest {

  private val auth = mockk<FirebaseAuth>()

  /** Stubs [FirebaseAuth.getInstance] and clears the security context before each test. */
  @BeforeEach
  fun setUp() {
    mockkStatic(FirebaseAuth::class)
    every { FirebaseAuth.getInstance() } returns auth
    SecurityContextHolder.clearContext()
  }

  /** Unmocks [FirebaseAuth] and clears the security context after each test. */
  @AfterEach
  fun tearDown() {
    unmockkStatic(FirebaseAuth::class)
    SecurityContextHolder.clearContext()
  }

  private fun tokenFor(email: String, uid: String = "uid-1"): FirebaseToken =
    mockk<FirebaseToken> {
      every { this@mockk.email } returns email
      every { this@mockk.uid } returns uid
    }

  /** A request with no Authorization header passes through with no authentication set. */
  @Test
  fun `request without an authorization header continues unauthenticated`() {
    val filter = FirebaseAuthenticationFilter(FirebaseProperties())
    val request = MockHttpServletRequest()
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(chain.request).isNotNull
    assertThat(SecurityContextHolder.getContext().authentication).isNull()
  }

  /**
   * A non-Bearer Authorization header (e.g. Basic) is ignored and the request continues
   * unauthenticated.
   */
  @Test
  fun `request with a non-bearer authorization header continues unauthenticated`() {
    val filter = FirebaseAuthenticationFilter(FirebaseProperties())
    val request = MockHttpServletRequest().apply { addHeader("Authorization", "Basic xyz") }
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(chain.request).isNotNull
    assertThat(SecurityContextHolder.getContext().authentication).isNull()
  }

  /** A verified token whose email is on the allow list authenticates the request as its uid. */
  @Test
  fun `verified token with an allowed email authenticates the request`() {
    every { auth.verifyIdToken("good-token") } returns tokenFor("a@example.com", "uid-1")
    val filter =
      FirebaseAuthenticationFilter(FirebaseProperties(allowedEmails = listOf("a@example.com")))
    val request = MockHttpServletRequest().apply { addHeader("Authorization", "Bearer good-token") }
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(chain.request).isNotNull
    assertThat(SecurityContextHolder.getContext().authentication?.principal).isEqualTo("uid-1")
  }

  /** With no allow list configured, any verified token authenticates the request. */
  @Test
  fun `verified token with an empty allow list authenticates the request`() {
    every { auth.verifyIdToken("good-token") } returns tokenFor("anyone@example.com")
    val filter = FirebaseAuthenticationFilter(FirebaseProperties())
    val request = MockHttpServletRequest().apply { addHeader("Authorization", "Bearer good-token") }
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(SecurityContextHolder.getContext().authentication).isNotNull
  }

  /** A verified token whose email isn't on the allow list is rejected with 403. */
  @Test
  fun `verified token outside the allow list is rejected`() {
    every { auth.verifyIdToken("good-token") } returns tokenFor("outsider@example.com")
    val filter =
      FirebaseAuthenticationFilter(FirebaseProperties(allowedEmails = listOf("a@example.com")))
    val request = MockHttpServletRequest().apply { addHeader("Authorization", "Bearer good-token") }
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(response.status).isEqualTo(HttpServletResponse.SC_FORBIDDEN)
    assertThat(chain.request).isNull()
    assertThat(SecurityContextHolder.getContext().authentication).isNull()
  }

  /**
   * A token that fails verification is treated like no token: the request continues
   * unauthenticated.
   */
  @Test
  fun `unverifiable token continues unauthenticated`() {
    every { auth.verifyIdToken("bad-token") } throws mockk<FirebaseAuthException>(relaxed = true)
    val filter = FirebaseAuthenticationFilter(FirebaseProperties())
    val request = MockHttpServletRequest().apply { addHeader("Authorization", "Bearer bad-token") }
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(chain.request).isNotNull
    assertThat(SecurityContextHolder.getContext().authentication).isNull()
  }
}
