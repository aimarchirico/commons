package no.chirico.commons.firebaseadmin

import org.springframework.boot.context.properties.ConfigurationProperties

@ConfigurationProperties(prefix = "firebase")
data class FirebaseProperties(
  val credentialsPath: String = "/app/config/firebase-service-account.json",
  val allowedEmails: List<String> = emptyList(),
)
