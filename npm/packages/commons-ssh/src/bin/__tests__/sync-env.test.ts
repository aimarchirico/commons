import {
  fail,
  printSummary,
  report,
  resolveEnv,
  writeOutputs,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {syncEnv} from '../sync-env.js';
import {sshRun} from '../../services/ssh.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
  writeOutputs: vi.fn(),
}));

vi.mock('../../services/ssh.js', () => ({sshRun: vi.fn()}));

const baseEnv = {
  SSH_HOST: 'vps.example.com',
  SSH_USER: 'deploy',
  SSH_KEY_FILE: '/keys/id',
  REMOTE_ENV_PATH: '~/docker/app/.env',
};

describe('sync-env.ts', () => {
  beforeEach(() => {
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveEnv).mockClear();
    vi.mocked(writeOutputs).mockClear();
    vi.mocked(sshRun).mockClear();
  });

  it('fails when the remote read fails', () => {
    vi.mocked(resolveEnv).mockReturnValue({...baseEnv});
    vi.mocked(sshRun).mockReturnValue({
      status: 1,
      stdout: '',
      stderr: 'permission denied',
    });

    expect(() => syncEnv()).toThrow(/fail: Could not read/);
  });

  it('fails when the remote write fails', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ...baseEnv,
      ENV_VALUES: 'HOST=db:5432',
    });
    vi.mocked(sshRun).mockImplementation((_target, command) =>
      command.startsWith('cat')
        ? {status: 0, stdout: '', stderr: ''}
        : {status: 1, stdout: '', stderr: 'no space left'},
    );

    expect(() => syncEnv()).toThrow(/fail: Could not write/);
  });

  it('reuses existing defaults and secrets, keeps fresh values fresh', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ...baseEnv,
      ENV_VALUES: 'HOST=db:5432',
      ENV_DEFAULTS: 'USER=app',
      ENV_SECRET_KEYS: 'PASSWORD',
    });
    vi.mocked(sshRun).mockImplementation((_target, command) => {
      if (command.startsWith('cat')) {
        return {
          status: 0,
          stdout:
            'HOST="old:5432"\nUSER="existing-user"\nPASSWORD="existing-pw"\n',
          stderr: '',
        };
      }
      return {status: 0, stdout: '', stderr: ''};
    });

    syncEnv();

    expect(sshRun).toHaveBeenCalledWith(
      {host: 'vps.example.com', user: 'deploy', keyFile: '/keys/id'},
      'mkdir -p ~/docker/app && cat > ~/docker/app/.env && chmod 600 ~/docker/app/.env',
      'HOST="db:5432"\nUSER="existing-user"\nPASSWORD="existing-pw"\n',
    );
    expect(report).toHaveBeenCalledWith('env HOST', 'updated');
    expect(report).toHaveBeenCalledWith('env USER', 'present');
    expect(report).toHaveBeenCalledWith('env PASSWORD', 'present');
    expect(printSummary).toHaveBeenCalledWith('commons-ssh sync-env');
  });

  it('generates a secret and applies a default when nothing exists remotely', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ...baseEnv,
      ENV_DEFAULTS: 'USER=app',
      ENV_SECRET_KEYS: 'PASSWORD',
    });
    vi.mocked(sshRun).mockImplementation((_target, command) =>
      command.startsWith('cat')
        ? {status: 0, stdout: '', stderr: ''}
        : {status: 0, stdout: '', stderr: ''},
    );

    syncEnv();

    expect(report).toHaveBeenCalledWith('env USER', 'created');
    expect(report).toHaveBeenCalledWith('env PASSWORD', 'created');
    const resource = `${baseEnv.SSH_USER}@${baseEnv.SSH_HOST}:${baseEnv.REMOTE_ENV_PATH}`;
    expect(report).toHaveBeenCalledWith(resource, 'written', 'mode 600');
  });

  it('reports the file as present when every resolved value is unchanged', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ...baseEnv,
      ENV_DEFAULTS: 'USER=app',
    });
    vi.mocked(sshRun).mockImplementation((_target, command) =>
      command.startsWith('cat')
        ? {status: 0, stdout: 'USER="app"\n', stderr: ''}
        : {status: 0, stdout: '', stderr: ''},
    );

    syncEnv();

    const resource = `${baseEnv.SSH_USER}@${baseEnv.SSH_HOST}:${baseEnv.REMOTE_ENV_PATH}`;
    expect(report).toHaveBeenCalledWith(resource, 'present', 'mode 600');
  });

  it('writes only the requested keys to outputs', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ...baseEnv,
      ENV_SECRET_KEYS: 'PROXY_SECRET',
      OUTPUT_KEYS: 'PROXY_SECRET',
    });
    vi.mocked(sshRun).mockImplementation((_target, command) =>
      command.startsWith('cat')
        ? {status: 0, stdout: 'PROXY_SECRET="existing-secret"\n', stderr: ''}
        : {status: 0, stdout: '', stderr: ''},
    );

    syncEnv();

    expect(writeOutputs).toHaveBeenCalledWith({
      PROXY_SECRET: 'existing-secret',
    });
  });

  it('does not call writeOutputs when OUTPUT_KEYS is unset', () => {
    vi.mocked(resolveEnv).mockReturnValue({...baseEnv});
    vi.mocked(sshRun).mockReturnValue({status: 0, stdout: '', stderr: ''});

    syncEnv();

    expect(writeOutputs).not.toHaveBeenCalled();
  });
});
