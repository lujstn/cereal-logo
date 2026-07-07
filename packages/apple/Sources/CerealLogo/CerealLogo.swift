import Lottie
import SwiftUI

#if os(iOS)
import CoreHaptics
#endif

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

/// Which ink the wordmark is drawn in, so it stays legible on either surface.
public enum CerealLogoColour: Sendable {
    /// The artwork's native charcoal, for a light surface. The default; unchanged from earlier versions.
    case dark
    /// A soft cool white, for placing the wordmark on a dark surface.
    case light
}

public struct CerealLogo: View {
    // @State so a random pick is resolved once per view identity, not on every redraw.
    @State private var variant: CerealLogoVariant
    private let colour: CerealLogoColour
    private let loop: Bool
    private let speed: CGFloat
    private let respectReducedMotion: Bool
    private let haptics: Bool
    private let title: String
    private let onFinish: ((Bool) -> Void)?

    @Environment(\.accessibilityReduceMotion) private var reduceMotion

    public init(
        _ mode: CerealLogoMode = .random,
        colour: CerealLogoColour = .dark,
        loop: Bool = false,
        speed: CGFloat = 1,
        respectReducedMotion: Bool = true,
        haptics: Bool = false,
        title: String = "Cereal",
        onFinish: ((Bool) -> Void)? = nil
    ) {
        _variant = State(initialValue: mode.resolved())
        self.colour = colour
        self.loop = loop
        self.speed = speed
        self.respectReducedMotion = respectReducedMotion
        self.haptics = haptics
        self.title = title
        self.onFinish = onFinish
    }

    private var still: Bool { respectReducedMotion && reduceMotion }

    public var body: some View {
        let base = inkedLogo(LottieAnimation.named(variant.resourceName, bundle: .module))

        return Group {
            if still {
                base
                    .currentProgress(1)
                    .resizable()
            } else {
                base
                    .animationSpeed(speed)
                    .playing(loopMode: loop ? .loop : .playOnce)
                    .animationDidFinish { completed in onFinish?(completed) }
                    .resizable()
            }
        }
        .accessibilityElement()
        .accessibilityLabel(Text(title))
        .accessibilityAddTraits(.isImage)
        .onAppear {
            #if os(iOS)
            if haptics, !still {
                CerealHaptics.shared.play(variant, speed: speed)
            }
            #endif
        }
    }

    /// The animation view with the requested ink applied. `.dark` keeps the artwork's own charcoal; `.light`
    /// overrides every letter fill via a Lottie value provider, which recolours at render time so the inflate
    /// and its haptics are untouched (a mask or SwiftUI colour filter would rasterise the animation instead).
    private func inkedLogo(_ animation: LottieAnimation?) -> LottieView<EmptyView> {
        let view = LottieView(animation: animation)
        switch colour {
        case .dark:
            return view
        case .light:
            return view.valueProvider(
                ColorValueProvider(LottieColor(r: 0.93, g: 0.94, b: 0.97, a: 1)),
                for: AnimationKeypath(keypath: "**.Color")
            )
        }
    }
}

#if os(iOS)
private struct HapticTrack: Decodable {
    struct Event: Decodable {
        let t: Double
        let intensity: Double
        let sharpness: Double
    }
    let events: [Event]
}

final class CerealHaptics {
    static let shared = CerealHaptics()

    private var engine: CHHapticEngine?
    private lazy var tracks = Self.load()

    private init() {}

    func play(_ variant: CerealLogoVariant, speed: CGFloat) {
        guard CHHapticEngine.capabilitiesForHardware().supportsHaptics,
              let track = tracks[variant.rawValue], !track.events.isEmpty else { return }
        let rate = speed > 0 ? Double(speed) : 1
        let events = track.events.map { event in
            CHHapticEvent(
                eventType: .hapticTransient,
                parameters: [
                    CHHapticEventParameter(parameterID: .hapticIntensity, value: Float(event.intensity)),
                    CHHapticEventParameter(parameterID: .hapticSharpness, value: Float(event.sharpness)),
                ],
                relativeTime: event.t / rate
            )
        }
        do {
            let engine = try runningEngine()
            let pattern = try CHHapticPattern(events: events, parameters: [])
            try engine.makePlayer(with: pattern).start(atTime: CHHapticTimeImmediate)
        } catch {
            // Haptics are non-essential; a failure should never affect the logo.
        }
    }

    private func runningEngine() throws -> CHHapticEngine {
        if let engine { return engine }
        let engine = try CHHapticEngine()
        engine.isAutoShutdownEnabled = true
        engine.resetHandler = { [weak self] in try? self?.engine?.start() }
        try engine.start()
        self.engine = engine
        return engine
    }

    private static func load() -> [String: HapticTrack] {
        guard let url = Bundle.module.url(forResource: "cereal-haptics", withExtension: "json"),
              let data = try? Data(contentsOf: url),
              let tracks = try? JSONDecoder().decode([String: HapticTrack].self, from: data)
        else { return [:] }
        return tracks
    }
}
#endif
