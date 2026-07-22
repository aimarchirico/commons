package no.chirico.commons.convention

import org.gradle.api.artifacts.VersionCatalogsExtension

plugins {
    id("org.jetbrains.kotlin.jvm")
    id("org.jetbrains.kotlin.kapt")
}

val libs = extensions.getByType<VersionCatalogsExtension>().named("libs")

dependencies {
    implementation(libs.findLibrary("mapstruct").get())
    kapt(libs.findLibrary("mapstruct-processor").get())
}

configure<org.jetbrains.kotlin.gradle.plugin.KaptExtension> {
    arguments {
        arg("mapstruct.defaultComponentModel", "spring")
        arg("mapstruct.unmappedTargetPolicy", "ERROR")
    }
}
