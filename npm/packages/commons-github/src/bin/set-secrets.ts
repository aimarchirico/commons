#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {ghOrThrow, repoContext} from '../services/gh.js';
import {parseEnvironmentScopes, parseNames} from '../services/scopes.js';

function set(
  name: string,
  label: string,
  slug: string,
  environment?: string,
): void {
  const value = process.env[name];
  if (value === undefined || value === '') {
    report(`${label} ${name}`, 'skipped', 'not set in the environment');
    return;
  }
  const args = ['secret', 'set', name, '--repo', slug];
  if (environment) args.push('--env', environment);
  ghOrThrow(args, value);
  report(`${label} ${name}`, 'written');
}

/**
 * Set repository and environment secrets in GitHub.
 */
export function setSecrets(): void {
  const env = resolveEnv([], ['GITHUB_SECRETS', 'GITHUB_ENVIRONMENT_SECRETS']);
  const {slug} = repoContext();

  try {
    for (const name of parseNames(env.GITHUB_SECRETS)) {
      set(name, 'secret', slug);
    }

    for (const scope of parseEnvironmentScopes(
      env.GITHUB_ENVIRONMENT_SECRETS,
    )) {
      for (const name of scope.names) {
        set(name, `${scope.environment} secret`, slug, scope.environment);
      }
    }
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  printSummary('commons-github set-secrets');
}
