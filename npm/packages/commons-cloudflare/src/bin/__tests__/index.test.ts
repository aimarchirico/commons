import {describe, expect, it, vi} from 'vitest';

const {runCli} = vi.hoisted(() => ({runCli: vi.fn()}));

vi.mock('../cli.js', () => ({runCli}));

describe('index.ts', () => {
  it('invokes runCli unconditionally when the module is loaded', async () => {
    await import('../index.js');
    expect(runCli).toHaveBeenCalled();
  });
});
