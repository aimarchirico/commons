import {
  fail,
  printSummary,
  report,
  resolveEnv,
} from '@aimarchirico/commons-project';
import {beforeEach, describe, expect, it, vi} from 'vitest';
import {createEnvironments} from '../create-environments.js';
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

describe('create-environments.ts', () => {
  beforeEach(() => {
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

  it('fails if no environments are specified', () => {
    vi.mocked(resolveEnv).mockReturnValue({GITHUB_ENVIRONMENTS: ''});
    expect(() => createEnvironments()).toThrow(
      'fail: GITHUB_ENVIRONMENTS is set but names no environments.',
    );
    expect(fail).toHaveBeenCalledWith(
      'GITHUB_ENVIRONMENTS is set but names no environments.',
    );
  });

  it('creates environments when they are missing and reports present when existing', () => {
    vi.mocked(resolveEnv).mockReturnValue({GITHUB_ENVIRONMENTS: 'dev,prod'});
    vi.mocked(apiGet).mockImplementation((endpoint: string) =>
      endpoint.includes('dev'),
    );

    createEnvironments();

    expect(report).toHaveBeenCalledWith('environment dev', 'present');
    expect(apiWrite).toHaveBeenCalledWith(
      'PUT',
      'repos/owner/repo/environments/prod',
    );
    expect(report).toHaveBeenCalledWith('environment prod', 'created');
    expect(printSummary).toHaveBeenCalledWith('create-environments');
  });

  it('catches non-Error exceptions and calls fail', () => {
    vi.mocked(resolveEnv).mockReturnValue({GITHUB_ENVIRONMENTS: 'dev'});
    vi.mocked(apiGet).mockImplementation(() => {
      throw 'string error';
    });

    expect(() => createEnvironments()).toThrow('fail: string error');
    expect(fail).toHaveBeenCalledWith('string error');
  });
});
