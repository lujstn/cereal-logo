import { useEffect, useMemo, useRef, useState } from 'react';
import { AccessibilityInfo, View, type ViewStyle, type StyleProp } from 'react-native';
import LottieView from 'lottie-react-native';

import flow from './assets/cereal-inflate-flow.json';
import split from './assets/cereal-inflate-split.json';
import bloom from './assets/cereal-inflate-bloom.json';

export const CEREAL_LOGO_MODES = ['flow', 'split', 'bloom'] as const;
export type CerealLogoVariant = (typeof CEREAL_LOGO_MODES)[number];
export type CerealLogoMode = CerealLogoVariant | 'random';

const SOURCES: Record<CerealLogoVariant, unknown> = { flow, split, bloom };

function pickRandom(): CerealLogoVariant {
  return CEREAL_LOGO_MODES[Math.floor(Math.random() * CEREAL_LOGO_MODES.length)];
}

function useReduceMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    let mounted = true;
    AccessibilityInfo.isReduceMotionEnabled().then((value) => {
      if (mounted) setReduced(value);
    });
    const sub = AccessibilityInfo.addEventListener('reduceMotionChanged', setReduced);
    return () => {
      mounted = false;
      sub.remove();
    };
  }, []);
  return reduced;
}

export interface CerealLogoProps {
  mode?: CerealLogoMode;
  loop?: boolean;
  autoPlay?: boolean;
  speed?: number;
  respectReducedMotion?: boolean;
  title?: string;
  style?: StyleProp<ViewStyle>;
  onAnimationFinish?: (cancelled: boolean) => void;
}

export function CerealLogo({
  mode = 'random',
  loop = false,
  autoPlay = true,
  speed = 1,
  respectReducedMotion = true,
  title = 'Cereal',
  style,
  onAnimationFinish,
}: CerealLogoProps) {
  const variant = useMemo<CerealLogoVariant>(
    () => (mode === 'random' ? pickRandom() : mode),
    [mode],
  );
  const reduced = useReduceMotion() && respectReducedMotion;
  const ref = useRef<LottieView>(null);

  useEffect(() => {
    if (reduced) ref.current?.pause();
  }, [reduced, variant]);

  // LottieView takes no accessibility props, so the label lives on a wrapper View.
  return (
    <View accessible accessibilityRole="image" accessibilityLabel={title}>
      <LottieView
        ref={ref}
        source={SOURCES[variant] as never}
        autoPlay={reduced ? false : autoPlay}
        loop={reduced ? false : loop}
        speed={speed}
        progress={reduced ? 1 : undefined}
        onAnimationFinish={onAnimationFinish}
        style={style}
      />
    </View>
  );
}

export default CerealLogo;
