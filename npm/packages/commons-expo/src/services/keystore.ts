import crypto from 'crypto';
import fs from 'fs';
import os from 'os';
import path from 'path';
import {spawnSync} from 'child_process';

export const password = (): string =>
  crypto.randomBytes(24).toString('base64url');

/**
 * Generate a keystore and return it base64-encoded. It is written to a
 * temporary file only because `keytool` has no way to emit to stdout, and
 * removed immediately: EAS is where the keystore is kept.
 */
export const generate = (options: {
  alias: string;
  storePassword: string;
  keyPassword: string;
  dname: string;
}): string => {
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'keystore-'));
  const file = path.join(dir, 'release.keystore');
  try {
    const result = spawnSync(
      'keytool',
      [
        '-genkeypair',
        '-keystore',
        file,
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
      ],
      {encoding: 'utf8', shell: process.platform === 'win32'},
    );
    if (result.error) {
      throw new Error(`Could not run keytool: ${result.error.message}`);
    }
    if (result.status !== 0) {
      throw new Error(
        `keytool failed:\n${`${result.stdout ?? ''}${result.stderr ?? ''}`.trim()}`,
      );
    }
    return fs.readFileSync(file).toString('base64');
  } finally {
    fs.rmSync(dir, {recursive: true, force: true});
  }
};
