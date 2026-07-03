plugins {
    id("com.android.library")
    id("org.jetbrains.kotlin.android")
    id("org.jetbrains.kotlin.plugin.compose")
    id("maven-publish")
}

group = "io.github.lujstn"
version = providers.gradleProperty("VERSION").get()

android {
    namespace = "com.lujstn.cereal.logo"
    compileSdk = 35

    defaultConfig {
        minSdk = 21
    }

    buildFeatures {
        compose = true
    }

    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_17
        targetCompatibility = JavaVersion.VERSION_17
    }

    kotlinOptions {
        jvmTarget = "17"
    }

    publishing {
        singleVariant("release") {
            withSourcesJar()
        }
    }
}

dependencies {
    implementation(platform("androidx.compose:compose-bom:2024.09.00"))
    implementation("androidx.compose.foundation:foundation")
    implementation("com.airbnb.android:lottie-compose:6.5.2")
}

afterEvaluate {
    publishing {
        publications {
            create<MavenPublication>("release") {
                from(components["release"])
                groupId = "io.github.lujstn"
                artifactId = "cereal-logo"
                version = providers.gradleProperty("VERSION").get()
            }
        }
        repositories {
            maven {
                name = "GitHubPackages"
                url = uri(
                    "https://maven.pkg.github.com/" +
                        (System.getenv("GITHUB_REPOSITORY") ?: "lujstn/cereal-logo"),
                )
                credentials {
                    username = System.getenv("GITHUB_ACTOR")
                        ?: providers.gradleProperty("gpr.user").orNull
                    password = System.getenv("GITHUB_TOKEN")
                        ?: providers.gradleProperty("gpr.token").orNull
                }
            }
        }
    }
}
