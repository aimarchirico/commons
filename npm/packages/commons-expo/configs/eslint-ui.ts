import { buildRegex } from '@aimarchirico/commons-ts/folders';
import { UI_FOLDERS } from './folders.js';

export default [
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
  }
];
