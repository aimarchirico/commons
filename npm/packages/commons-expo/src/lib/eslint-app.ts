import {folderRule} from '@aimarchirico/commons-ts/folders';
import {APP_FOLDERS} from './folders';
import baseConfig from './eslint-base';

export default [
  ...baseConfig,
  folderRule(APP_FOLDERS),
  {
    files: ['**/_layout.tsx'],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },
  {
    files: ['**/app/**/*.tsx'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
];
