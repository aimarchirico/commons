#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {api, resolveAccount} from '../services/api-client.js';

type ServiceToken = {
  id: string;
  name: string;
  client_id: string;
  client_secret?: string;
};
type Policy = {include?: Array<Record<string, unknown>>};

const env = resolveEnv(
  ['CLOUDFLARE_API_TOKEN', 'SERVICE_TOKEN_NAME', 'ACCESS_POLICY_ID'],
  ['CLOUDFLARE_ACCOUNT_ID'],
);

const cf = api(env.CLOUDFLARE_API_TOKEN);
const name = env.SERVICE_TOKEN_NAME;

const attach = async (
  token: ServiceToken,
  policyPath: string,
  account: string,
): Promise<void> => {
  const policy = await cf.get<Policy>(policyPath);
  if (!policy) {
    fail(`No Access policy ${env.ACCESS_POLICY_ID} in account ${account}.`);
  }
  const include = policy.include ?? [];
  const attached = include.some(
    rule =>
      (rule.service_token as {token_id?: string} | undefined)?.token_id ===
      token.id,
  );
  if (attached) {
    report(`policy ${env.ACCESS_POLICY_ID}`, 'present', `includes ${name}`);
    return;
  }
  await cf.send('PUT', policyPath, {
    ...policy,
    include: [...include, {service_token: {token_id: token.id}}],
  });
  report(`policy ${env.ACCESS_POLICY_ID}`, 'updated', `includes ${name}`);
};

const run = async (): Promise<void> => {
  const account = await resolveAccount(cf, env.CLOUDFLARE_ACCOUNT_ID);
  const base = `/accounts/${account}`;
  const tokens = `${base}/access/service_tokens`;
  const policyPath = `${base}/access/policies/${env.ACCESS_POLICY_ID}`;

  const existing = ((await cf.get<ServiceToken[]>(tokens)) ?? []).find(
    token => token.name === name,
  );

  if (existing) {
    /**
     * A service token's secret is returned only at creation, so an existing
     * token is left alone: reuse the stored secret, or rotate deliberately by
     * deleting the token first.
     */
    report(
      `service token ${name}`,
      'present',
      'secret cannot be re-read; reuse the stored value or rotate deliberately',
    );
    writeOutputs({CF_ACCESS_CLIENT_ID: existing.client_id});
    await attach(existing, policyPath, account);
    return;
  }

  const created = await cf.send<ServiceToken>('POST', tokens, {name});
  report(`service token ${name}`, 'created');
  writeOutputs({
    CF_ACCESS_CLIENT_ID: created.client_id,
    CF_ACCESS_CLIENT_SECRET: created.client_secret ?? '',
  });
  await attach(created, policyPath, account);
};

run()
  .then(() => printSummary('create-service-token'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
