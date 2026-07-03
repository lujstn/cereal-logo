# @lujstn/cereal-logo-react-native

The animated Cereal wordmark for React Native. Each letter inflates like a balloon;
pick a take or let it choose one at random. Renders with
[lottie-react-native](https://www.npmjs.com/package/lottie-react-native); the three
animation takes are bundled in.

```bash
npm install @lujstn/cereal-logo-react-native lottie-react-native
cd ios && pod install   # lottie-react-native has a native module
```

`react`, `react-native` and `lottie-react-native` are peer dependencies.

## Usage

```tsx
import { CerealLogo } from '@lujstn/cereal-logo-react-native';

export function Header() {
  return <CerealLogo mode="split" style={{ width: 240, height: 80 }} />;
}
```

## Props

| prop | type | default | notes |
| --- | --- | --- | --- |
| `mode` | `'flow' \| 'split' \| 'bloom' \| 'random'` | `'random'` | `random` is resolved once per mount |
| `loop` | `boolean` | `false` | play once by default |
| `autoPlay` | `boolean` | `true` | |
| `speed` | `number` | `1` | playback multiplier |
| `respectReducedMotion` | `boolean` | `true` | freeze on the finished word when the OS asks for reduced motion |
| `haptics` | `boolean` | `false` | melodic tap sequence via the built-in `Vibration` API (timing honoured on Android; fixed pulses on iOS) |
| `title` | `string` | `'Cereal'` | accessible name (wrapper `accessibilityRole="image"` + `accessibilityLabel`) |
| `style` | `StyleProp<ViewStyle>` | | size the logo here |
| `onAnimationFinish` | `(cancelled: boolean) => void` | | fires when a non-looping play ends |
