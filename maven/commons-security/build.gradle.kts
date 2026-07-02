plugins {
  id("no.chirico.commons.convention.kotlin")
  `maven-publish`
}

group = "no.chirico.commons"

version = "1.1.0" // x-release-please-version

dependencies {
  implementation(platform(libs.spring.boot.dependencies))
  implementation("org.springframework.boot:spring-boot-starter-web")
  testImplementation(project(":commons-test"))
}

publishing {
  publications {
    create<MavenPublication>("mavenJava") {
      from(components["java"])
      groupId = "no.chirico.commons"
      artifactId = "commons-security"
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
