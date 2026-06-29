plugins {
    `kotlin-dsl`
    `maven-publish`
}

group = "no.chirico.core"
version = "0.2.0" // x-release-please-version

java {
    sourceCompatibility = JavaVersion.VERSION_25
    targetCompatibility = JavaVersion.VERSION_25
}

dependencies {
    implementation(libs.kotlin.gradle.plugin)
    implementation(libs.kotlin.allopen)
    implementation(libs.kotlin.noarg)
    implementation(libs.spring.boot.gradle.plugin) {
        exclude(group = "io.spring.gradle", module = "dependency-management-plugin")
    }
    implementation(libs.ktfmt.gradle.plugin)
}

publishing {
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
