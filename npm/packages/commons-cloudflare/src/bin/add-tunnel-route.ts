#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {api, resolveAccount} from '../services/api-client.js';

type Ingress = {hostname?: string; service: string; path?: string};
type Configuration = {config?: {ingress?: Ingress[]}};

const env = resolveEnv(
  ['CLOUDFLARE_API_TOKEN', 'TUNNEL_ID', 'TUNNEL_HOSTNAME', 'TUNNEL_SERVICE'],
  ['CLOUDFLARE_ACCOUNT_ID', 'TUNNEL_PATH'],
);

const cf = api(env.CLOUDFLARE_API_TOKEN);
const resource = env.TUNNEL_PATH
  ? `tunnel route ${env.TUNNEL_HOSTNAME}/${env.TUNNEL_PATH}`
  : `tunnel route ${env.TUNNEL_HOSTNAME}`;

const run = async (): Promise<void> => {
  const account = await resolveAccount(cf, env.CLOUDFLARE_ACCOUNT_ID);
  const path = `/accounts/${account}/cfd_tunnel/${env.TUNNEL_ID}/configurations`;

  const current = await cf.get<Configuration>(path);
  if (!current) {
    fail(`No tunnel ${env.TUNNEL_ID} in account ${account}.`);
  }

  const config = current.config ?? {};
  const ingress = config.ingress ?? [];
  const matches = (entry: Ingress): boolean =>
    entry.hostname === env.TUNNEL_HOSTNAME && entry.path === env.TUNNEL_PATH;
  const existing = ingress.find(matches);

  if (existing?.service === env.TUNNEL_SERVICE) {
    report(resource, 'present', `→ ${existing.service}`);
    return;
  }

  const rule: Ingress = {
    hostname: env.TUNNEL_HOSTNAME,
    service: env.TUNNEL_SERVICE,
    ...(env.TUNNEL_PATH ? {path: env.TUNNEL_PATH} : {}),
  };

  /**
   * The catch-all rule has no hostname and must stay last, so an inserted rule
   * goes before it and every existing rule is preserved. Path-specific rules
   * must precede the bare-hostname rule they'd otherwise be shadowed by, so
   * they're inserted before the first same-hostname entry rather than at the
   * end of the hostname group.
   */
  const kept = ingress.filter(entry => !matches(entry));
  const shadowedAt = env.TUNNEL_PATH
    ? kept.findIndex(
        entry => !entry.hostname || entry.hostname === env.TUNNEL_HOSTNAME,
      )
    : kept.findIndex(entry => !entry.hostname);
  const updated =
    shadowedAt === -1
      ? [...kept, rule]
      : [...kept.slice(0, shadowedAt), rule, ...kept.slice(shadowedAt)];

  await cf.send('PUT', path, {config: {...config, ingress: updated}});
  report(resource, existing ? 'updated' : 'created', `→ ${env.TUNNEL_SERVICE}`);
};

run()
  .then(() => printSummary('add-tunnel-route'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
