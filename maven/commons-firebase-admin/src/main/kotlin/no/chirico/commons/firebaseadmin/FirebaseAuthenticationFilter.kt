package no.chirico.commons.firebaseadmin

import com.google.firebase.auth.FirebaseAuth
import com.google.firebase.auth.FirebaseAuthException
import jakarta.servlet.FilterChain
import jakarta.servlet.http.HttpServletRequest
import jakarta.servlet.http.HttpServletResponse
import org.springframework.security.authentication.UsernamePasswordAuthenticationToken
import org.springframework.security.core.context.SecurityContextHolder
import org.springframework.security.web.authentication.WebAuthenticationDetailsSource
import org.springframework.web.filter.OncePerRequestFilter

/**
 * Authenticates requests carrying a Firebase ID token in the `Authorization` header.
 *
 * A verified token whose email passes the allow list populates the security context. A missing or
 * unverifiable token leaves the context empty and lets the chain continue, so the security
 * configuration decides whether the endpoint was public. A verified token outside the allow list is
 * rejected outright.
 */
class FirebaseAuthenticationFilter(private val properties: FirebaseProperties) :
  OncePerRequestFilter() {

  override fun doFilterInternal(
    request: HttpServletRequest,
    response: HttpServletResponse,
    filterChain: FilterChain,
  ) {
    val header = request.getHeader("Authorization")
    if (header != null && header.startsWith("Bearer ")) {
      try {
        val decoded = FirebaseAuth.getInstance().verifyIdToken(header.substring(7))
        val email = decoded.email
        val allowed = properties.allowedEmails
        if (allowed.isEmpty() || allowed.any { it.equals(email, ignoreCase = true) }) {
          val auth = UsernamePasswordAuthenticationToken(decoded.uid, null, emptyList())
          auth.details = WebAuthenticationDetailsSource().buildDetails(request)
          SecurityContextHolder.getContext().authentication = auth
        } else {
          logger.warn("Access denied for email: $email")
          response.sendError(HttpServletResponse.SC_FORBIDDEN, "Access denied")
          return
        }
      } catch (e: FirebaseAuthException) {
        logger.error("Token verification failed: ${e.message}")
      }
    }
    filterChain.doFilter(request, response)
  }
}
