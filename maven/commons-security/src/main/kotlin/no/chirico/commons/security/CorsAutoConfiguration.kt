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

@ConfigurationProperties(prefix = "cors")
data class CorsProperties(val allowedOrigins: List<String> = emptyList())

@AutoConfiguration
@EnableConfigurationProperties(CorsProperties::class)
@ConditionalOnProperty(prefix = "cors", name = ["allowed-origins"])
class CorsAutoConfiguration {

  // Ahead of ProxyValidationFilter: preflight requests carry no X-Proxy-Secret header.
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
