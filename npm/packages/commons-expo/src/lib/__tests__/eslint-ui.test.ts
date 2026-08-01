import {describe, expect, it} from 'vitest';
import {folderRule} from '@aimarchirico/commons-ts/folders';
import config from '../eslint-ui';
import baseConfig from '../eslint-core';
import {UI_FOLDERS} from '../folders';

describe('eslint-ui', () => {
  it('extends eslint-core with the UI folder rule and an override', () => {
    expect(config.length).toBe(baseConfig.length + 2);
  });

  it('restricts folders to UI_FOLDERS', () => {
    const folderBlock = config.findLast(
      block => block.rules?.['check-file/folder-naming-convention'],
    );
    expect(folderBlock).toEqual(folderRule(UI_FOLDERS));
  });

  it('disables the filename convention for web/android tsx files', () => {
    const override = config.find(block =>
      block.files?.includes('**/*.{web,android}.tsx'),
    );
    expect(override?.rules?.['check-file/filename-naming-convention']).toBe(
      'off',
    );
  });
});
