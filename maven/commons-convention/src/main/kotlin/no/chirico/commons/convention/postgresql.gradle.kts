package no.chirico.commons.convention

import org.gradle.api.artifacts.VersionCatalogsExtension
import org.springframework.boot.gradle.plugin.SpringBootPlugin

plugins {
  kotlin("jvm")
  kotlin("plugin.jpa")
}

configure<org.jetbrains.kotlin.allopen.gradle.AllOpenExtension> {
  annotation("jakarta.persistence.Entity")
  annotation("jakarta.persistence.MappedSuperclass")
  annotation("jakarta.persistence.Embeddable")
}

val libs = extensions.getByType<VersionCatalogsExtension>().named("libs")

dependencies {
  implementation(platform(SpringBootPlugin.BOM_COORDINATES))
  implementation("org.springframework.boot:spring-boot-starter-data-jpa")
  implementation("org.springframework.boot:spring-boot-flyway")
  implementation("org.flywaydb:flyway-core")
  implementation("org.flywaydb:flyway-database-postgresql")
  implementation(libs.findLibrary("hypersistence-utils").get())
  runtimeOnly("org.postgresql:postgresql")

  testImplementation(platform(SpringBootPlugin.BOM_COORDINATES))
  testImplementation("org.springframework.boot:spring-boot-testcontainers")
  testImplementation("org.testcontainers:testcontainers-junit-jupiter")
  testImplementation("org.testcontainers:testcontainers-postgresql")
}
