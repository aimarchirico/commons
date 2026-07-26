#!/usr/bin/env node

import {resolveEnv} from '@aimarchirico/commons-project/env';
import {writeOutputs} from '@aimarchirico/commons-project/outputs';
import {fail, printSummary, report} from '@aimarchirico/commons-project/report';
import {api} from '../services/api.js';

type ServiceToken = {
  id: string;
  name: string;
  client_id: string;
  client_secret?: string;
};
type Policy = {include?: Array<Record<string, unknown>>};

const env = resolveEnv([
  'CLOUDFLARE_ACCOUNT_ID',
  'CLOUDFLARE_API_TOKEN',
  'SERVICE_TOKEN_NAME',
  'ACCESS_POLICY_ID',
]);

const cf = api(env.CLOUDFLARE_API_TOKEN);
const account = `/accounts/${env.CLOUDFLARE_ACCOUNT_ID}`;
const tokens = `${account}/access/service_tokens`;
const policyPath = `${account}/access/policies/${env.ACCESS_POLICY_ID}`;
const name = env.SERVICE_TOKEN_NAME;

const attach = async (token: ServiceToken): Promise<void> => {
  const policy = await cf.get<Policy>(policyPath);
  if (!policy) {
    fail(
      `No Access policy ${env.ACCESS_POLICY_ID} in account ${env.CLOUDFLARE_ACCOUNT_ID}.`,
    );
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
  const existing = ((await cf.get<ServiceToken[]>(tokens)) ?? []).find(
    token => token.name === name,
  );

  if (existing) {
    // A service token's secret is returned only at creation, so an existing
    // token is left alone: reuse the stored secret, or rotate deliberately by
    // deleting the token first.
    report(
      `service token ${name}`,
      'present',
      'secret cannot be re-read; reuse the stored value or rotate deliberately',
    );
    writeOutputs({CF_ACCESS_CLIENT_ID: existing.client_id});
    await attach(existing);
    return;
  }

  const created = await cf.send<ServiceToken>('POST', tokens, {name});
  report(`service token ${name}`, 'created');
  writeOutputs({
    CF_ACCESS_CLIENT_ID: created.client_id,
    CF_ACCESS_CLIENT_SECRET: created.client_secret ?? '',
  });
  await attach(created);
};

run()
  .then(() => printSummary('create-service-token'))
  .catch((error: unknown) => {
    fail(error instanceof Error ? error.message : String(error));
  });
