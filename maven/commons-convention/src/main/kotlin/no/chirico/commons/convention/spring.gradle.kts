package no.chirico.commons.convention

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
