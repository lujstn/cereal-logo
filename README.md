# Cereal logo

The animated Cereal wordmark, as a cross-platform component. Each letter inflates
like a balloon; the caller chooses which of three takes plays, or asks for a random one.

| mode | motion |
| --- | --- |
| `flow` | letters pop left to right in a tight, rolling wave |
| `split` | `c` leads, then `a` and `e` burst in together, and `r e l` complete the word |
| `bloom` | ignites in the centre and blooms outward to both ends |
| `random` | picks one of the three per mount |

One animation, authored once, rendered natively on every platform by [Lottie](https://airbnb.io/lottie/).
Each platform package embeds the three `.json` takes and renders them with its own native
Lottie player, so there is no webview and no runtime asset fetching.

## Packages

| Platform | Package | Registry |
| --- | --- | --- |
| Web (React) | `@lujstn/cereal-logo-react` | npm |
| React Native | `@lujstn/cereal-logo-react-native` | npm |
| iOS / macOS / tvOS (SwiftUI) | `CerealLogo` | Swift Package Manager |
| Android (Compose) | `io.github.lujstn:cereal-logo` | Maven (GitHub Packages) |

Every package exposes the same idea: a `CerealLogo` component with a `mode` of
`flow`, `split`, `bloom` or `random`, plus `loop`, `speed`, and reduced-motion handling.

### React

```bash
npm install @lujstn/cereal-logo-react
```

```tsx
import { CerealLogo } from '@lujstn/cereal-logo-react';

export function Header() {
  return <CerealLogo mode="random" style={{ width: 240 }} />;
}
```

### React Native

```bash
npm install @lujstn/cereal-logo-react-native lottie-react-native
```

```tsx
import { CerealLogo } from '@lujstn/cereal-logo-react-native';

export function Header() {
  return <CerealLogo mode="split" style={{ width: 240, height: 80 }} />;
}
```

### SwiftUI

Add the package in Xcode (File > Add Package Dependencies) or in `Package.swift`:

```swift
.package(url: "https://github.com/lujstn/cereal-logo.git", from: "1.0.0")
```

```swift
import CerealLogo
import SwiftUI

struct Header: View {
    var body: some View {
        CerealLogo(.random)
            .frame(width: 240)
    }
}
```

Pass `colour: .light` to ink the wordmark for a dark surface (the default is `.dark`, the native charcoal):

```swift
CerealLogo(.split, colour: .light)
    .frame(width: 240)
```

### Android (Compose)

```kotlin
// build.gradle.kts
dependencies {
    implementation("io.github.lujstn:cereal-logo:1.1.1")
}
```

```kotlin
import androidx.compose.ui.unit.dp
import com.lujstn.cereal.logo.CerealLogo
import com.lujstn.cereal.logo.CerealLogoMode

CerealLogo(
    modifier = Modifier.size(width = 240.dp, height = 80.dp),
    mode = CerealLogoMode.BLOOM,
)
```

## Shared API

Every platform accepts the same options (names follow each platform's convention):

- **mode**: `flow` | `split` | `bloom` | `random`. Defaults to `random`, resolved once per mount so it does not re-pick on redraw.
- **colour** (Apple only for now): `dark` (default) | `light`. The ink the wordmark is drawn in — its native charcoal for a light surface, or a soft cool white for a dark one, recoloured at render time so the animation is untouched.
- **loop**: repeat, or play once (the default).
- **speed**: playback multiplier, default `1`.
- **haptics**: a short melodic tap sequence timed to the letters, off by default. Opt in with `haptics = true`.
- **reduced motion**: on by default, so when the OS requests reduced motion the component shows the finished word without animating (and stays silent). Opt out with `respectReducedMotion = false`.

## Haptics

Each mode plays a little rhythm as its letters pop, timed from the same source as the
animation so the taps stay in sync. `flow` rolls up a scale, `split` accents the
`a`+`e` chord, `bloom` is three rising chords. Fidelity follows the platform: iOS uses
Core Haptics with per-tap intensity and sharpness; Android uses the vibrator (the
library adds the `VIBRATE` permission); web and React Native fall back to the coarser
Vibration API and no-op where it is unsupported (for example iOS Safari). Haptics are off
by default; when enabled they fire once as the animation starts, never on loop repeats,
and are suppressed under reduced motion.

## Repository layout

```
generator/          Python source of truth: parses cereal.svg, builds every take,
                    writes the manifest and the local preview, and syncs the three
                    published takes into every package.
assets/             The generated .json takes plus manifest.json.
packages/react/     @lujstn/cereal-logo-react
packages/react-native/  @lujstn/cereal-logo-react-native
packages/apple/     CerealLogo sources (Package.swift lives at the repo root, as SPM requires)
packages/android/   io.github.lujstn:cereal-logo
```

## Changing the animation

The Python generator is the only place motion is authored. Nobody edits JSON by hand.

```bash
python3 generator/generate_lottie.py
```

That rebuilds `assets/`, refreshes `generator/preview.html` (a local-only page, git-ignored,
to compare every take with a scrubbable timeline), and copies the three published takes into
all four packages. Tweak `VARIANTS`, `INFLATE_ANCHORS` or `INFLATE_BOUNCE` at the top of the
script and re-run.

To add a fourth mode, add it to `VARIANTS`, list it in `PUBLISHED_MODES`, and add the
matching enum case in each package (four small edits, one per platform).

## Testing

Instead of CI, a git `pre-push` hook runs the full suite before anything leaves your
machine: it regenerates the assets and fails on drift, builds and render-tests the React
package, type-checks React Native, and builds the SwiftUI and Android packages. Enable it
once per clone:

```bash
git config core.hooksPath .githooks
```

Run it any time with `npm test`. Set `SKIP_ANDROID=1` to skip the (slower) Android build.

## Versioning and releasing

The root `package.json` version is the single source of truth. Bumping it propagates
everywhere automatically:

```bash
npm version patch     # or minor / major
```

That runs `scripts/sync-version.mjs` (updating both npm packages and the Android
`gradle.properties`), regenerates the manifest, and creates the commit and `v*` tag.
Then publish:

```bash
git push --follow-tags                                   # SwiftPM consumes the tag directly
npm publish --workspace @lujstn/cereal-logo-react
npm publish --workspace @lujstn/cereal-logo-react-native
( cd packages/android && ./gradlew publish )             # GitHub Packages
```

## Licence

Proprietary. The Cereal logo and its animations are the intellectual property of the
owner and are not licensed for reuse, redistribution, or modification. The packages are
published publicly for installation convenience only. All rights reserved.
