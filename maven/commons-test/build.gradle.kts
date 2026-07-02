plugins {
  id("no.chirico.commons.convention.kotlin")
  `java-library`
  `maven-publish`
}

group = "no.chirico.commons"

version = "1.1.2" // x-release-please-version

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
      groupId = "no.chirico.commons"
      artifactId = "commons-test"
      version = project.version.toString()
    }
  }
  repositories {
    maven {
      name = "GitHubPackages"
      url = uri("https://maven.pkg.github.com/aimarchirico/commons")
      credentials {
        username = System.getenv("GITHUB_ACTOR")
        password = System.getenv("GITHUB_TOKEN")
      }
    }
  }
}
