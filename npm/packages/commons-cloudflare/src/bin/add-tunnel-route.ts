#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {api, resolveAccount} from '../services/api-client.js';
import {pathToFileURL} from 'url';

type Ingress = {hostname?: string; service: string; path?: string};
type Configuration = {config?: {ingress?: Ingress[]}};

/**
 * Add or update a Cloudflare Tunnel ingress route.
 */
export async function addTunnelRoute(): Promise<void> {
  const env = resolveEnv(
    ['CLOUDFLARE_API_TOKEN', 'TUNNEL_ID', 'TUNNEL_HOSTNAME', 'TUNNEL_SERVICE'],
    ['CLOUDFLARE_ACCOUNT_ID', 'TUNNEL_PATH'],
  );

  const cf = api(env.CLOUDFLARE_API_TOKEN);
  const resource = env.TUNNEL_PATH
    ? `tunnel route ${env.TUNNEL_HOSTNAME}/${env.TUNNEL_PATH}`
    : `tunnel route ${env.TUNNEL_HOSTNAME}`;

  try {
    const account = await resolveAccount(cf, env.CLOUDFLARE_ACCOUNT_ID);
    const path = `/accounts/${account}/cfd_tunnel/${env.TUNNEL_ID}/configurations`;

    const current = await cf.get<Configuration>(path);
    if (!current) {
      fail(`No tunnel ${env.TUNNEL_ID} in account ${account}.`);
    }

    const config = current.config ?? {};
    const ingress = config.ingress ?? [];
    function matches(entry: Ingress): boolean {
      return (
        entry.hostname === env.TUNNEL_HOSTNAME && entry.path === env.TUNNEL_PATH
      );
    }
    const existing = ingress.find(matches);

    if (existing?.service === env.TUNNEL_SERVICE) {
      report(resource, 'present', `→ ${existing.service}`);
    } else {
      const rule: Ingress = {
        hostname: env.TUNNEL_HOSTNAME,
        service: env.TUNNEL_SERVICE,
        ...(env.TUNNEL_PATH ? {path: env.TUNNEL_PATH} : {}),
      };

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
      report(
        resource,
        existing ? 'updated' : 'created',
        `→ ${env.TUNNEL_SERVICE}`,
      );
    }
  } catch (error) {
    fail(error instanceof Error ? error.message : String(error));
  }

  printSummary('add-tunnel-route');
}

if (import.meta.url === pathToFileURL(process.argv[1]).href) {
  void addTunnelRoute();
}
