#!/usr/bin/env node

import fs from 'fs';
import path from 'path';
import {
  fail,
  instruct,
  printSummary,
  report,
  resolveEnv,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {pathToFileURL} from 'url';

type CredentialsJson = {
  android?: {
    keystore?: {
      keystorePath?: string;
      keystorePassword?: string;
      keyAlias?: string;
      keyPassword?: string;
    };
  };
};

const STEPS = [
  'pnpm exec eas credentials --platform android',
  '  → "Keystore: Manage everything needed to build your project"',
  '      → "Set up a new keystore"          (skip if one already exists)',
  '  → "credentials.json: Upload/Download credentials between EAS servers and your local json"',
  '      → "Download credentials from EAS to credentials.json"',
  'then re-run this command to import and shred the downloaded files.',
];

/**
 * Import an Android keystore downloaded via `eas credentials` into
 * environment outputs, then shred the local copies.
 */
export function importKeystore(): void {
  const env = resolveEnv([], ['ANDROID_KEYSTORE_BASE64']);
  const file = 'credentials.json';
  const resource = 'android signing key';

  if (env.ANDROID_KEYSTORE_BASE64) {
    report(resource, 'present', 'ANDROID_KEYSTORE_BASE64 already set');
    printSummary('import-keystore');
    return;
  }

  if (!fs.existsSync(file)) {
    instruct(resource, `no ${file} found`, STEPS);
    printSummary('import-keystore');
    return;
  }

  try {
    const parsed = JSON.parse(fs.readFileSync(file, 'utf8')) as CredentialsJson;
    const keystore = parsed.android?.keystore;
    const keystorePath = keystore?.keystorePath;

    if (!keystore || !keystorePath) {
      fail(
        `${file} has no "android.keystore" entry. Download it again:\n  ${STEPS.join('\n  ')}`,
      );
    }
    if (!fs.existsSync(keystorePath)) {
      fail(`${file} points at ${keystorePath}, which does not exist.`);
    }
    if (!keystore.keystorePassword || !keystore.keyAlias) {
      fail(`${file} is missing the keystore password or key alias.`);
    }

    writeOutputs({
      ANDROID_KEYSTORE_BASE64: fs.readFileSync(keystorePath).toString('base64'),
      ANDROID_KEYSTORE_PASSWORD: keystore.keystorePassword,
      ANDROID_KEY_ALIAS: keystore.keyAlias,
      ANDROID_KEY_PASSWORD: keystore.keyPassword ?? keystore.keystorePassword,
    });
    report(resource, 'written', `imported from ${file}`);

    fs.rmSync(keystorePath, {force: true});
    fs.rmSync(file, {force: true});
    const parent = path.dirname(keystorePath);
    if (fs.existsSync(parent) && !fs.readdirSync(parent).length) {
      fs.rmdirSync(parent);
    }
    console.log(`  removed ${file} and ${keystorePath}`);
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  printSummary('import-keystore');
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  importKeystore();
}
