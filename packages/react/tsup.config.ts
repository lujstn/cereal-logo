import { defineConfig } from 'tsup';

export default defineConfig({
  entry: ['src/index.tsx'],
  format: ['esm', 'cjs'],
  outExtension: ({ format }) => ({ js: format === 'cjs' ? '.cjs' : '.js' }),
  dts: true,
  clean: true,
  sourcemap: true,
  treeshake: true,
  // The three Lottie JSON takes are inlined into the bundle, so the package is
  // self-contained with no runtime asset fetching.
  loader: { '.json': 'json' },
  external: ['react', 'react-dom', 'lottie-react'],
});
