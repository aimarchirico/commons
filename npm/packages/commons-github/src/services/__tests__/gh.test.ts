import {beforeEach, describe, expect, it, vi} from 'vitest';

const {run, requireCli, runOrThrow, runJson, context} = vi.hoisted(() => ({
  run: vi.fn(),
  requireCli: vi.fn(),
  runOrThrow: vi.fn(),
  runJson: vi.fn(),
  context: vi.fn(),
}));

vi.mock('@aimarchirico/commons-project', () => ({
  run,
  requireCli,
  runOrThrow,
  runJson,
  context,
}));

describe('gh', () => {
  beforeEach(() => {
    run.mockReset();
    requireCli.mockReset();
    runOrThrow.mockReset();
    runJson.mockReset();
    context.mockReset();
  });

  it('requireGh asserts a recent enough CLI version', async () => {
    const {requireGh} = await import('../gh.js');
    requireGh();
    expect(requireCli).toHaveBeenCalledWith(
      'gh',
      expect.objectContaining({minVersion: '2.40.0'}),
    );
  });

  it('gh runs the CLI and returns the result', async () => {
    run.mockReturnValue({status: 0, stdout: 'out', stderr: ''});
    const {gh} = await import('../gh.js');
    expect(gh(['repo', 'view'])).toEqual({
      status: 0,
      stdout: 'out',
      stderr: '',
    });
  });

  it('gh wraps a run failure with the install hint', async () => {
    run.mockImplementation(() => {
      throw new Error('gh not found');
    });
    const {gh} = await import('../gh.js');
    expect(() => gh(['repo', 'view'])).toThrow('Install the GitHub CLI');
  });

  it('ghOrThrow delegates to runOrThrow', async () => {
    runOrThrow.mockReturnValue('ok');
    const {ghOrThrow} = await import('../gh.js');
    expect(ghOrThrow(['api', '/x'])).toBe('ok');
    expect(runOrThrow).toHaveBeenCalledWith('gh', ['api', '/x'], undefined);
  });

  it('ghJson delegates to runJson', async () => {
    runJson.mockReturnValue({a: 1});
    const {ghJson} = await import('../gh.js');
    expect(ghJson(['api', '/x'])).toEqual({a: 1});
  });

  it('apiGet returns the parsed JSON on success', async () => {
    run.mockReturnValue({status: 0, stdout: '{"a":1}', stderr: ''});
    const {apiGet} = await import('../gh.js');
    expect(apiGet('/x')).toEqual({a: 1});
  });

  it('apiGet returns undefined for a 404', async () => {
    run.mockReturnValue({status: 1, stdout: '', stderr: 'HTTP 404: Not Found'});
    const {apiGet} = await import('../gh.js');
    expect(apiGet('/missing')).toBeUndefined();
  });

  it('apiGet throws for other failures', async () => {
    run.mockReturnValue({status: 1, stdout: '', stderr: 'HTTP 500'});
    const {apiGet} = await import('../gh.js');
    expect(() => apiGet('/broken')).toThrow('gh api /broken failed');
  });

  it('apiWrite posts each field', async () => {
    runOrThrow.mockReturnValue('');
    const {apiWrite} = await import('../gh.js');
    apiWrite('POST', '/x', {a: '1', b: '2'});
    expect(runOrThrow).toHaveBeenCalledWith(
      'gh',
      ['api', '--method', 'POST', '/x', '--silent', '-f', 'a=1', '-f', 'b=2'],
      undefined,
    );
  });

  it('repoContext derives and reports the repository', async () => {
    runJson.mockReturnValue({owner: {login: 'aimarchirico'}, name: 'commons'});
    const {repoContext} = await import('../gh.js');
    expect(repoContext()).toEqual({
      owner: 'aimarchirico',
      repo: 'commons',
      slug: 'aimarchirico/commons',
    });
    expect(context).toHaveBeenCalledWith(
      'repository',
      'aimarchirico/commons',
      'derived from the working directory',
    );
  });
});
