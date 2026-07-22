import { buildRegex } from '@aimarchirico/commons-ts/folders';
import { APP_FOLDERS } from './folders.js';

export default [
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
  }
];
