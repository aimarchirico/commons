import baseConfig from '@aimarchirico/commons-tools/eslint';
import gts from 'gts';
import {createRequire} from 'module';
import {defineConfig} from 'eslint/config';

const require = createRequire(import.meta.url);
const gtsPrettier = require('gts/.prettierrc.json');

export default defineConfig([
  ...baseConfig,
  ...gts,
  {
    rules: {
      'prettier/prettier': ['error', gtsPrettier],
    },
  },
]);
