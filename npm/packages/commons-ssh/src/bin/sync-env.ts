#!/usr/bin/env node

import crypto from 'crypto';
import path from 'path';
import {
  fail,
  printSummary,
  report,
  resolveEnv,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {sshRun} from '../services/ssh.js';

function parsePairs(list?: string): Record<string, string> {
  return Object.fromEntries(
    (list ?? '')
      .split(',')
      .map(entry => entry.trim())
      .filter(Boolean)
      .map(entry => {
        const index = entry.indexOf('=');
        return [entry.slice(0, index), entry.slice(index + 1)];
      }),
  );
}

function parseNames(list?: string): string[] {
  return (list ?? '')
    .split(',')
    .map(name => name.trim())
    .filter(Boolean);
}

function parseRemoteEnv(text: string): Record<string, string> {
  return Object.fromEntries(
    text
      .split('\n')
      .map(line => line.trim())
      .filter(line => line && !line.startsWith('#'))
      .map(line => {
        const index = line.indexOf('=');
        return [
          line.slice(0, index),
          line.slice(index + 1).replace(/^"|"$/g, ''),
        ];
      })
      .filter(([name]) => name),
  );
}

const generateSecret = (): string =>
  crypto.randomBytes(32).toString('base64url');

/**
 * Reconcile a `.env` file on a remote host: reuse whatever already exists
 * there, generate any missing secrets, and write the merged result back.
 */
export function syncEnv(): void {
  const env = resolveEnv(
    ['SSH_HOST', 'SSH_USER', 'SSH_KEY_FILE', 'REMOTE_ENV_PATH'],
    ['ENV_VALUES', 'ENV_DEFAULTS', 'ENV_SECRET_KEYS', 'OUTPUT_KEYS'],
  );
  const target = {
    host: env.SSH_HOST,
    user: env.SSH_USER,
    keyFile: env.SSH_KEY_FILE,
  };
  const resource = `${env.SSH_USER}@${env.SSH_HOST}:${env.REMOTE_ENV_PATH}`;

  const read = sshRun(target, `cat ${env.REMOTE_ENV_PATH} 2>/dev/null || true`);
  if (read.status !== 0) {
    fail(`Could not read ${resource}:\n${read.stderr}`);
  }
  const existing = parseRemoteEnv(read.stdout);

  const values = parsePairs(env.ENV_VALUES);
  const defaults = parsePairs(env.ENV_DEFAULTS);
  const secretKeys = parseNames(env.ENV_SECRET_KEYS);

  const resolved: Record<string, string> = {...values};
  for (const [key, fallback] of Object.entries(defaults)) {
    resolved[key] = existing[key] ?? fallback;
  }
  for (const key of secretKeys) {
    resolved[key] = existing[key] ?? process.env[key] ?? generateSecret();
  }

  const remoteDir = path.dirname(env.REMOTE_ENV_PATH).replace(/\\/g, '/');
  const contents = `${Object.entries(resolved)
    .map(([key, value]) => `${key}="${value}"`)
    .join('\n')}\n`;

  const write = sshRun(
    target,
    `mkdir -p ${remoteDir} && cat > ${env.REMOTE_ENV_PATH} && chmod 600 ${env.REMOTE_ENV_PATH}`,
    contents,
  );
  if (write.status !== 0) {
    fail(`Could not write ${resource}:\n${write.stderr}`);
  }

  const unchanged = Object.keys(resolved).every(
    key => existing[key] === resolved[key],
  );
  report(resource, unchanged ? 'present' : 'written', 'mode 600');
  for (const key of Object.keys(resolved)) {
    const before = existing[key];
    const outcome =
      before === undefined
        ? 'created'
        : before === resolved[key]
          ? 'present'
          : 'updated';
    report(`env ${key}`, outcome);
  }

  const outputKeys = parseNames(env.OUTPUT_KEYS);
  if (outputKeys.length) {
    writeOutputs(
      Object.fromEntries(outputKeys.map(key => [key, resolved[key]])),
    );
  }

  printSummary('commons-ssh sync-env');
}
