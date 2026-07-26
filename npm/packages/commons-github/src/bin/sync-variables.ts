#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-project/env';
import {fail, printSummary, report} from '@aimarchirico/commons-project/report';
import {apiGet, apiWrite, repoContext} from '../services/gh.js';
import {parseEnvironmentScopes, parseNames} from '../services/scopes.js';

const env = resolveEnv(
  [],
  ['GITHUB_VARIABLES', 'GITHUB_ENVIRONMENT_VARIABLES'],
);
const {slug} = repoContext();

const sync = (collection: string, label: string, name: string): void => {
  const value = process.env[name];
  if (value === undefined || value === '') {
    report(`${label} ${name}`, 'skipped', 'not set in the environment');
    return;
  }

  const current = apiGet<{value: string}>(`${collection}/${name}`);
  if (!current) {
    apiWrite('POST', collection, {name, value});
    report(`${label} ${name}`, 'created');
    return;
  }
  if (current.value === value) {
    report(`${label} ${name}`, 'present', 'value already correct');
    return;
  }
  apiWrite('PATCH', `${collection}/${name}`, {name, value});
  report(`${label} ${name}`, 'updated');
};

try {
  for (const name of parseNames(env.GITHUB_VARIABLES)) {
    sync(`repos/${slug}/actions/variables`, 'variable', name);
  }

  for (const scope of parseEnvironmentScopes(
    env.GITHUB_ENVIRONMENT_VARIABLES,
  )) {
    for (const name of scope.names) {
      sync(
        `repos/${slug}/environments/${scope.environment}/variables`,
        `${scope.environment} variable`,
        name,
      );
    }
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

printSummary('sync-variables');
