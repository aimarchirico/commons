import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {syncVariables} from '../sync-variables.js';
import {apiGet, apiWrite, repoContext} from '../../services/gh.js';

vi.mock('@aimarchirico/commons-project', () => ({
  fail: vi.fn((msg: string) => {
    throw new Error(`fail: ${msg}`);
  }),
  printSummary: vi.fn(),
  report: vi.fn(),
  resolveEnv: vi.fn(),
}));

vi.mock('../../services/gh.js', () => ({
  apiGet: vi.fn(),
  apiWrite: vi.fn(),
  repoContext: vi.fn(),
}));

describe('sync-variables.ts', () => {
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
    vi.mocked(apiGet).mockClear();
    vi.mocked(apiWrite).mockClear();
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

  it('skips variables when not set or empty in process.env', () => {
    process.env.EMPTY_VAR = '';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_VARIABLES: 'MISSING_VAR,EMPTY_VAR',
      GITHUB_ENVIRONMENT_VARIABLES: '',
    });

    syncVariables();

    expect(report).toHaveBeenCalledWith(
      'variable MISSING_VAR',
      'skipped',
      'not set in the environment',
    );
    expect(report).toHaveBeenCalledWith(
      'variable EMPTY_VAR',
      'skipped',
      'not set in the environment',
    );
    expect(apiGet).not.toHaveBeenCalled();
  });

  it('creates missing variable when apiGet returns undefined', () => {
    process.env.NEW_VAR = 'new-val';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_VARIABLES: 'NEW_VAR',
      GITHUB_ENVIRONMENT_VARIABLES: '',
    });
    vi.mocked(apiGet).mockReturnValue(undefined);

    syncVariables();

    expect(apiGet).toHaveBeenCalledWith(
      'repos/owner/repo/actions/variables/NEW_VAR',
    );
    expect(apiWrite).toHaveBeenCalledWith(
      'POST',
      'repos/owner/repo/actions/variables',
      {name: 'NEW_VAR', value: 'new-val'},
    );
    expect(report).toHaveBeenCalledWith('variable NEW_VAR', 'created');
  });

  it('reports present when variable value matches existing value', () => {
    process.env.SAME_VAR = 'same-val';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_VARIABLES: 'SAME_VAR',
      GITHUB_ENVIRONMENT_VARIABLES: '',
    });
    vi.mocked(apiGet).mockReturnValue({value: 'same-val'});

    syncVariables();

    expect(report).toHaveBeenCalledWith(
      'variable SAME_VAR',
      'present',
      'value already correct',
    );
    expect(apiWrite).not.toHaveBeenCalled();
  });

  it('updates variable when variable value differs from existing value', () => {
    process.env.DIFF_VAR = 'new-val';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_VARIABLES: 'DIFF_VAR',
      GITHUB_ENVIRONMENT_VARIABLES: '',
    });
    vi.mocked(apiGet).mockReturnValue({value: 'old-val'});

    syncVariables();

    expect(apiWrite).toHaveBeenCalledWith(
      'PATCH',
      'repos/owner/repo/actions/variables/DIFF_VAR',
      {name: 'DIFF_VAR', value: 'new-val'},
    );
    expect(report).toHaveBeenCalledWith('variable DIFF_VAR', 'updated');
  });

  it('syncs environment variables for environment scopes', () => {
    process.env.ENV_VAR = 'env-val';

    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_VARIABLES: '',
      GITHUB_ENVIRONMENT_VARIABLES: 'staging=ENV_VAR',
    });
    vi.mocked(apiGet).mockReturnValue(undefined);

    syncVariables();

    expect(apiGet).toHaveBeenCalledWith(
      'repos/owner/repo/environments/staging/variables/ENV_VAR',
    );
    expect(apiWrite).toHaveBeenCalledWith(
      'POST',
      'repos/owner/repo/environments/staging/variables',
      {name: 'ENV_VAR', value: 'env-val'},
    );
    expect(report).toHaveBeenCalledWith('staging variable ENV_VAR', 'created');
    expect(printSummary).toHaveBeenCalledWith('sync-variables');
  });

  it('catches non-Error exceptions and calls fail', () => {
    process.env.VAR = 'val';
    vi.mocked(resolveEnv).mockReturnValue({
      GITHUB_VARIABLES: 'VAR',
      GITHUB_ENVIRONMENT_VARIABLES: '',
    });
    vi.mocked(apiGet).mockImplementation(() => {
      throw new Error('api error');
    });

    expect(() => syncVariables()).toThrow('fail: api error');
    expect(fail).toHaveBeenCalledWith('api error');
  });
});
