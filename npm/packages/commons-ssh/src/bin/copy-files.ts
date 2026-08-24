#!/usr/bin/env node

import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {scpFiles} from '../services/ssh.js';

/**
 * Copy local files to a directory on a remote host over scp.
 */
export function copyFiles(): void {
  const env = resolveEnv([
    'SSH_HOST',
    'SSH_USER',
    'SSH_KEY_FILE',
    'REMOTE_DIR',
    'LOCAL_FILES',
  ]);
  const target = {
    host: env.SSH_HOST,
    user: env.SSH_USER,
    keyFile: env.SSH_KEY_FILE,
  };
  const localFiles = env.LOCAL_FILES.split(',')
    .map(file => file.trim())
    .filter(Boolean);
  const resource = `${env.SSH_USER}@${env.SSH_HOST}:${env.REMOTE_DIR}`;

  if (!localFiles.length) {
    fail('LOCAL_FILES is set but names no files.');
  }

  const status = scpFiles(target, localFiles, env.REMOTE_DIR);
  if (status !== 0) {
    fail(`Could not copy files to ${resource}.`);
  }

  report(resource, 'written', localFiles.join(', '));
  printSummary('commons-ssh copy-files');
}
