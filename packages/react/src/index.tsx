import {
  useEffect,
  useMemo,
  useRef,
  useState,
  type CSSProperties,
} from 'react';
import LottieImport, { type LottieRefCurrentProps } from 'lottie-react';

import flow from './assets/cereal-inflate-flow.json';
import split from './assets/cereal-inflate-split.json';
import bloom from './assets/cereal-inflate-bloom.json';

// Some CJS/ESM setups deliver the module namespace instead of the default export;
// fall back to it so the component renders under bundlers and server rendering alike.
const Lottie = (LottieImport as unknown as { default?: typeof LottieImport }).default ?? LottieImport;

export const CEREAL_LOGO_MODES = ['flow', 'split', 'bloom'] as const;
export type CerealLogoVariant = (typeof CEREAL_LOGO_MODES)[number];
export type CerealLogoMode = CerealLogoVariant | 'random';

const SOURCES: Record<CerealLogoVariant, unknown> = { flow, split, bloom };

function pickRandom(): CerealLogoVariant {
  return CEREAL_LOGO_MODES[Math.floor(Math.random() * CEREAL_LOGO_MODES.length)];
}

function usePrefersReducedMotion(): boolean {
  const [reduced, setReduced] = useState(false);
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const query = window.matchMedia('(prefers-reduced-motion: reduce)');
    setReduced(query.matches);
    const onChange = (event: MediaQueryListEvent) => setReduced(event.matches);
    query.addEventListener?.('change', onChange);
    return () => query.removeEventListener?.('change', onChange);
  }, []);
  return reduced;
}

export interface CerealLogoProps {
  mode?: CerealLogoMode;
  loop?: boolean;
  autoplay?: boolean;
  speed?: number;
  respectReducedMotion?: boolean;
  title?: string;
  className?: string;
  style?: CSSProperties;
  onComplete?: () => void;
}

export function CerealLogo({
  mode = 'random',
  loop = false,
  autoplay = true,
  speed = 1,
  respectReducedMotion = true,
  title = 'Cereal',
  className,
  style,
  onComplete,
}: CerealLogoProps) {
  const variant = useMemo<CerealLogoVariant>(
    () => (mode === 'random' ? pickRandom() : mode),
    [mode],
  );
  const reduced = usePrefersReducedMotion() && respectReducedMotion;
  const ref = useRef<LottieRefCurrentProps>(null);

  const apply = () => {
    const item = ref.current;
    if (!item) return;
    item.setSpeed(speed);
    if (reduced) {
      const frames = item.getDuration(true) ?? 0;
      item.goToAndStop(Math.max(frames - 1, 0), true);
    }
  };

  useEffect(apply, [reduced, speed, variant]);

  return (
    <Lottie
      lottieRef={ref}
      animationData={SOURCES[variant]}
      loop={reduced ? false : loop}
      autoplay={reduced ? false : autoplay}
      onDOMLoaded={apply}
      onComplete={onComplete}
      role="img"
      aria-label={title}
      className={className}
      style={style}
    />
  );
}

export default CerealLogo;
