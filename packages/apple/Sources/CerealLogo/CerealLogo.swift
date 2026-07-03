import Lottie
import SwiftUI

public enum CerealLogoVariant: String, CaseIterable, Sendable {
    case flow
    case split
    case bloom

    var resourceName: String { "cereal-inflate-\(rawValue)" }
}

public enum CerealLogoMode: Sendable {
    case flow
    case split
    case bloom
    case random

    func resolved() -> CerealLogoVariant {
        switch self {
        case .flow: return .flow
        case .split: return .split
        case .bloom: return .bloom
        case .random: return CerealLogoVariant.allCases.randomElement() ?? .flow
        }
    }
}

public struct CerealLogo: View {
    // @State so a random pick is resolved once per view identity, not on every redraw.
    @State private var variant: CerealLogoVariant
    private let loop: Bool
    private let speed: CGFloat
    private let respectReducedMotion: Bool
    private let title: String
    private let onFinish: ((Bool) -> Void)?

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(
        _ mode: CerealLogoMode = .random,
        loop: Bool = false,
        speed: CGFloat = 1,
        respectReducedMotion: Bool = true,
        title: String = "Cereal",
        onFinish: ((Bool) -> Void)? = nil
    ) {
        _variant = State(initialValue: mode.resolved())
        self.loop = loop
        self.speed = speed
        self.respectReducedMotion = respectReducedMotion
        self.title = title
        self.onFinish = onFinish
    }

    public var body: some View {
        let animation = LottieAnimation.named(variant.resourceName, bundle: .module)

        return Group {
            if respectReducedMotion, reduceMotion {
                LottieView(animation: animation)
                    .currentProgress(1)
                    .resizable()
            } else {
                LottieView(animation: animation)
                    .animationSpeed(speed)
                    .playing(loopMode: loop ? .loop : .playOnce)
                    .animationDidFinish { completed in onFinish?(completed) }
                    .resizable()
            }
        }
        .accessibilityElement()
        .accessibilityLabel(Text(title))
        .accessibilityAddTraits(.isImage)
    }
}
