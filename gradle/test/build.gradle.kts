plugins {
  id("no.chirico.core.buildlogic.kotlin")
  `java-library`
  `maven-publish`
}

group = "no.chirico.core"

version = "0.1.0" // x-release-please-version

dependencies {
  implementation(platform(libs.spring.boot.dependencies))
  api(libs.archunit)
  api("org.junit.jupiter:junit-jupiter-api")
  runtimeOnly("org.junit.platform:junit-platform-launcher")
  runtimeOnly("org.junit.jupiter:junit-jupiter-engine")
}

publishing {
  publications {
    create<MavenPublication>("mavenJava") {
      from(components["java"])
      groupId = "no.chirico.core"
      artifactId = "core-test"
      version = project.version.toString()
    }
  }
  repositories {
    maven {
      name = "GitHubPackages"
      url = uri("https://maven.pkg.github.com/aimarchirico/core")
      credentials {
        username = System.getenv("GITHUB_ACTOR")
        password = System.getenv("GITHUB_TOKEN")
      }
    }
  }
}
