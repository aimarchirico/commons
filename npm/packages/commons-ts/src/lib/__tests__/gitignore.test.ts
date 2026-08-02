import {afterEach, describe, expect, it, vi} from 'vitest';

async function importFresh() {
  vi.resetModules();
  return import('../gitignore');
}

describe('gitignoreConfig', () => {
  afterEach(() => {
    vi.doUnmock('node:child_process');
    vi.resetModules();
  });

  it('is empty when git reports no ignored paths', async () => {
    vi.doMock('node:child_process', () => ({
      execFileSync: vi.fn(() => ''),
    }));
    const {gitignoreConfig} = await importFresh();
    expect(gitignoreConfig).toEqual([]);
  });

  it('is empty when git is unavailable', async () => {
    vi.doMock('node:child_process', () => ({
      execFileSync: vi.fn(() => {
        throw new Error('git not found');
      }),
    }));
    const {gitignoreConfig} = await importFresh();
    expect(gitignoreConfig).toEqual([]);
  });

  it('converts directory entries into glob patterns', async () => {
    vi.doMock('node:child_process', () => ({
      execFileSync: vi.fn(() => 'dist/\0build.log\0'),
    }));
    const {gitignoreConfig} = await importFresh();
    expect(gitignoreConfig).toEqual([{ignores: ['dist/**', 'build.log']}]);
  });
});
