package no.chirico.core.buildlogic

import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    kotlin("jvm")
    id("com.ncorti.ktfmt.gradle")
}

configure<com.ncorti.ktfmt.gradle.KtfmtExtension> {
    googleStyle()
}

configure<org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension> {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_25)
        freeCompilerArgs.addAll("-Xjsr305=strict")
    }
}

configure<org.gradle.api.plugins.JavaPluginExtension> {
    toolchain {
        languageVersion.set(JavaLanguageVersion.of(25))
    }
}

tasks.withType<Test>().configureEach {
    useJUnitPlatform()
}

tasks.named("check") {
    dependsOn("ktfmtCheck")
}
