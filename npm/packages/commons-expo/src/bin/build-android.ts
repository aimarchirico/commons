#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import {spawnSync} from 'child_process';

const androidDir = path.resolve('android');
if (!fs.existsSync(androidDir)) {
  console.error('No android/ directory found. Run "expo prebuild" first.');
  process.exit(1);
}

const args = ['assembleRelease'];

const keystoreBase64 = process.env.ANDROID_KEYSTORE_BASE64;
if (keystoreBase64) {
  /**
   * A keystore with a blank password, alias, or key password signs with
   * whatever gradle's -P defaults to rather than failing, producing a release
   * build that looks signed but was not signed with the intended key.
   */
  const companions = [
    'ANDROID_KEYSTORE_PASSWORD',
    'ANDROID_KEY_ALIAS',
    'ANDROID_KEY_PASSWORD',
  ] as const;
  const missing = companions.filter(name => !process.env[name]);
  if (missing.length) {
    console.error(
      `ANDROID_KEYSTORE_BASE64 is set but missing:\n${missing
        .map(name => `  - ${name}`)
        .join('\n')}`,
    );
    process.exit(1);
  }

  const keystorePath = path.join(androidDir, 'app', 'release.keystore');
  fs.writeFileSync(keystorePath, Buffer.from(keystoreBase64, 'base64'));
  console.log(`Wrote ${keystorePath}, building signed release.`);
  args.push(
    `-Pandroid.injected.signing.store.file=${keystorePath}`,
    `-Pandroid.injected.signing.store.password=${process.env.ANDROID_KEYSTORE_PASSWORD}`,
    `-Pandroid.injected.signing.key.alias=${process.env.ANDROID_KEY_ALIAS}`,
    `-Pandroid.injected.signing.key.password=${process.env.ANDROID_KEY_PASSWORD}`,
  );
} else if (process.env.ANDROID_ALLOW_UNSIGNED) {
  console.log(
    'ANDROID_KEYSTORE_BASE64 not set, building with default (debug) signing.',
  );
} else {
  /**
   * Falling through to debug signing produces an APK that looks like a release
   * build and cannot be shipped, so an unset keystore fails here rather than
   * several steps later. Provisioning that never reached "import-keystore"
   * would otherwise look complete.
   */
  console.error(
    'ANDROID_KEYSTORE_BASE64 is not set, so this release build would be signed\n' +
      'with the debug key. Run "commons-expo import-keystore" and pass the values\n' +
      'it emits, or set ANDROID_ALLOW_UNSIGNED=1 to build unsigned deliberately.',
  );
  process.exit(1);
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
