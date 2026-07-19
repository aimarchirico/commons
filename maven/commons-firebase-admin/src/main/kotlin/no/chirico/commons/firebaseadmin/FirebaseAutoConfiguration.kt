package no.chirico.commons.firebaseadmin

import com.google.auth.oauth2.GoogleCredentials
import com.google.firebase.FirebaseApp
import com.google.firebase.FirebaseOptions
import jakarta.servlet.DispatcherType
import java.io.File
import java.io.FileInputStream
import java.io.FileNotFoundException
import org.springframework.boot.autoconfigure.AutoConfiguration
import org.springframework.boot.autoconfigure.condition.ConditionalOnMissingBean
import org.springframework.boot.context.properties.EnableConfigurationProperties
import org.springframework.context.annotation.Bean
import org.springframework.security.config.annotation.web.builders.HttpSecurity
import org.springframework.security.config.annotation.web.configuration.EnableWebSecurity
import org.springframework.security.config.http.SessionCreationPolicy
import org.springframework.security.web.SecurityFilterChain
import org.springframework.security.web.authentication.UsernamePasswordAuthenticationFilter

@AutoConfiguration
@EnableWebSecurity
@EnableConfigurationProperties(FirebaseProperties::class)
class FirebaseAutoConfiguration {

  private val publicPaths = arrayOf("/swagger-ui/**", "/v3/api-docs/**")

  @Bean
  @ConditionalOnMissingBean
  fun firebaseApp(properties: FirebaseProperties): FirebaseApp {
    val file = File(properties.credentialsPath)
    if (!file.isFile) {
      throw FileNotFoundException(
        "Firebase credentials not found at: ${properties.credentialsPath}"
      )
    }
    val options =
      FirebaseOptions.builder()
        .setCredentials(GoogleCredentials.fromStream(FileInputStream(file)))
        .build()
    return FirebaseApp.initializeApp(options)
  }

  @Bean
  @ConditionalOnMissingBean
  fun firebaseAuthenticationFilter(properties: FirebaseProperties): FirebaseAuthenticationFilter =
    FirebaseAuthenticationFilter(properties)

  @Bean
  @ConditionalOnMissingBean
  fun firebaseSecurityFilterChain(
    http: HttpSecurity,
    filter: FirebaseAuthenticationFilter,
  ): SecurityFilterChain {
    http
      .csrf { it.disable() }
      .cors { it.disable() }
      .sessionManagement { it.sessionCreationPolicy(SessionCreationPolicy.STATELESS) }
      .authorizeHttpRequests {
        it.dispatcherTypeMatchers(DispatcherType.ASYNC).permitAll()
        it.requestMatchers(*publicPaths).permitAll()
        it.anyRequest().authenticated()
      }
      .addFilterBefore(filter, UsernamePasswordAuthenticationFilter::class.java)
    return http.build()
  }
}
