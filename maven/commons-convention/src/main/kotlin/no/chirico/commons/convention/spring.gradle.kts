package no.chirico.commons.convention

import org.springframework.boot.gradle.plugin.SpringBootPlugin

plugins {
  id("org.springframework.boot")
  kotlin("plugin.spring")
  kotlin("plugin.jpa")
}

configure<org.jetbrains.kotlin.allopen.gradle.AllOpenExtension> {
  annotation("jakarta.persistence.Entity")
  annotation("jakarta.persistence.MappedSuperclass")
  annotation("jakarta.persistence.Embeddable")
}

dependencies {
  testImplementation(platform(SpringBootPlugin.BOM_COORDINATES))
  testImplementation("org.springframework.boot:spring-boot-starter-test")
}
