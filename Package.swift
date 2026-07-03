// swift-tools-version: 5.9
import PackageDescription

// Swift Package Manager resolves a package from the repository root, so the
// manifest lives here and points at the Apple package sources under packages/apple.
let package = Package(
    name: "CerealLogo",
    platforms: [
        .iOS(.v14),
        .tvOS(.v14),
        .macOS(.v12),
    ],
    products: [
        .library(name: "CerealLogo", targets: ["CerealLogo"]),
    ],
    dependencies: [
        .package(url: "https://github.com/airbnb/lottie-ios.git", from: "4.6.0"),
    ],
    targets: [
        .target(
            name: "CerealLogo",
            dependencies: [
                .product(name: "Lottie", package: "lottie-ios"),
            ],
            path: "packages/apple/Sources/CerealLogo",
            resources: [.process("Resources")]
        ),
    ]
)
