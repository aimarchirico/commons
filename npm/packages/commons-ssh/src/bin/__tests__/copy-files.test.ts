import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {copyFiles} from '../copy-files.js';
import {scpFiles} from '../../services/ssh.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
}));

vi.mock('../../services/ssh.js', () => ({scpFiles: vi.fn()}));

const baseEnv = {
  SSH_HOST: 'vps.example.com',
  SSH_USER: 'deploy',
  SSH_KEY_FILE: '/keys/id',
  REMOTE_DIR: '~/docker/app',
};

describe('copy-files.ts', () => {
  beforeEach(() => {
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveEnv).mockClear();
    vi.mocked(scpFiles).mockClear();
  });

  it('copies the listed files and reports success', () => {
    vi.mocked(resolveEnv).mockReturnValue({
      ...baseEnv,
      LOCAL_FILES: 'a.txt, b.txt',
    });
    vi.mocked(scpFiles).mockReturnValue(0);

    copyFiles();

    expect(scpFiles).toHaveBeenCalledWith(
      {host: 'vps.example.com', user: 'deploy', keyFile: '/keys/id'},
      ['a.txt', 'b.txt'],
      '~/docker/app',
    );
    expect(report).toHaveBeenCalledWith(
      'deploy@vps.example.com:~/docker/app',
      'written',
      'a.txt, b.txt',
    );
    expect(printSummary).toHaveBeenCalledWith('commons-ssh copy-files');
  });

  it('fails when LOCAL_FILES names no files', () => {
    vi.mocked(resolveEnv).mockReturnValue({...baseEnv, LOCAL_FILES: ' , '});

    expect(() => copyFiles()).toThrow(/fail: LOCAL_FILES/);
    expect(scpFiles).not.toHaveBeenCalled();
  });

  it('fails when scp exits non-zero', () => {
    vi.mocked(resolveEnv).mockReturnValue({...baseEnv, LOCAL_FILES: 'a.txt'});
    vi.mocked(scpFiles).mockReturnValue(1);

    expect(() => copyFiles()).toThrow(/fail: Could not copy files/);
  });
});
