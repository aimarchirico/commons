package no.chirico.commons.security

import jakarta.servlet.http.HttpServletResponse
import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.mock.web.MockFilterChain
import org.springframework.mock.web.MockHttpServletRequest
import org.springframework.mock.web.MockHttpServletResponse
import org.springframework.test.util.ReflectionTestUtils

class ProxyValidationFilterTest {

  private fun filterWithSecret(secret: String): ProxyValidationFilter =
    ProxyValidationFilter().also { ReflectionTestUtils.setField(it, "proxySecret", secret) }

  @Test
  fun `request continues when no proxy secret is configured`() {
    val filter = filterWithSecret("")
    val request = MockHttpServletRequest()
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(chain.request).isNotNull
  }

  @Test
  fun `request continues when the proxy header matches the configured secret`() {
    val filter = filterWithSecret("s3cret")
    val request = MockHttpServletRequest().apply { addHeader("X-Proxy-Secret", "s3cret") }
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(chain.request).isNotNull
  }

  @Test
  fun `request is rejected when the proxy header is missing or wrong`() {
    val filter = filterWithSecret("s3cret")
    val request = MockHttpServletRequest()
    val response = MockHttpServletResponse()
    val chain = MockFilterChain()

    filter.doFilter(request, response, chain)

    assertThat(response.status).isEqualTo(HttpServletResponse.SC_FORBIDDEN)
    assertThat(chain.request).isNull()
  }
}
