package no.chirico.commons.convention

import java.io.File
import org.gradle.testing.jacoco.tasks.JacocoCoverageVerification
import org.gradle.testing.jacoco.tasks.JacocoReport
import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
  kotlin("jvm")
  id("com.ncorti.ktfmt.gradle")
  id("dev.detekt")
  jacoco
}

configure<com.ncorti.ktfmt.gradle.KtfmtExtension> { googleStyle() }

/**
 * Unpack the documentation rules bundled in this plugin so consuming builds inherit them without
 * declaring a detekt configuration of their own. The anonymous object resolves the resource against
 * this plugin's own jar.
 */
val bundledDetektConfig =
  checkNotNull(object {}.javaClass.getResource("/detekt.yaml")) {
    "commons-convention is missing its bundled detekt.yaml"
  }

val detektConfigFile = layout.buildDirectory.file("detekt/commons-detekt.yaml").get().asFile

detektConfigFile.parentFile.mkdirs()

detektConfigFile.writeText(bundledDetektConfig.readText())

configure<dev.detekt.gradle.extensions.DetektExtension> {
  buildUponDefaultConfig.set(true)
  config.setFrom(detektConfigFile)
  source.from(file("build.gradle.kts"))
}

/**
 * Put this plugin's own artifact on detekt's rule classpath, which is how detekt discovers the rule
 * set bundled alongside these scripts. Applying this plugin via `plugins { }` only puts it on the
 * buildscript classpath; detekt's Gradle task loads custom rule providers exclusively from jars
 * declared on the `detektPlugins` configuration, so the `RuleSetProvider` here would otherwise
 * never be found. Resolving the artifact from the enclosing class keeps the coordinates and version
 * out of the script, so the rules can never drift from the plugin shipping them.
 */
val conventionArtifact = object {}.javaClass.protectionDomain?.codeSource?.location

dependencies {
  if (conventionArtifact != null) {
    add("detektPlugins", files(File(conventionArtifact.toURI())))
  }
  testImplementation(kotlin("test-junit5"))
  testRuntimeOnly("org.junit.platform:junit-platform-launcher")
}

configure<org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension> {
  compilerOptions {
    jvmTarget.set(JvmTarget.JVM_25)
    freeCompilerArgs.addAll("-Xjsr305=strict", "-java-parameters")
  }
}

configure<org.gradle.api.plugins.JavaPluginExtension> {
  toolchain { languageVersion.set(JavaLanguageVersion.of(25)) }
}

tasks.withType<Test>().configureEach {
  useJUnitPlatform()
  finalizedBy(tasks.named("jacocoTestReport"))
}

tasks.named<JacocoReport>("jacocoTestReport") { dependsOn(tasks.named("test")) }

/**
 * Requires 80% line coverage and 80% branch coverage across each module's whole build, so a few
 * thin classes don't force pointless tests.
 */
tasks.named<JacocoCoverageVerification>("jacocoTestCoverageVerification") {
  dependsOn(tasks.named("jacocoTestReport"))
  violationRules {
    rule {
      element = "BUNDLE"
      limit {
        counter = "LINE"
        value = "COVEREDRATIO"
        minimum = "0.80".toBigDecimal()
      }
      limit {
        counter = "BRANCH"
        value = "COVEREDRATIO"
        minimum = "0.80".toBigDecimal()
      }
    }
  }
}

val verifyTestSourcesPresent =
  tasks.register("verifyTestSourcesPresent") {
    group = "verification"
    description = "Fails if this module has main sources but no test sources."
    val sourceSets = project.the<org.gradle.api.tasks.SourceSetContainer>()
    val sourceExtensions = setOf("kt", "java")
    val mainSources =
      sourceSets.getByName("main").allSource.filter { it.extension in sourceExtensions }
    val testSources =
      sourceSets.getByName("test").allSource.filter { it.extension in sourceExtensions }
    inputs.files(mainSources).withPropertyName("mainSources").ignoreEmptyDirectories()
    inputs.files(testSources).withPropertyName("testSources").ignoreEmptyDirectories()
    val moduleName = project.name
    doLast {
      if (!mainSources.isEmpty && testSources.isEmpty) {
        throw GradleException("Module '$moduleName' has main sources but no tests.")
      }
    }
  }

tasks.named("check") {
  dependsOn("ktfmtCheck", "detekt", "jacocoTestCoverageVerification", verifyTestSourcesPresent)
}
