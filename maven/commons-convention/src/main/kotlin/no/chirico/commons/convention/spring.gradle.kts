package no.chirico.commons.convention

import org.springframework.boot.gradle.plugin.SpringBootPlugin

plugins {
  kotlin("jvm")
  id("org.springframework.boot")
  kotlin("plugin.spring")
}

dependencies {
  testImplementation(platform(SpringBootPlugin.BOM_COORDINATES))
  testImplementation("org.springframework.boot:spring-boot-starter-test")
}
