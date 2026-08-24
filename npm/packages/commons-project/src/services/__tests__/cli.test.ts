import {beforeEach, describe, expect, it, vi} from 'vitest';

const {spawnSync} = vi.hoisted(() => ({spawnSync: vi.fn()}));

vi.mock('child_process', () => ({spawnSync}));

async function importCli() {
  vi.resetModules();
  return import('../cli');
}

describe('run', () => {
  beforeEach(() => {
    spawnSync.mockReset();
  });

  it('runs a string command and trims output', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: ' out \n', stderr: ''});
    const {run} = await importCli();
    expect(run('echo', ['hi'])).toEqual({status: 0, stdout: 'out', stderr: ''});
  });

  it('runs a resolved {argv, name} command with its prefix args', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: 'ok', stderr: ''});
    const {run} = await importCli();
    run({argv: ['node', '/bin/tool'], name: 'tool'}, ['--flag']);
    expect(spawnSync).toHaveBeenCalledWith(
      'node',
      ['/bin/tool', '--flag'],
      expect.objectContaining({encoding: 'utf8'}),
    );
  });

  it('lets options.shell override the platform default', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: '', stderr: ''});
    const {run} = await importCli();
    run('echo', ['hi'], undefined, {shell: false});
    expect(spawnSync).toHaveBeenCalledWith(
      'echo',
      ['hi'],
      expect.objectContaining({shell: false}),
    );
  });

  it('defaults a missing status to 1', async () => {
    spawnSync.mockReturnValue({status: null, stdout: '', stderr: ''});
    const {run} = await importCli();
    expect(run('echo', []).status).toBe(1);
  });

  it('throws naming the command when spawning fails', async () => {
    spawnSync.mockReturnValue({error: new Error('ENOENT')});
    const {run} = await importCli();
    expect(() => run('missing-cmd', [])).toThrow(
      'Could not run "missing-cmd": ENOENT.',
    );
  });

  it('throws naming the resolved command on spawn failure', async () => {
    spawnSync.mockReturnValue({error: new Error('ENOENT')});
    const {run} = await importCli();
    expect(() => run({argv: ['node', '/bin/tool'], name: 'tool'}, [])).toThrow(
      'Could not run "tool": ENOENT.',
    );
  });
});

describe('runOrThrow', () => {
  beforeEach(() => spawnSync.mockReset());

  it('returns stdout on success', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: 'ok', stderr: ''});
    const {runOrThrow} = await importCli();
    expect(runOrThrow('echo', ['hi'])).toBe('ok');
  });

  it('throws with stderr on failure', async () => {
    spawnSync.mockReturnValue({status: 1, stdout: '', stderr: 'bad'});
    const {runOrThrow} = await importCli();
    expect(() => runOrThrow('echo', ['hi'])).toThrow('echo hi failed:\nbad');
  });
});

describe('runJson', () => {
  it('parses stdout as JSON', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: '{"a":1}', stderr: ''});
    const {runJson} = await importCli();
    expect(runJson('echo', [])).toEqual({a: 1});
  });
});

describe('runStreamed', () => {
  beforeEach(() => spawnSync.mockReset());

  it('returns the exit status', async () => {
    spawnSync.mockReturnValue({status: 0});
    const {runStreamed} = await importCli();
    expect(runStreamed('echo', ['hi'])).toBe(0);
    expect(spawnSync).toHaveBeenCalledWith(
      'echo',
      ['hi'],
      expect.objectContaining({stdio: 'inherit'}),
    );
  });

  it('lets options.shell override the platform default', async () => {
    spawnSync.mockReturnValue({status: 0});
    const {runStreamed} = await importCli();
    runStreamed('scp', ['a', 'b'], {shell: false});
    expect(spawnSync).toHaveBeenCalledWith(
      'scp',
      ['a', 'b'],
      expect.objectContaining({shell: false}),
    );
  });

  it('throws naming the command when spawning fails', async () => {
    spawnSync.mockReturnValue({error: new Error('ENOENT')});
    const {runStreamed} = await importCli();
    expect(() => runStreamed('missing', [])).toThrow('Could not run "missing"');
  });
});
