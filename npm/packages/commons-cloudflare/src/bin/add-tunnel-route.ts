#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-ts/env';
import {fail, printSummary, report} from '@aimarchirico/commons-ts/report';
import {api} from '../services/api.js';

type Ingress = {hostname?: string; service: string; path?: string};
type Configuration = {config?: {ingress?: Ingress[]}};

const env = resolveEnv([
  'CLOUDFLARE_ACCOUNT_ID',
  'CLOUDFLARE_API_TOKEN',
  'TUNNEL_ID',
  'TUNNEL_HOSTNAME',
  'TUNNEL_SERVICE',
]);

const cf = api(env.CLOUDFLARE_API_TOKEN);
const path = `/accounts/${env.CLOUDFLARE_ACCOUNT_ID}/cfd_tunnel/${env.TUNNEL_ID}/configurations`;
const resource = `tunnel route ${env.TUNNEL_HOSTNAME}`;

const run = async (): Promise<void> => {
  const current = await cf.get<Configuration>(path);
  if (!current) {
    fail(`No tunnel ${env.TUNNEL_ID} in account ${env.CLOUDFLARE_ACCOUNT_ID}.`);
  }

  const config = current.config ?? {};
  const ingress = config.ingress ?? [];
  const existing = ingress.find(rule => rule.hostname === env.TUNNEL_HOSTNAME);

  if (existing?.service === env.TUNNEL_SERVICE) {
    report(resource, 'present', `→ ${existing.service}`);
    return;
  }

  const rule: Ingress = {
    hostname: env.TUNNEL_HOSTNAME,
    service: env.TUNNEL_SERVICE,
  };

  // The catch-all rule has no hostname and must stay last, so an inserted rule
  // goes before it and every existing rule is preserved.
  const kept = ingress.filter(entry => entry.hostname !== env.TUNNEL_HOSTNAME);
  const catchAllAt = kept.findIndex(entry => !entry.hostname);
  const updated =
    catchAllAt === -1
      ? [...kept, rule]
      : [...kept.slice(0, catchAllAt), rule, ...kept.slice(catchAllAt)];

  await cf.send('PUT', path, {config: {...config, ingress: updated}});
  report(resource, existing ? 'updated' : 'created', `→ ${env.TUNNEL_SERVICE}`);
};

run()
  .then(() => printSummary('add-tunnel-route'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
