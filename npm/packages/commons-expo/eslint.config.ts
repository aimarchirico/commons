import {defineConfig} from 'eslint/config';
import baseConfig from './src/lib/eslint-core';

/** ESLint configuration. */
export default defineConfig([
  ...baseConfig,
  {
    files: ['**/eslint*.ts'],
    rules: {
      'import/no-default-export': 'off',
    },
  },
]);
