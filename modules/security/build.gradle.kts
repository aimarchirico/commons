plugins {
  id("no.chirico.core.buildlogic.kotlin")
  `maven-publish`
}

group = "no.chirico.core"

version = "0.0.1"

dependencies {
  implementation(platform(libs.spring.boot.dependencies))
  implementation("org.springframework.boot:spring-boot-starter-web")
}

publishing {
  publications {
    create<MavenPublication>("mavenJava") {
      from(components["java"])
      groupId = "no.chirico.core"
      artifactId = "core-security"
      version = "0.0.1"
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
