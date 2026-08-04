import {afterEach, beforeEach, describe, expect, it, vi} from 'vitest';
import {materializeTemplates} from '../materialize-templates.js';

const {mkdirSync, cpSync, log} = vi.hoisted(() => ({
  mkdirSync: vi.fn(),
  cpSync: vi.fn(),
  log: vi.fn(),
}));

vi.mock('fs', () => ({
  default: {
    mkdirSync,
    cpSync,
  },
  mkdirSync,
  cpSync,
}));

describe('materialize-templates.ts', () => {
  beforeEach(() => {
    mkdirSync.mockReset();
    cpSync.mockReset();
    log.mockReset();
    vi.spyOn(console, 'log').mockImplementation(log);
  });

  afterEach(() => {
    vi.restoreAllMocks();
  });

  it('materializes github templates', () => {
    materializeTemplates();

    expect(mkdirSync).toHaveBeenCalledWith(expect.stringMatching(/\.github$/), {
      recursive: true,
    });
    expect(cpSync).toHaveBeenCalledWith(
      expect.stringMatching(/github$/),
      expect.stringMatching(/\.github$/),
      {recursive: true},
    );
    expect(log).toHaveBeenCalledWith(
      'Materialized .github templates.',
    );
  });
});
