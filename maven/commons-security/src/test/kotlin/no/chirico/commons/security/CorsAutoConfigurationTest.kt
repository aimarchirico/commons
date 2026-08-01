package no.chirico.commons.security

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test
import org.springframework.mock.web.MockFilterChain
import org.springframework.mock.web.MockHttpServletRequest
import org.springframework.mock.web.MockHttpServletResponse

class CorsAutoConfigurationTest {

  @Test
  fun `corsFilter grants an allowed origin credentialed access to every method`() {
    val properties = CorsProperties(allowedOrigins = listOf("https://example.com"))
    val filter = CorsAutoConfiguration().corsFilter(properties)

    val request =
      MockHttpServletRequest("GET", "/anything").apply {
        addHeader("Origin", "https://example.com")
      }
    val response = MockHttpServletResponse()

    filter.doFilter(request, response, MockFilterChain())

    assertThat(response.getHeader("Access-Control-Allow-Origin")).isEqualTo("https://example.com")
    assertThat(response.getHeader("Access-Control-Allow-Credentials")).isEqualTo("true")
  }

  @Test
  fun `corsFilter denies an origin outside the allowed list`() {
    val properties = CorsProperties(allowedOrigins = listOf("https://example.com"))
    val filter = CorsAutoConfiguration().corsFilter(properties)

    val request =
      MockHttpServletRequest("GET", "/anything").apply {
        addHeader("Origin", "https://evil.example")
      }
    val response = MockHttpServletResponse()

    filter.doFilter(request, response, MockFilterChain())

    assertThat(response.getHeader("Access-Control-Allow-Origin")).isNull()
  }

  @Test
  fun `corsProperties defaults to no allowed origins`() {
    assertThat(CorsProperties().allowedOrigins).isEmpty()
  }
}
