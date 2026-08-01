import {describe, expect, it} from 'vitest';
import {buildRegex, CORE_FOLDERS, folderRule} from '../folders';

describe('buildRegex', () => {
  it('joins folder names into an alternation group', () => {
    expect(buildRegex(['lib', 'bin'])).toBe('(lib|bin)');
  });

  it('handles a single folder', () => {
    expect(buildRegex(['lib'])).toBe('(lib)');
  });

  it('handles an empty list', () => {
    expect(buildRegex([])).toBe('()');
  });
});

describe('folderRule', () => {
  it('defaults to CORE_FOLDERS', () => {
    const rule = folderRule();
    expect(rule.files).toEqual(['**/src/**/*']);
    expect(rule.rules).toEqual({
      'check-file/folder-naming-convention': [
        'error',
        {'**/src/*/': buildRegex(CORE_FOLDERS)},
      ],
    });
  });

  it('accepts a custom folder list', () => {
    const rule = folderRule(['app', 'assets']);
    expect(rule.rules).toEqual({
      'check-file/folder-naming-convention': [
        'error',
        {'**/src/*/': '(app|assets)'},
      ],
    });
  });
});
