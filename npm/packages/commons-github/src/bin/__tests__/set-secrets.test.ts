import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {setSecrets} from '../set-secrets.js';
import {ghOrThrow, repoContext} from '../../services/gh.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
}));

vi.mock('../../services/gh.js', () => ({
  ghOrThrow: vi.fn(),
  repoContext: vi.fn(),
}));

describe('set-secrets.ts', () => {
  const originalEnv = process.env;

  beforeEach(() => {
    process.env = {...originalEnv};
    vi.mocked(fail).mockClear();
    vi.mocked(fail).mockImplementation((msg: string) => {
      throw new Error(`fail: ${msg}`);
    });
    vi.mocked(printSummary).mockClear();
    vi.mocked(report).mockClear();
    vi.mocked(resolveEnv).mockClear();
    vi.mocked(ghOrThrow).mockClear();
    vi.mocked(repoContext).mockClear();

    vi.mocked(repoContext).mockReturnValue({
      owner: 'owner',
      repo: 'repo',
      slug: 'owner/repo',
    });
  });

  afterEach(() => {
    process.env = originalEnv;
  });

  it('sets secrets and environment secrets when present in process.env', () => {
    process.env.MY_SECRET = 'secret-val';
    process.env.ENV_SECRET = 'env-val';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_SECRETS: 'MY_SECRET',
      GITHUB_ENVIRONMENT_SECRETS: 'prod=ENV_SECRET',
    });

    setSecrets();

    expect(ghOrThrow).toHaveBeenCalledWith(
      ['secret', 'set', 'MY_SECRET', '--repo', 'owner/repo'],
      'secret-val',
    );
    expect(report).toHaveBeenCalledWith('secret MY_SECRET', 'written');

    expect(ghOrThrow).toHaveBeenCalledWith(
      ['secret', 'set', 'ENV_SECRET', '--repo', 'owner/repo', '--env', 'prod'],
      'env-val',
    );
    expect(report).toHaveBeenCalledWith('prod secret ENV_SECRET', 'written');
    expect(printSummary).toHaveBeenCalledWith('commons-github set-secrets');
  });

  it('skips secrets when not set or empty in process.env', () => {
    process.env.EMPTY_SECRET = '';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_SECRETS: 'MISSING_SECRET,EMPTY_SECRET',
      GITHUB_ENVIRONMENT_SECRETS: '',
    });

    setSecrets();

    expect(report).toHaveBeenCalledWith(
      'secret MISSING_SECRET',
      'skipped',
      'not set in the environment',
    );
    expect(report).toHaveBeenCalledWith(
      'secret EMPTY_SECRET',
      'skipped',
      'not set in the environment',
    );
    expect(ghOrThrow).not.toHaveBeenCalled();
  });

  it('catches non-Error exceptions and calls fail', () => {
    process.env.MY_SECRET = 'val';
    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_SECRETS: 'MY_SECRET',
      GITHUB_ENVIRONMENT_SECRETS: '',
    });
    vi.mocked(ghOrThrow).mockImplementation(() => {
      throw 'secret error';
    });

    expect(() => setSecrets()).toThrow('fail: secret error');
    expect(fail).toHaveBeenCalledWith('secret error');
  });
});
