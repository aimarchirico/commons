package no.chirico.commons.convention

import org.gradle.api.GradleException
import org.gradle.api.artifacts.ProjectDependency

// Enforces the api/impl/core modular-monolith dependency rules at configuration time.
//
//   :app     -> :*:impl, :core*
//   :*:impl  -> :*:api,  :core*
//   :*:api   -> :core*
//   :core*   -> :core*
//
// Any other project-to-project dependency fails the build before compilation.
// Because :api modules only reach :core, cross-feature cycles are impossible.
afterEvaluate {
    val current = project.path
    configurations.configureEach {
        dependencies.withType(ProjectDependency::class.java).forEach { dep ->
            val target = dep.path
            val allowed =
                when {
                    current == ":app" -> target.endsWith(":impl") || target.startsWith(":core")
                    current.endsWith(":impl") -> target.endsWith(":api") || target.startsWith(":core")
                    current.endsWith(":api") -> target.startsWith(":core")
                    current.startsWith(":core") -> target.startsWith(":core")
                    else -> false
                }
            if (!allowed) {
                throw GradleException("Architecture violation: $current may not depend on $target")
            }
        }
    }
}
