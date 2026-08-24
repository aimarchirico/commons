#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {api, resolveAccount} from '../services/api-client.js';

type EnvVar = {type: string; value?: string};
type Project = {
  deployment_configs: Record<
    string,
    {env_vars?: Record<string, EnvVar | null>}
  >;
};

function parseNames(list?: string): string[] {
  return (list ?? '')
    .split(/[,\s]+/)
    .map(name => name.trim())
    .filter(Boolean);
}

/**
 * Sync Cloudflare Pages production environment variables and secrets.
 * Secrets use Cloudflare's secret_text type, which the API never returns a
 * value for on read, so a secret's "changed" state can't be diffed the way a
 * plain_text variable's can - it is written every run instead.
 */
export async function setPagesEnv(): Promise<void> {
  const env = resolveEnv(
    ['CLOUDFLARE_API_TOKEN', 'PAGES_PROJECT_NAME', 'PAGES_VARIABLES'],
    ['CLOUDFLARE_ACCOUNT_ID', 'PAGES_SECRETS'],
  );

  const cf = api(env.CLOUDFLARE_API_TOKEN);
  const target = 'production';
  const variableNames = parseNames(env.PAGES_VARIABLES);
  const secretNames = parseNames(env.PAGES_SECRETS);

  try {
    const account = await resolveAccount(cf, env.CLOUDFLARE_ACCOUNT_ID);
    const project = `/accounts/${account}/pages/projects/${env.PAGES_PROJECT_NAME}`;

    const current = await cf.get<Project>(project);
    if (!current) {
      fail(
        `No Pages project "${env.PAGES_PROJECT_NAME}". Run create-pages-project first.`,
      );
    }

    const existing = current.deployment_configs?.[target]?.env_vars ?? {};
    const changes: Record<string, EnvVar> = {};

    for (const name of variableNames) {
      const value = process.env[name];
      if (value === undefined || value === '') {
        report(
          `pages ${target} ${name}`,
          'skipped',
          'not set in the environment',
        );
        continue;
      }
      const before = existing[name];
      if (before?.value === value) {
        report(`pages ${target} ${name}`, 'present', 'value already correct');
        continue;
      }
      changes[name] = {type: 'plain_text', value};
      report(`pages ${target} ${name}`, before ? 'updated' : 'created');
    }

    for (const name of secretNames) {
      const value = process.env[name];
      if (value === undefined || value === '') {
        report(
          `pages ${target} ${name}`,
          'skipped',
          'not set in the environment',
        );
        continue;
      }
      changes[name] = {type: 'secret_text', value};
      report(
        `pages ${target} ${name}`,
        existing[name] ? 'updated' : 'created',
        'secret value cannot be diffed, written unconditionally',
      );
    }

    if (Object.keys(changes).length) {
      await cf.send('PATCH', project, {
        deployment_configs: {[target]: {env_vars: changes}},
      });
    }
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  printSummary('commons-cloudflare set-pages-env');
}
