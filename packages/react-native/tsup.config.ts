import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.tsx'],
  format: ['esm', 'cjs'],
  outExtension: ({ format }) => ({ js: format === 'cjs' ? '.cjs' : '.js' }),
  dts: true,
  clean: true,
  sourcemap: true,
  // The three Lottie JSON takes are inlined so the package is self-contained.
  loader: { '.json': 'json' },
  external: ['react', 'react-native', 'lottie-react-native'],
});
