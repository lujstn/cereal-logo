# @lujstn/cereal-logo-react

The animated Cereal wordmark for React. Each letter inflates like a balloon; pick a
take or let it choose one at random. Renders with [lottie-react](https://www.npmjs.com/package/lottie-react);
the three animation takes are bundled in, so there is nothing to fetch at runtime.

```bash
npm install @lujstn/cereal-logo-react
```

`react` (and `react-dom`) are peer dependencies.

## Usage

```tsx
import { CerealLogo } from '@lujstn/cereal-logo-react';

export function Header() {
  return <CerealLogo mode="random" style={{ width: 240 }} />;
}
```

## Props

| prop | type | default | notes |
| --- | --- | --- | --- |
| `mode` | `'flow' \| 'split' \| 'bloom' \| 'random'` | `'random'` | `random` is resolved once per mount |
| `loop` | `boolean` | `false` | play once by default |
| `autoplay` | `boolean` | `true` | |
| `speed` | `number` | `1` | playback multiplier |
| `respectReducedMotion` | `boolean` | `true` | show the finished word, unanimated, when the OS asks for reduced motion |
| `haptics` | `boolean` | `false` | melodic tap sequence via the Web Vibration API (no-op where unsupported, e.g. iOS Safari) |
| `title` | `string` | `'Cereal'` | accessible name (`role="img"` + `aria-label`) |
| `className` | `string` | | |
| `style` | `CSSProperties` | | size the logo here |
| `onComplete` | `() => void` | | fires when a non-looping play ends |

`CEREAL_LOGO_MODES` is exported if you want to build your own picker.
