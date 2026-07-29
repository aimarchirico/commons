package no.chirico.commons.firebaseadmin

import org.springframework.boot.context.properties.ConfigurationProperties

/**
 * Settings bound from the `firebase` configuration prefix.
 *
 * @property credentialsPath Path to the service account JSON the Admin SDK initialises from.
 * @property allowedEmails Emails permitted to authenticate. An empty list allows every verified
 *   account.
 */
@ConfigurationProperties(prefix = "firebase")
data class FirebaseProperties(
  val credentialsPath: String = "/app/config/firebase-service-account.json",
  val allowedEmails: List<String> = emptyList(),
)
