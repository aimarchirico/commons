import { buildRegex } from '@aimarchirico/commons-ts/folders';
import baseConfig from './eslint.js';
import { UI_FOLDERS } from './folders.js';

export default [
  ...baseConfig,
  {
    files: ['**/src/**/*'],
    rules: {
      'check-file/folder-naming-convention': [
        'error',
        {
          '**/src/**/': buildRegex(UI_FOLDERS)
        }
      ]
    }
  },
  {
    files: ['**/*.{web,native,ios,android}.{ts,tsx}'],
    rules: {
      'check-file/filename-naming-convention': 'off'
    }
  }
];
