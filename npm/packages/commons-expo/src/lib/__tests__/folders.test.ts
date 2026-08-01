import {describe, expect, it} from 'vitest';
import {CORE_FOLDERS as TS_FOLDERS} from '@aimarchirico/commons-ts/folders';
import {APP_FOLDERS, CORE_FOLDERS, UI_FOLDERS} from '../folders';

describe('CORE_FOLDERS', () => {
  it('extends the shared TS folder set', () => {
    expect(CORE_FOLDERS).toEqual([
      ...TS_FOLDERS,
      'contexts',
      'hooks',
      'locales',
    ]);
  });
});

describe('UI_FOLDERS', () => {
  it('extends CORE_FOLDERS with UI-specific folders', () => {
    expect(UI_FOLDERS).toEqual([
      ...CORE_FOLDERS,
      'components',
      'screens',
      'styles',
    ]);
  });
});

describe('APP_FOLDERS', () => {
  it('lists the folders allowed under the app root', () => {
    expect(APP_FOLDERS).toEqual(['app', 'assets', 'lib']);
  });
});
