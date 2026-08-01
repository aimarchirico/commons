import type {Linter} from 'eslint';
import {folderRule} from '@aimarchirico/commons-ts/folders';
import {UI_FOLDERS} from './folders';
import baseConfig from './eslint-core';

const config: Linter.Config[] = [
  ...baseConfig,
  folderRule(UI_FOLDERS),
  {
    files: ['**/*.{web,android}.tsx'],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },
];

export default config;
