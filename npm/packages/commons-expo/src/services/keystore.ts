import crypto from 'crypto';
import {spawnSync} from 'child_process';

const run = (
  command: string,
  args: string[],
): {status: number; output: string} => {
  const result = spawnSync(command, args, {
    encoding: 'utf8',
    shell: process.platform === 'win32',
  });
  if (result.error) {
    throw new Error(`Could not run "${command}": ${result.error.message}`);
  }
  return {
    status: result.status ?? 1,
    output: `${result.stdout ?? ''}${result.stderr ?? ''}`.trim(),
  };
};

export const password = (): string =>
  crypto.randomBytes(24).toString('base64url');

/**
 * Link the app to its EAS project. Idempotent: `--force` overwrites an
 * already-configured id with the same value.
 */
export const linkEasProject = (projectId: string): void => {
  const result = run('npx', [
    '--yes',
    'eas-cli',
    'init',
    '--id',
    projectId,
    '--force',
    '--non-interactive',
  ]);
  if (result.status !== 0) {
    throw new Error(`eas init failed:\n${result.output}`);
  }
};

export const generate = (options: {
  file: string;
  alias: string;
  storePassword: string;
  keyPassword: string;
  dname: string;
}): void => {
  const result = run('keytool', [
    '-genkeypair',
    '-keystore',
    options.file,
    '-alias',
    options.alias,
    '-keyalg',
    'RSA',
    '-keysize',
    '2048',
    '-validity',
    '10000',
    '-storetype',
    'PKCS12',
    '-storepass',
    options.storePassword,
    '-keypass',
    options.keyPassword,
    '-dname',
    options.dname,
  ]);
  if (result.status !== 0) {
    throw new Error(`keytool failed:\n${result.output}`);
  }
};

/**
 * Confirm the keystore opens with the given password and holds the alias, so a
 * mismatch is reported rather than discovered by a failing release build.
 */
export const verify = (
  file: string,
  alias: string,
  storePassword: string,
): void => {
  const result = run('keytool', [
    '-list',
    '-keystore',
    file,
    '-alias',
    alias,
    '-storepass',
    storePassword,
  ]);
  if (result.status !== 0) {
    throw new Error(
      `Existing keystore ${file} does not open with the supplied password, or has no alias "${alias}":\n${result.output}`,
    );
  }
};
