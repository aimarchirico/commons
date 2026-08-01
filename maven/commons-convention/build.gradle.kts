plugins {
  `kotlin-dsl`
  `maven-publish`
  jacoco
  alias(libs.plugins.ktfmt)
  alias(libs.plugins.detekt)
}

group = "no.chirico.commons"

version = "2.1.0" // x-release-please-version

java {
  sourceCompatibility = JavaVersion.VERSION_25
  targetCompatibility = JavaVersion.VERSION_25
}

dependencies {
  components {
    withModule("dev.detekt:detekt-api") {
      allVariants {
        withCapabilities { addCapability("dev.detekt", "detekt-api-test-fixtures", id.version) }
      }
    }
  }

  implementation(libs.kotlin.gradle.plugin)
  implementation(libs.kotlin.allopen)
  implementation(libs.kotlin.noarg)
  implementation(libs.spring.boot.gradle.plugin) {
    exclude(group = "io.spring.gradle", module = "dependency-management-plugin")
  }
  implementation(libs.ktfmt.gradle.plugin)
  implementation(libs.detekt.gradle.plugin)
  compileOnly(libs.detekt.api)

  testImplementation(libs.detekt.api)
  testImplementation(libs.detekt.test)
  testImplementation(libs.detekt.test.utils)
  testImplementation(libs.junit.jupiter.api)
  testImplementation(libs.assertj.core)
  testImplementation(gradleTestKit())
  testRuntimeOnly(libs.junit.platform.launcher)
  testRuntimeOnly(libs.junit.jupiter.engine)

  detektPlugins(files(sourceSets.main.get().output))
}

configure<com.ncorti.ktfmt.gradle.KtfmtExtension> { googleStyle() }

configure<dev.detekt.gradle.extensions.DetektExtension> {
  buildUponDefaultConfig.set(true)
  config.setFrom(file("src/main/resources/detekt.yaml"))
  source.from(file("build.gradle.kts"))
}

tasks.withType<Test>().configureEach {
  useJUnitPlatform()
  finalizedBy(tasks.named("jacocoTestReport"))
}

tasks.named<JacocoReport>("jacocoTestReport") { dependsOn(tasks.named("test")) }

tasks.named<JacocoCoverageVerification>("jacocoTestCoverageVerification") {
  dependsOn(tasks.named("jacocoTestReport"))
  violationRules {
    rule {
      limit {
        counter = "LINE"
        value = "COVEREDRATIO"
        minimum = "0.80".toBigDecimal()
      }
    }
  }
}

tasks.named("check") { dependsOn("ktfmtCheck", "detekt", "jacocoTestCoverageVerification") }

publishing {
  repositories {
    maven {
      name = "GitHubPackages"
      url = uri("https://maven.pkg.github.com/aimarchirico/commons")
      credentials {
        username = System.getenv("GITHUB_ACTOR") ?: providers.gradleProperty("gpr.user").orNull
        password = System.getenv("GITHUB_TOKEN") ?: providers.gradleProperty("gpr.key").orNull
      }
    }
  }
}
