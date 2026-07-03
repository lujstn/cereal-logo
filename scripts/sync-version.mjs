// Propagates the root package.json version to every platform package.
// The root version is the single source of truth; run this (or `npm version`,
// which runs it automatically) after bumping it.
import { readFileSync, writeFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const root = dirname(dirname(fileURLToPath(import.meta.url)));
const version = JSON.parse(readFileSync(join(root, 'package.json'), 'utf8')).version;

function setJsonVersion(relPath) {
  const file = join(root, relPath);
  const next = readFileSync(file, 'utf8').replace(/("version":\s*")[^"]*(")/, `$1${version}$2`);
  writeFileSync(file, next);
}

function setGradleVersion(relPath) {
  const file = join(root, relPath);
  const next = readFileSync(file, 'utf8').replace(/^VERSION=.*$/m, `VERSION=${version}`);
  writeFileSync(file, next);
}

setJsonVersion('packages/react/package.json');
setJsonVersion('packages/react-native/package.json');
setGradleVersion('packages/android/gradle.properties');

console.log(`synced version ${version} -> react, react-native, android (SwiftUI uses the git tag)`);
