import {describe, expect, it} from 'vitest';
import {folderRule} from '@aimarchirico/commons-ts/folders';
import config from './eslint-app';
import baseConfig from './eslint-core';
import {APP_FOLDERS} from './folders';

describe('eslint-app', () => {
  it('extends eslint-core with the app folder rule and overrides', () => {
    expect(config.length).toBe(baseConfig.length + 3);
  });

  it('restricts folders to APP_FOLDERS', () => {
    const folderBlock = config.find(
      block => block.rules?.['check-file/folder-naming-convention'],
    );
    expect(folderBlock).toEqual(folderRule(APP_FOLDERS));
  });

  it('disables the filename convention for _layout.tsx files', () => {
    const layoutBlock = config.find(block =>
      block.files?.includes('**/_layout.tsx'),
    );
    expect(layoutBlock?.rules?.['check-file/filename-naming-convention']).toBe(
      'off',
    );
  });

  it('allows default exports under app/', () => {
    const appBlock = config.find(block => block.files?.includes('**/app/**/*.tsx'));
    expect(appBlock?.rules?.['import/no-default-export']).toBe('off');
  });
});
