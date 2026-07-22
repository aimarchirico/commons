import { buildRegex } from '@aimarchirico/commons-ts/folders';
import baseConfig from './eslint.js';
import { APP_FOLDERS } from './folders.js';

export default [
  ...baseConfig,
  {
    files: ['**/src/**/*'],
    rules: {
      'check-file/folder-naming-convention': [
        'error',
        {
          '**/src/**/': buildRegex(APP_FOLDERS)
        }
      ]
    }
  },
  {
    files: ['**/_layout.tsx'],
    rules: {
      'check-file/filename-naming-convention': 'off'
    }
  },
  {
    files: ['**/app/**/*.tsx'],
    rules: {
      'import/no-default-export': 'off'
    }
  }
];
