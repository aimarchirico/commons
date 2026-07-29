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

const env = resolveEnv([], ['ANDROID_KEYSTORE_BASE64']);
const file = 'credentials.json';
const resource = 'android signing key';

// A keystore already in the environment is the finished state: the value came
// from a store the build reads, and re-importing could only replace a working
// signing key with a different one.
if (env.ANDROID_KEYSTORE_BASE64) {
  report(resource, 'present', 'ANDROID_KEYSTORE_BASE64 already set');
  printSummary('import-keystore');
  process.exit(0);
}

// eas-cli exposes keystore creation and download only through an interactive
// menu, whose neighbouring entry deletes the keystore outright. Driving that
// menu unattended is not worth the failure mode, so the menu is the operator's
// to drive and the mechanical half is this command's.
if (!fs.existsSync(file)) {
  instruct(resource, `no ${file} found`, STEPS);
  printSummary('import-keystore');
  process.exit(0);
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

  // EAS remains the store of record, so the local copies are a transfer
  // artefact. Leaving them behind is how a signing key ends up committed.
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
