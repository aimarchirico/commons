package no.chirico.commons.firebaseadmin

import org.assertj.core.api.Assertions.assertThat
import org.junit.jupiter.api.Test

/** Verifies [FirebaseProperties] defaults and binds its configured values correctly. */
class FirebasePropertiesTest {

  /**
   * With no configuration, the properties default to the standard container path and no allow list.
   */
  @Test
  fun `defaults to the standard container credentials path and no email restriction`() {
    val properties = FirebaseProperties()

    assertThat(properties.credentialsPath).isEqualTo("/app/config/firebase-service-account.json")
    assertThat(properties.allowedEmails).isEmpty()
  }

  /** An explicitly configured path and allow list are bound as given. */
  @Test
  fun `binds the configured path and allow list`() {
    val properties =
      FirebaseProperties(credentialsPath = "/tmp/creds.json", allowedEmails = listOf("a@b.com"))

    assertThat(properties.credentialsPath).isEqualTo("/tmp/creds.json")
    assertThat(properties.allowedEmails).containsExactly("a@b.com")
  }
}
