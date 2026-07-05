pluginManagement {
    includeBuild("commons-convention")
    repositories {
        mavenCentral()
        gradlePluginPortal()
    }
}

dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.FAIL_ON_PROJECT_REPOS)
    repositories {
        mavenCentral()
    }
}

rootProject.name = "commons"

include(":commons-security", ":commons-test", ":commons-firebase-admin")
