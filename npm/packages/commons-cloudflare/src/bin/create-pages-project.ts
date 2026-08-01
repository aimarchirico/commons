#!/usr/bin/env node

import {
  context,
  defaultBranch,
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {api, resolveAccount} from '../services/api-client.js';

const env = resolveEnv(
  ['CLOUDFLARE_API_TOKEN', 'PAGES_PROJECT_NAME', 'PAGES_CUSTOM_DOMAIN'],
  ['CLOUDFLARE_ACCOUNT_ID'],
);

const cf = api(env.CLOUDFLARE_API_TOKEN);
const name = env.PAGES_PROJECT_NAME;
const domain = env.PAGES_CUSTOM_DOMAIN;

const productionBranch = (): string => {
  const derived = defaultBranch();
  context(
    'production branch',
    derived ?? 'main',
    derived
      ? "derived from the remote's default branch"
      : 'no remote, assumed default',
  );
  return derived ?? 'main';
};

const run = async (): Promise<void> => {
  const account = await resolveAccount(cf, env.CLOUDFLARE_ACCOUNT_ID);
  const projects = `/accounts/${account}/pages/projects`;

  const existing = await cf.get<{name: string}>(`${projects}/${name}`);
  if (existing) {
    report(`pages project ${name}`, 'present');
  } else {
    await cf.send('POST', projects, {
      name,
      production_branch: productionBranch(),
    });
    report(`pages project ${name}`, 'created');
  }

  const domains =
    (await cf.get<Array<{name: string}>>(`${projects}/${name}/domains`)) ?? [];
  if (domains.some(entry => entry.name === domain)) {
    report(`custom domain ${domain}`, 'present');
    return;
  }
  await cf.send('POST', `${projects}/${name}/domains`, {name: domain});
  await cf.send('PATCH', `${projects}/${name}/domains/${domain}`, {});
  report(`custom domain ${domain}`, 'created', 'automatic DNS requested');
};

run()
  .then(() => printSummary('create-pages-project'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
