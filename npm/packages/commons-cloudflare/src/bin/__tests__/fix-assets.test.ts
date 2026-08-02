import {beforeEach, describe, expect, it, vi} from 'vitest';
import {fixAssets} from '../fix-assets.js';

const {test, mv, replaceInFileSync} = vi.hoisted(() => ({
  test: vi.fn(),
  mv: vi.fn(),
  replaceInFileSync: vi.fn(),
}));

vi.mock('shelljs', () => ({
  default: {test, mv},
}));

vi.mock('replace-in-file', () => ({
  replaceInFileSync,
}));

describe('fix-assets.ts', () => {
  beforeEach(() => {
    test.mockReset();
    mv.mockReset();
    replaceInFileSync.mockReset();
  });

  it('renames node_modules and rewrites references when present', () => {
    test.mockReturnValue(true);

    fixAssets();

    expect(test).toHaveBeenCalledWith('-d', 'dist/assets/node_modules');
    expect(mv).toHaveBeenCalledWith(
      'dist/assets/node_modules',
      'dist/assets/nodemodules',
    );
    expect(replaceInFileSync).toHaveBeenCalledWith({
      files: 'dist/**/*',
      from: /assets\/node_modules/g,
      to: 'assets/nodemodules',
    });
  });

  it('does nothing when node_modules is absent', () => {
    test.mockReturnValue(false);

    fixAssets();

    expect(mv).not.toHaveBeenCalled();
    expect(replaceInFileSync).not.toHaveBeenCalled();
  });
});
