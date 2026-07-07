#!/usr/bin/env node
'use strict';

const fs = require('fs');
const path = require('path');
const {spawnSync} = require('child_process');

const androidDir = path.resolve('android');
if (!fs.existsSync(androidDir)) {
  console.error('No android/ directory found. Run "expo prebuild" first.');
  process.exit(1);
}

const args = ['assembleRelease'];

const keystoreBase64 = process.env.ANDROID_KEYSTORE_BASE64;
if (keystoreBase64) {
  const keystorePath = path.join(androidDir, 'app', 'release.keystore');
  fs.writeFileSync(keystorePath, Buffer.from(keystoreBase64, 'base64'));
  console.log(`Wrote ${keystorePath}, building signed release.`);
  args.push(
    `-Pandroid.injected.signing.store.file=${keystorePath}`,
    `-Pandroid.injected.signing.store.password=${process.env.ANDROID_KEYSTORE_PASSWORD || ''}`,
    `-Pandroid.injected.signing.key.alias=${process.env.ANDROID_KEY_ALIAS || ''}`,
    `-Pandroid.injected.signing.key.password=${process.env.ANDROID_KEY_PASSWORD || ''}`,
  );
} else {
  console.log(
    'ANDROID_KEYSTORE_BASE64 not set, building with default (debug) signing.',
  );
}

const result = spawnSync('bash', ['gradlew', ...args], {
  cwd: androidDir,
  stdio: 'inherit',
});

if (result.error) {
  console.error(result.error.message);
  process.exit(1);
}
process.exit(result.status ?? 1);
