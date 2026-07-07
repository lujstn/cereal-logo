# Changelog

All notable changes to this project are documented here. Versions follow
[semantic versioning](https://semver.org/), and the root `package.json` version is the
single source of truth that propagates to every platform package.

## [1.2.0] - 2026-07-07

### Added

- A `colour` option on the Apple/SwiftUI component: `.dark` (the default, the artwork's native
  charcoal, unchanged from earlier versions) or `.light` (a soft cool white for placing the wordmark
  on a dark surface). The light ink is applied through a Lottie colour value provider, so it recolours
  at render time and the inflate animation and its melodic haptics run untouched. The other platforms
  keep their existing behaviour for now.

## [1.1.1] - 2026-07-03

### Changed

- Trimmed the dead hold at the end of every inflate take so each composition now ends
  just after the wordmark finishes forming, four frames of settle after the final
  letter lands. Consumers reveal on the animation's finish callback, so the previous
  long tail added roughly 0.8 seconds of dead pause on launch. Out points are now
  `flow` 73, `split` 72, `bloom` 60 (and `classic` 83) frames rather than the fixed
  long durations. The generator derives each out point from the last keyframe instead
  of a per-take `hold`, so the pacing stays correct if the beats ever change.

## [1.1.0] - 2026-07-03

### Added

- Opt-in haptics that tap once per letter pop, with letters that fire together merged
  into a single stronger tap.

### Changed

- Built against the latest React, React Native, iOS and Android runtimes.

## [1.0.0] - 2026-07-03

### Added

- Initial release of the animated Cereal balloon-inflate logo as a cross-platform
  component, generated from a single source of truth and shipped to React, React
  Native, SwiftUI and Android Compose.

[1.1.1]: https://github.com/lujstn/cereal-logo/compare/v1.1.0...v1.1.1
[1.1.0]: https://github.com/lujstn/cereal-logo/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/lujstn/cereal-logo/releases/tag/v1.0.0
