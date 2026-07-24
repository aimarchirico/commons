import {CORE_FOLDERS as TS_FOLDERS} from '@aimarchirico/commons-ts/folders';

export const CORE_FOLDERS = [
  ...TS_FOLDERS,
  'contexts',
  'hooks',
  'locales',
];

export const UI_FOLDERS = [
  ...CORE_FOLDERS,
  'components',
  'screens',
  'styles',
];

export const APP_FOLDERS = ['app', 'assets', 'lib'];
