import {defineConfig} from 'eslint/config';
import baseConfig from '@aimarchirico/commons-ts/eslint-core';

/** ESLint configuration. */
export default defineConfig([
  ...baseConfig,
  {
    files: ['**/eslint*.ts', '**/vitest-coverage.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
]);
