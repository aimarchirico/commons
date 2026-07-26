#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-project/env';
import {fail, printSummary, report} from '@aimarchirico/commons-project/report';
import {api} from '../services/api.js';

const env = resolveEnv(
  [
    'CLOUDFLARE_ACCOUNT_ID',
    'CLOUDFLARE_API_TOKEN',
    'PAGES_PROJECT_NAME',
    'PAGES_CUSTOM_DOMAIN',
  ],
  ['PAGES_PRODUCTION_BRANCH'],
);

const cf = api(env.CLOUDFLARE_API_TOKEN);
const projects = `/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/pages/projects`;
const name = env.PAGES_PROJECT_NAME;
const domain = env.PAGES_CUSTOM_DOMAIN;

const run = async (): Promise<void> => {
  const existing = await cf.get<{name: string}>(`${projects}/${name}`);
  if (existing) {
    report(`pages project ${name}`, 'present');
  } else {
    await cf.send('POST', projects, {
      name,
      production_branch: env.PAGES_PRODUCTION_BRANCH ?? 'main',
    });
    report(`pages project ${name}`, 'created');
  }

  // A Pages project without its custom domain is never a wanted end state, so
  // attaching it belongs to this command rather than a separate one.
  const domains =
    (await cf.get<Array<{name: string}>>(`${projects}/${name}/domains`)) ?? [];
  if (domains.some(entry => entry.name === domain)) {
    report(`custom domain ${domain}`, 'present');
    return;
  }
  await cf.send('POST', `${projects}/${name}/domains`, {name: domain});
  // Requests verification, which creates the DNS record automatically when the
  // domain's zone belongs to the same account.
  await cf.send('PATCH', `${projects}/${name}/domains/${domain}`, {});
  report(`custom domain ${domain}`, 'created', 'automatic DNS requested');
};

run()
  .then(() => printSummary('create-pages-project'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
