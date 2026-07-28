package no.chirico.commons.convention

import org.jetbrains.kotlin.gradle.dsl.JvmTarget

plugins {
    kotlin("jvm")
    id("com.ncorti.ktfmt.gradle")
    id("dev.detekt")
}

configure<com.ncorti.ktfmt.gradle.KtfmtExtension> {
    googleStyle()
}

/**
 * Unpack the documentation rules bundled in this plugin so consuming builds
 * inherit them without declaring a detekt configuration of their own. The
 * anonymous object resolves the resource against this plugin's own jar.
 */
val bundledDetektConfig =
    checkNotNull(object {}.javaClass.getResource("/detekt.yaml")) {
        "commons-convention is missing its bundled detekt.yaml"
    }

val detektConfigFile = layout.buildDirectory.file("detekt/commons-detekt.yaml").get().asFile

detektConfigFile.parentFile.mkdirs()
detektConfigFile.writeText(bundledDetektConfig.readText())

configure<dev.detekt.gradle.extensions.DetektExtension> {
    buildUponDefaultConfig.set(true)
    config.setFrom(detektConfigFile)
}

configure<org.jetbrains.kotlin.gradle.dsl.KotlinJvmProjectExtension> {
    compilerOptions {
        jvmTarget.set(JvmTarget.JVM_25)
        freeCompilerArgs.addAll("-Xjsr305=strict", "-java-parameters")
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
    dependsOn("ktfmtCheck", "detekt")
}
