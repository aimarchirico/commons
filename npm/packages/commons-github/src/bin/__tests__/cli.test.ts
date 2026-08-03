import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const {
  exit,
  error,
  createProject,
  createEnvironments,
  syncVariables,
  setSecrets,
  materializeTemplates,
} = vi.hoisted(() => ({
  exit: vi.fn((code?: number) => {
    throw new Error(`process.exit(${code})`);
  }),
  error: vi.fn(),
  createProject: vi.fn(),
  createEnvironments: vi.fn(),
  syncVariables: vi.fn(),
  setSecrets: vi.fn(),
  materializeTemplates: vi.fn(),
}));

vi.mock('../create-project.js', () => ({createProject}));
vi.mock('../create-environments.js', () => ({createEnvironments}));
vi.mock('../sync-variables.js', () => ({syncVariables}));
vi.mock('../set-secrets.js', () => ({setSecrets}));
vi.mock('../materialize-templates.js', () => ({materializeTemplates}));

describe('cli.ts', () => {
  beforeEach(() => {
    exit.mockReset();
    error.mockReset();
    vi.spyOn(process, 'exit').mockImplementation(
      exit as unknown as typeof process.exit,
    );
    vi.spyOn(console, 'error').mockImplementation(error);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('prints usage and exits when no command argument is provided', async () => {
    const {runCli} = await import('../cli.js');
    expect(() => runCli(['node', 'cli.js'])).toThrow('process.exit(1)');
    expect(error).toHaveBeenCalledWith(expect.stringContaining('Usage:'));
    expect(exit).toHaveBeenCalledWith(1);
  });

  it('prints usage and exits when an invalid command is provided', async () => {
    const {runCli} = await import('../cli.js');
    expect(() => runCli(['node', 'cli.js', 'unknown-command'])).toThrow(
      'process.exit(1)',
    );
    expect(error).toHaveBeenCalledWith(expect.stringContaining('Usage:'));
    expect(exit).toHaveBeenCalledWith(1);
  });

  it.each([
    ['create-project', createProject],
    ['create-environments', createEnvironments],
    ['sync-variables', syncVariables],
    ['set-secrets', setSecrets],
    ['materialize-templates', materializeTemplates],
  ])('dispatches %s to its handler', async (verb, handler) => {
    const {runCli} = await import('../cli.js');
    expect(() => runCli(['node', 'cli.js', verb])).not.toThrow();
    await vi.waitFor(() => expect(handler).toHaveBeenCalled());
  });
});
