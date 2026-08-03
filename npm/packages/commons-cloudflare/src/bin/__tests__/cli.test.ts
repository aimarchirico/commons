import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';

const {
  exit,
  error,
  fixAssets,
  createPagesProject,
  setPagesEnv,
  addTunnelRoute,
  createServiceToken,
} = vi.hoisted(() => ({
  exit: vi.fn((code?: number) => {
    throw new Error(`process.exit(${code})`);
  }),
  error: vi.fn(),
  fixAssets: vi.fn(),
  createPagesProject: vi.fn(),
  setPagesEnv: vi.fn(),
  addTunnelRoute: vi.fn(),
  createServiceToken: vi.fn(),
}));

vi.mock('../fix-assets.js', () => ({fixAssets}));
vi.mock('../create-pages-project.js', () => ({createPagesProject}));
vi.mock('../set-pages-env.js', () => ({setPagesEnv}));
vi.mock('../add-tunnel-route.js', () => ({addTunnelRoute}));
vi.mock('../create-service-token.js', () => ({createServiceToken}));

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
    ['fix-assets', fixAssets],
    ['create-pages-project', createPagesProject],
    ['set-pages-env', setPagesEnv],
    ['add-tunnel-route', addTunnelRoute],
    ['create-service-token', createServiceToken],
  ])('dispatches %s to its handler', async (verb, handler) => {
    const {runCli} = await import('../cli.js');
    expect(() => runCli(['node', 'cli.js', verb])).not.toThrow();
    await vi.waitFor(() => expect(handler).toHaveBeenCalled());
  });
});
