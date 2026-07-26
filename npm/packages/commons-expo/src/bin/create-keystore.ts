#!/usr/bin/env node

import fs from 'fs';
import {resolveEnv} from '@aimarchirico/commons-project/env';
import {writeOutputs} from '@aimarchirico/commons-project/outputs';
import {fail, printSummary, report} from '@aimarchirico/commons-project/report';
import {
  generate,
  linkEasProject,
  password,
  verify,
} from '../services/keystore.js';

const env = resolveEnv(
  ['EXPO_TOKEN', 'EAS_PROJECT_ID'],
  [
    'ANDROID_KEYSTORE_FILE',
    'ANDROID_KEY_ALIAS',
    'ANDROID_KEYSTORE_PASSWORD',
    'ANDROID_KEY_PASSWORD',
    'ANDROID_KEY_DNAME',
  ],
);

const file = env.ANDROID_KEYSTORE_FILE ?? 'release.keystore';
const alias = env.ANDROID_KEY_ALIAS ?? 'release';

try {
  linkEasProject(env.EAS_PROJECT_ID);
  report(`eas project ${env.EAS_PROJECT_ID}`, 'present', 'linked to the app');

  let storePassword = env.ANDROID_KEYSTORE_PASSWORD;
  let keyPassword = env.ANDROID_KEY_PASSWORD;

  if (fs.existsSync(file)) {
    // Replacing signing keys breaks updates for every installed copy of the
    // app, so an existing keystore is only ever read back.
    if (!storePassword || !keyPassword) {
      fail(
        `A keystore already exists at ${file} but ANDROID_KEYSTORE_PASSWORD and ANDROID_KEY_PASSWORD are not set. Supply the stored passwords, or rotate deliberately by moving the keystore aside first.`,
      );
    }
    verify(file, alias, storePassword);
    report(`keystore ${file}`, 'present', 'read back, not regenerated');
  } else {
    storePassword ??= password();
    keyPassword ??= storePassword;
    generate({
      file,
      alias,
      storePassword,
      keyPassword,
      dname: env.ANDROID_KEY_DNAME ?? `CN=${alias}`,
    });
    report(`keystore ${file}`, 'created', `alias ${alias}`);
  }

  writeOutputs({
    ANDROID_KEY_ALIAS: alias,
    ANDROID_KEYSTORE_BASE64: fs.readFileSync(file).toString('base64'),
    ANDROID_KEYSTORE_PASSWORD: storePassword,
    ANDROID_KEY_PASSWORD: keyPassword,
  });
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

printSummary('create-keystore');
