#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-ts/env';
import {fail, printSummary, report} from '@aimarchirico/commons-ts/report';
import {apiGet, apiWrite, repoContext} from '../services/gh.js';
import {parseNames} from '../services/scopes.js';

const env = resolveEnv(['GITHUB_ENVIRONMENTS']);
const {slug} = repoContext();
const environments = parseNames(env.GITHUB_ENVIRONMENTS);

if (!environments.length) {
  fail('GITHUB_ENVIRONMENTS is set but names no environments.');
}

try {
  for (const name of environments) {
    const endpoint = `repos/${slug}/environments/${name}`;
    if (apiGet(endpoint)) {
      report(`environment ${name}`, 'present');
      continue;
    }
    apiWrite('PUT', endpoint);
    report(`environment ${name}`, 'created');
  }
} catch (error) {
  fail(error instanceof Error ? error.message : String(error));
}

printSummary('create-environments');
