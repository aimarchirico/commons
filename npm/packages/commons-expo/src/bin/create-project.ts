#!/usr/bin/env node

import {
  context,
  fail,
  printSummary,
  report,
  requireCli,
  resolveEnv,
  runJson,
  writeOutputs,
} from '@aimarchirico/commons-project';

type Initialized = {
  status: string;
  projectId: string;
  owner: string;
  slug: string;
  dashboardUrl: string;
};

requireCli('eas', {
  minVersion: '21.0.0',
  installHint:
    'Install it with "npm install -g eas-cli", then authenticate with "eas login" or set EXPO_TOKEN.',
});

// The account is derived from the app config's `owner` field, which eas-cli
// reads itself. The override exists because a token with access to several
// accounts cannot resolve one without being told.
const env = resolveEnv([], ['EXPO_ACCOUNT']);

const args = [
  'init',
  '--non-interactive',
  '--json',
  // Without --force, eas-cli treats both linking an existing project and
  // creating a missing one as decisions needing confirmation, which it cannot
  // ask for here.
  '--force',
];
if (env.EXPO_ACCOUNT) args.push('--account', env.EXPO_ACCOUNT);

context(
  'eas account',
  env.EXPO_ACCOUNT ?? 'from app config',
  env.EXPO_ACCOUNT ? 'from EXPO_ACCOUNT' : 'derived from the "owner" field',
);

try {
  const result = runJson<Initialized>('eas', args);
  report(
    `eas project ${result.owner}/${result.slug}`,
    result.status === 'created' ? 'created' : 'present',
    result.projectId,
  );
  writeOutputs({EAS_PROJECT_ID: result.projectId});
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

printSummary('create-project');
