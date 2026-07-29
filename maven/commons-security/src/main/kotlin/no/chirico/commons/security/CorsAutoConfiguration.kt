package no.chirico.commons.security

import org.springframework.boot.autoconfigure.AutoConfiguration
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty
import org.springframework.boot.context.properties.ConfigurationProperties
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.context.annotation.Bean
import org.springframework.core.Ordered
import org.springframework.core.annotation.Order
import org.springframework.web.cors.CorsConfiguration
import org.springframework.web.cors.UrlBasedCorsConfigurationSource
import org.springframework.web.filter.CorsFilter

/**
 * Settings bound from the `cors` configuration prefix.
 *
 * @property allowedOrigins Origins permitted to call the API. Leaving it empty switches the CORS
 *   configuration off entirely.
 */
@ConfigurationProperties(prefix = "cors")
data class CorsProperties(val allowedOrigins: List<String> = emptyList())

/**
 * Registers a CORS filter when `cors.allowed-origins` is set.
 *
 * The whole configuration is conditional on that property, so an application that never serves
 * browsers pays nothing for it.
 */
@AutoConfiguration
@EnableConfigurationProperties(CorsProperties::class)
@ConditionalOnProperty(prefix = "cors", name = ["allowed-origins"])
class CorsAutoConfiguration {

  /**
   * Builds the CORS filter for the configured origins.
   *
   * It runs at the highest precedence, ahead of [ProxyValidationFilter], because preflight requests
   * carry no `X-Proxy-Secret` header and would otherwise be rejected before the browser ever sends
   * the real request.
   *
   * @param properties The bound CORS settings.
   * @return The filter, applied to every path.
   */
  @Bean
  @Order(Ordered.HIGHEST_PRECEDENCE)
  fun corsFilter(properties: CorsProperties): CorsFilter {
    val config =
      CorsConfiguration().apply {
        allowedOrigins = properties.allowedOrigins
        allowedMethods = listOf("GET", "POST", "PUT", "PATCH", "DELETE", "OPTIONS")
        allowedHeaders = listOf("*")
        allowCredentials = true
      }
    val source =
      UrlBasedCorsConfigurationSource().apply { registerCorsConfiguration("/**", config) }
    return CorsFilter(source)
  }
}
