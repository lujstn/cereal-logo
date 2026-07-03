// Render smoke test for the built React package: every mode must render and
// carry the accessible name. Run after `npm run build --workspace @lujstn/cereal-logo-react`.
import { createElement } from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const { CerealLogo, CEREAL_LOGO_MODES } = await import(join(root, 'packages/react/dist/index.js'));

let failures = 0;
for (const mode of [...CEREAL_LOGO_MODES, 'random']) {
  const html = renderToStaticMarkup(createElement(CerealLogo, { mode }));
  const rendered = html.includes('<svg') || html.includes('<div');
  const labelled = html.includes('aria-label="Cereal"');
  const ok = rendered && labelled;
  console.log(`  ${mode.padEnd(7)} render=${rendered} a11y=${labelled}`);
  if (!ok) failures += 1;
}

if (failures) {
  console.error(`react smoke: ${failures} mode(s) failed`);
  process.exit(1);
}
console.log('  react render smoke passed');
