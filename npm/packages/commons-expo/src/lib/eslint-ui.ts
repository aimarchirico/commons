import {folderRule} from '@aimarchirico/commons-ts/folders';
import {UI_FOLDERS} from './folders';
import baseConfig from './eslint-base';

export default [
  ...baseConfig,
  folderRule(UI_FOLDERS),
  {
    files: ['**/*.{web,android}.tsx'],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },
];
