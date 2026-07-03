# io.github.lujstn:cereal-logo (Android / Compose)

The animated Cereal wordmark for Jetpack Compose. Each letter inflates like a balloon;
pick a take or let it choose one at random. Renders with
[lottie-compose](https://github.com/airbnb/lottie-android); the three animation takes
ship as `raw` resources.

## Install

Published to GitHub Packages. Add the repository and dependency:

```kotlin
// settings.gradle.kts
dependencyResolutionManagement {
    repositories {
        maven {
            url = uri("https://maven.pkg.github.com/lujstn/cereal-logo")
            credentials {
                username = providers.gradleProperty("gpr.user").orNull ?: System.getenv("GITHUB_ACTOR")
                password = providers.gradleProperty("gpr.token").orNull ?: System.getenv("GITHUB_TOKEN")
            }
        }
    }
}
```

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.github.lujstn:cereal-logo:1.1.0")
}
```

## Usage

```kotlin
import androidx.compose.ui.Modifier
import androidx.compose.foundation.layout.size
import androidx.compose.ui.unit.dp
import com.lujstn.cereal.logo.CerealLogo
import com.lujstn.cereal.logo.CerealLogoMode

CerealLogo(
    modifier = Modifier.size(width = 240.dp, height = 80.dp),
    mode = CerealLogoMode.RANDOM,   // or FLOW / SPLIT / BLOOM
)
```

## API

```kotlin
@Composable
fun CerealLogo(
    modifier: Modifier = Modifier,
    mode: CerealLogoMode = CerealLogoMode.RANDOM,
    loop: Boolean = false,
    speed: Float = 1f,
    respectReducedMotion: Boolean = true,   // freeze on the finished word when animator scale is 0
    haptics: Boolean = false,                // melodic vibration sequence timed to the letters
    contentDescription: String = "Cereal",  // accessibility label (TalkBack reads this)
)

// The library declares the VIBRATE permission, which merges into your app's manifest.
```

`random` is resolved once per composition, so it does not re-pick on recomposition.
