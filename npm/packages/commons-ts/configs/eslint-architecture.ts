import { FOLDERS, buildRegex } from './folders.js';

export default [
  {
    files: ['**/src/**/*'],
    rules: {
      'check-file/folder-naming-convention': [
        'error',
        {
          '**/src/**/': buildRegex(FOLDERS)
        }
      ]
    }
  }
];
