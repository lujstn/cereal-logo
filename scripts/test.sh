#!/usr/bin/env bash
# Full verification suite. Run directly (`npm test`) or via the pre-push git hook.
# Set SKIP_ANDROID=1 to skip the slower Android build.
set -euo pipefail
cd "$(dirname "$0")/.."

echo "==> Regenerating assets and checking for drift"
gen_hash() {
  find assets \
    packages/react/src/assets \
    packages/react-native/src/assets \
    packages/apple/Sources/CerealLogo/Resources \
    packages/android/src/main/res/raw \
    -name '*.json' -type f 2>/dev/null | sort | xargs shasum | shasum
}
before="$(gen_hash)"
python3 generator/generate_lottie.py >/dev/null
if [ "$before" != "$(gen_hash)" ]; then
  echo "ERROR: committed assets were stale; regeneration changed them. Commit the update." >&2
  exit 1
fi

echo "==> React: build + render smoke test"
npm run build --workspace @lujstn/cereal-logo-react >/dev/null
node scripts/smoke-react.mjs

echo "==> React Native: typecheck"
npm run typecheck --workspace @lujstn/cereal-logo-react-native >/dev/null

echo "==> SwiftUI: build for iOS"
# Build for the real iOS target, not the host: the macOS slice skips the
# CoreHaptics code and misses iOS-only availability errors.
xcodebuild -scheme CerealLogo -destination 'generic/platform=iOS' \
  -skipPackagePluginValidation build -quiet

if [ "${SKIP_ANDROID:-0}" != "1" ]; then
  echo "==> Android: assembleRelease"
  export JAVA_HOME="${JAVA_HOME:-$(/usr/libexec/java_home -v 17 2>/dev/null || true)}"
  ( cd packages/android && ./gradlew assembleRelease -q --console=plain )
fi

echo "All checks passed."
