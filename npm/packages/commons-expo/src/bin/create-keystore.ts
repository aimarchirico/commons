#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-project/env';
import {writeOutputs} from '@aimarchirico/commons-project/outputs';
import {fail, printSummary, report} from '@aimarchirico/commons-project/report';
import {
  createAppCredentials,
  createBuildCredentials,
  createKeystore,
  resolveApp,
} from '../services/eas.js';
import type {Keystore} from '../services/eas.js';
import {generate, password} from '../services/keystore.js';

const env = resolveEnv(
  ['EAS_PROJECT_ID', 'ANDROID_APPLICATION_ID'],
  [
    'EXPO_TOKEN',
    'ANDROID_KEY_ALIAS',
    'ANDROID_KEYSTORE_PASSWORD',
    'ANDROID_KEY_PASSWORD',
    'ANDROID_KEY_DNAME',
    'ANDROID_BUILD_CREDENTIALS_NAME',
  ],
);

const alias = env.ANDROID_KEY_ALIAS ?? 'release';
const profile = env.ANDROID_BUILD_CREDENTIALS_NAME ?? 'production';

const run = async (): Promise<void> => {
  const app = await resolveApp(env.EAS_PROJECT_ID);
  report(`eas project ${app.fullName}`, 'present', app.id);

  const appCredentials = app.androidAppCredentials.find(
    entry => entry.applicationIdentifier === env.ANDROID_APPLICATION_ID,
  );
  const existing = appCredentials?.androidAppBuildCredentialsList.find(
    entry => entry.name === profile,
  );

  let keystore: Keystore;

  if (existing?.androidKeystore) {
    // Replacing signing keys breaks updates for every installed copy of the
    // app, so an existing keystore is only ever read back.
    keystore = existing.androidKeystore;
    report(
      `keystore for "${profile}"`,
      'present',
      'read back from EAS, not regenerated',
    );
  } else {
    const storePassword = env.ANDROID_KEYSTORE_PASSWORD ?? password();
    const keyPassword = env.ANDROID_KEY_PASSWORD ?? storePassword;
    const base64EncodedKeystore = generate({
      alias,
      storePassword,
      keyPassword,
      dname: env.ANDROID_KEY_DNAME ?? `CN=${alias}`,
    });

    keystore = await createKeystore(app.ownerAccount.id, {
      base64EncodedKeystore,
      keystorePassword: storePassword,
      keyAlias: alias,
      keyPassword,
    });
    report(`keystore for "${profile}"`, 'created', `alias ${alias}`);

    const target =
      appCredentials ??
      (await createAppCredentials(app.id, env.ANDROID_APPLICATION_ID));
    if (!appCredentials) {
      report(
        `android credentials ${env.ANDROID_APPLICATION_ID}`,
        'created',
        target.id,
      );
    }

    await createBuildCredentials(target.id, {
      name: profile,
      isDefault: true,
      keystoreId: keystore.id,
    });
    report(`build credentials "${profile}"`, 'created', 'stored in EAS');
  }

  writeOutputs({
    ANDROID_KEY_ALIAS: keystore.keyAlias,
    ANDROID_KEYSTORE_BASE64: keystore.keystore,
    ANDROID_KEYSTORE_PASSWORD: keystore.keystorePassword,
    ANDROID_KEY_PASSWORD: keystore.keyPassword ?? keystore.keystorePassword,
  });
};

run()
  .then(() => printSummary('create-keystore'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
