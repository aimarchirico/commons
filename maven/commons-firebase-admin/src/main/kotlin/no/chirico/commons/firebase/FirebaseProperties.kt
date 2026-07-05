package no.chirico.commons.firebase

import org.springframework.boot.context.properties.ConfigurationProperties

@ConfigurationProperties(prefix = "firebase")
data class FirebaseProperties(
  val credentialsPath: List<String> =
    listOf("/app/config/firebase-service-account.json", "../firebase-service-account.json"),
  val allowedEmails: List<String> = emptyList(),
)
