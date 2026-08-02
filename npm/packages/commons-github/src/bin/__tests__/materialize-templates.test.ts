import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {materializeTemplates} from '../materialize-templates.js';

const {mkdirSync, copyFileSync, cpSync, log} = vi.hoisted(() => ({
  mkdirSync: vi.fn(),
  copyFileSync: vi.fn(),
  cpSync: vi.fn(),
  log: vi.fn(),
}));

vi.mock('fs', () => ({
  default: {
    mkdirSync,
    copyFileSync,
    cpSync,
  },
  mkdirSync,
  copyFileSync,
  cpSync,
}));

describe('materialize-templates.ts', () => {
  beforeEach(() => {
    mkdirSync.mockReset();
    copyFileSync.mockReset();
    cpSync.mockReset();
    log.mockReset();
    vi.spyOn(console, 'log').mockImplementation(log);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('materializes contributing and github templates', () => {
    materializeTemplates();

    expect(mkdirSync).toHaveBeenCalledWith(expect.stringMatching(/\.github$/), {
      recursive: true,
    });
    expect(copyFileSync).toHaveBeenCalledWith(
      expect.stringMatching(/CONTRIBUTING\.md$/),
      expect.stringMatching(/CONTRIBUTING\.md$/),
    );
    expect(cpSync).toHaveBeenCalledWith(
      expect.stringMatching(/github$/),
      expect.stringMatching(/\.github$/),
      {recursive: true},
    );
    expect(log).toHaveBeenCalledWith(
      'Materialized CONTRIBUTING.md and .github templates.',
    );
  });
});
