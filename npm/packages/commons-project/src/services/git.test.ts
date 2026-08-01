import {afterEach, describe, expect, it, vi} from 'vitest';

const {run} = vi.hoisted(() => ({run: vi.fn()}));
vi.mock('./cli.js', () => ({run}));

describe('defaultBranch', () => {
  afterEach(() => {
    run.mockReset();
  });

  it('returns the branch name with the origin/ prefix stripped', async () => {
    run.mockReturnValue({status: 0, stdout: 'origin/main', stderr: ''});
    const {defaultBranch} = await import('./git');
    expect(defaultBranch()).toBe('main');
    expect(run).toHaveBeenCalledWith('git', [
      'symbolic-ref',
      '--short',
      'refs/remotes/origin/HEAD',
    ]);
  });

  it('returns undefined when there is no remote', async () => {
    run.mockReturnValue({status: 128, stdout: '', stderr: 'fatal'});
    const {defaultBranch} = await import('./git');
    expect(defaultBranch()).toBeUndefined();
  });

  it('returns undefined when stdout is empty after stripping', async () => {
    run.mockReturnValue({status: 0, stdout: '', stderr: ''});
    const {defaultBranch} = await import('./git');
    expect(defaultBranch()).toBeUndefined();
  });
});
