plugins {
  id("no.chirico.commons.convention.kotlin")
  `java-library`
  `maven-publish`
}

group = "no.chirico.commons"

version = "1.0.3" // x-release-please-version

dependencies {
  implementation(platform(libs.spring.boot.dependencies))
  api("org.springframework.boot:spring-boot-starter-security")
  implementation("org.springframework.boot:spring-boot-starter-web")
  implementation(libs.firebase.admin)
  testImplementation(project(":commons-test"))
}

publishing {
  publications {
    create<MavenPublication>("mavenJava") {
      from(components["java"])
      groupId = "no.chirico.commons"
      artifactId = "commons-firebase-admin"
      version = project.version.toString()
    }
  }
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
