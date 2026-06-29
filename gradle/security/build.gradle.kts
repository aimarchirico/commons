plugins {
  id("no.chirico.core.buildlogic.kotlin")
  `maven-publish`
}

group = "no.chirico.core"

version = "0.2.0" // x-release-please-version

dependencies {
  implementation(platform(libs.spring.boot.dependencies))
  implementation("org.springframework.boot:spring-boot-starter-web")
  testImplementation(project(":test"))
}

publishing {
  publications {
    create<MavenPublication>("mavenJava") {
      from(components["java"])
      groupId = "no.chirico.core"
      artifactId = "core-security"
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
