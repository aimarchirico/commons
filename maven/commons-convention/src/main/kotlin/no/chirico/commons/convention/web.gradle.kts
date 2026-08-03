package no.chirico.commons.convention

import org.gradle.api.artifacts.VersionCatalogsExtension
import org.springframework.boot.gradle.plugin.SpringBootPlugin

plugins { kotlin("jvm") }

val libs = extensions.getByType<VersionCatalogsExtension>().named("libs")

dependencies {
  implementation(platform(SpringBootPlugin.BOM_COORDINATES))
  implementation("org.springframework.boot:spring-boot-starter-web")
  implementation("org.springframework.boot:spring-boot-starter-actuator")
  implementation("org.springframework.boot:spring-boot-starter-validation")
  implementation(libs.findLibrary("springdoc-openapi").get())
}
