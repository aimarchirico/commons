import path from 'path';
import {beforeEach, describe, expect, it, vi} from 'vitest';

const expectedBin = path.join('/deps', 'tool', 'bin', 'cli.js');

const {spawnSync, readFileSync, requireResolve, fail} = vi.hoisted(() => ({
  spawnSync: vi.fn(),
  readFileSync: vi.fn(),
  requireResolve: vi.fn(),
  fail: vi.fn((message: string) => {
    throw new Error(message);
  }),
}));

vi.mock('child_process', () => ({spawnSync}));
vi.mock('module', () => ({
  createRequire: () => ({resolve: requireResolve}),
}));
vi.mock('fs', () => ({default: {readFileSync}, readFileSync}));
vi.mock('../report.js', () => ({fail}));

const importCli = async () => {
  vi.resetModules();
  return import('../cli');
};

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

  it('throws naming the command when spawning fails', async () => {
    spawnSync.mockReturnValue({error: new Error('ENOENT')});
    const {runStreamed} = await importCli();
    expect(() => runStreamed('missing', [])).toThrow('Could not run "missing"');
  });
});

describe('packageBin', () => {
  beforeEach(() => {
    requireResolve.mockReset();
    readFileSync.mockReset();
  });

  it('resolves the bin path for a string bin field', async () => {
    requireResolve.mockReturnValue('/deps/tool/package.json');
    readFileSync.mockReturnValue(JSON.stringify({bin: './bin/cli.js'}));
    const {packageBin} = await importCli();
    expect(packageBin('file:///caller.js', 'tool', 'tool')).toEqual([
      process.execPath,
      expectedBin,
    ]);
  });

  it('resolves the bin path for an object bin field keyed by binName', async () => {
    requireResolve.mockReturnValue('/deps/tool/package.json');
    readFileSync.mockReturnValue(
      JSON.stringify({bin: {tool: './bin/cli.js', other: './bin/other.js'}}),
    );
    const {packageBin} = await importCli();
    expect(packageBin('file:///caller.js', 'tool', 'tool')).toEqual([
      process.execPath,
      expectedBin,
    ]);
  });

  it('returns undefined when the package has no matching bin entry', async () => {
    requireResolve.mockReturnValue('/deps/tool/package.json');
    readFileSync.mockReturnValue(JSON.stringify({}));
    const {packageBin} = await importCli();
    expect(packageBin('file:///caller.js', 'tool', 'tool')).toBeUndefined();
  });

  it('returns undefined when resolution throws', async () => {
    requireResolve.mockImplementation(() => {
      throw new Error('not found');
    });
    const {packageBin} = await importCli();
    expect(packageBin('file:///caller.js', 'tool', 'tool')).toBeUndefined();
  });
});

describe('requireCli', () => {
  beforeEach(() => {
    spawnSync.mockReset();
    fail.mockClear();
  });

  it('fails when the CLI cannot be run at all', async () => {
    spawnSync.mockReturnValue({error: new Error('ENOENT')});
    const {requireCli} = await importCli();
    expect(() =>
      requireCli('tool', {minVersion: '1.0.0', installHint: 'install it'}),
    ).toThrow('is not available');
  });

  it('fails when the CLI exits non-zero', async () => {
    spawnSync.mockReturnValue({status: 1, stdout: '', stderr: ''});
    const {requireCli} = await importCli();
    expect(() =>
      requireCli('tool', {minVersion: '1.0.0', installHint: 'install it'}),
    ).toThrow('is not usable');
  });

  it('passes when the version meets the minimum', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: '2.40.1', stderr: ''});
    const {requireCli} = await importCli();
    expect(() =>
      requireCli('tool', {minVersion: '2.40.0', installHint: 'install it'}),
    ).not.toThrow();
  });

  it('fails when the version is below the minimum', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: '1.9.0', stderr: ''});
    const {requireCli} = await importCli();
    expect(() =>
      requireCli('tool', {minVersion: '2.0.0', installHint: 'install it'}),
    ).toThrow('older than the required 2.0.0');
  });

  it('passes when the version cannot be parsed', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: 'unknown', stderr: ''});
    const {requireCli} = await importCli();
    expect(() =>
      requireCli('tool', {minVersion: '2.0.0', installHint: 'install it'}),
    ).not.toThrow();
  });

  it('uses custom version args when given', async () => {
    spawnSync.mockReturnValue({status: 0, stdout: '2.0.0', stderr: ''});
    const {requireCli} = await importCli();
    requireCli('tool', {
      minVersion: '2.0.0',
      installHint: 'install it',
      versionArgs: ['version'],
    });
    expect(spawnSync).toHaveBeenCalledWith(
      'tool',
      ['version'],
      expect.anything(),
    );
  });
});

describe('resolveTool', () => {
  beforeEach(() => {
    requireResolve.mockReset();
    readFileSync.mockReset();
    spawnSync.mockReset();
    fail.mockClear();
  });

  it('returns the local bin without a version check when minVersion is absent', async () => {
    requireResolve.mockReturnValue('/deps/tool/package.json');
    readFileSync.mockReturnValue(JSON.stringify({bin: './bin/cli.js'}));
    const {resolveTool} = await importCli();
    expect(
      resolveTool({
        from: 'file:///caller.js',
        package: 'tool',
        bin: 'tool',
        installHint: 'install it',
      }),
    ).toEqual({
      argv: [process.execPath, expectedBin],
      name: 'tool',
    });
  });

  it('fails when no minVersion is given and local resolution fails', async () => {
    requireResolve.mockImplementation(() => {
      throw new Error('not found');
    });
    const {resolveTool} = await importCli();
    expect(() =>
      resolveTool({
        from: 'file:///caller.js',
        package: 'tool',
        bin: 'tool',
        installHint: 'install it',
      }),
    ).toThrow('could not be resolved from tool');
  });

  it('falls back to PATH and checks the version when minVersion is given', async () => {
    requireResolve.mockImplementation(() => {
      throw new Error('not found');
    });
    spawnSync.mockReturnValue({status: 0, stdout: '3.0.0', stderr: ''});
    const {resolveTool} = await importCli();
    expect(
      resolveTool({
        from: 'file:///caller.js',
        package: 'tool',
        bin: 'tool',
        minVersion: '2.0.0',
        installHint: 'install it',
      }),
    ).toBe('tool');
  });

  it('prefers the local resolution and checks its version when minVersion is given', async () => {
    requireResolve.mockReturnValue('/deps/tool/package.json');
    readFileSync.mockReturnValue(JSON.stringify({bin: './bin/cli.js'}));
    spawnSync.mockReturnValue({status: 0, stdout: '3.0.0', stderr: ''});
    const {resolveTool} = await importCli();
    expect(
      resolveTool({
        from: 'file:///caller.js',
        package: 'tool',
        bin: 'tool',
        minVersion: '2.0.0',
        installHint: 'install it',
      }),
    ).toEqual({
      argv: [process.execPath, expectedBin],
      name: 'tool',
    });
  });
});
