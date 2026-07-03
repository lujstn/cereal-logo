# CerealLogo (SwiftUI)

The animated Cereal wordmark for SwiftUI (iOS, macOS, tvOS). Each letter inflates like
a balloon; pick a take or let it choose one at random. Renders with
[lottie-ios](https://github.com/airbnb/lottie-ios); the three animation takes ship as
bundle resources.

> The `Package.swift` lives at the repository root, because Swift Package Manager
> resolves a package from the repo root. These are the package's sources.

## Install

Xcode > File > Add Package Dependencies, or in `Package.swift`:

```swift
.package(url: "https://github.com/lujstn/cereal-logo.git", from: "1.0.0")
```

Then add `CerealLogo` to your target.

## Usage

```swift
import CerealLogo
import SwiftUI

struct Header: View {
    var body: some View {
        CerealLogo(.random)          // or .flow / .split / .bloom
            .frame(width: 240)       // the view is resizable
    }
}
```

## API

```swift
CerealLogo(
    _ mode: CerealLogoMode = .random,   // .flow, .split, .bloom, .random
    loop: Bool = false,
    speed: CGFloat = 1,
    respectReducedMotion: Bool = true,  // show the finished word, unanimated, under Reduce Motion
    haptics: Bool = false,               // melodic Core Haptics tap sequence timed to the letters
    title: String = "Cereal",           // accessibility label (VoiceOver reads this)
    onFinish: ((Bool) -> Void)? = nil   // called when a non-looping play ends
)
```

`random` is resolved once per view identity, so it does not re-pick on every redraw.
