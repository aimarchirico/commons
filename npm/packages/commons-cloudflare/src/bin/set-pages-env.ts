#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {api, resolveAccount} from '../services/api-client.js';
import {pathToFileURL} from 'url';

type EnvVar = {type: string; value?: string};
type Project = {
  deployment_configs: Record<
    string,
    {env_vars?: Record<string, EnvVar | null>}
  >;
};

/**
 * Sync Cloudflare Pages production environment variables.
 */
export async function setPagesEnv(): Promise<void> {
  const env = resolveEnv(
    ['CLOUDFLARE_API_TOKEN', 'PAGES_PROJECT_NAME', 'PAGES_VARIABLES'],
    ['CLOUDFLARE_ACCOUNT_ID'],
  );

  const cf = api(env.CLOUDFLARE_API_TOKEN);
  const target = 'production';
  const names = env.PAGES_VARIABLES.split(/[,\s]+/)
    .map(name => name.trim())
    .filter(Boolean);

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

    for (const name of names) {
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

    if (Object.keys(changes).length) {
      await cf.send('PATCH', project, {
        deployment_configs: {[target]: {env_vars: changes}},
      });
    }
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  printSummary('set-pages-env');
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  void setPagesEnv();
}
