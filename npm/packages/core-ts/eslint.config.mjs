import {defineConfig} from 'eslint/config';
import gts from 'gts';
import checkFile from 'eslint-plugin-check-file';
import {createRequire} from 'module';

const require = createRequire(import.meta.url);
const gtsPrettier = require('gts/.prettierrc.json');

export default defineConfig([
  ...gts,

  {
    files: ['src/**/*.{js,ts,jsx,tsx}'],
    plugins: {
      'check-file': checkFile,
    },
    rules: {
      'import/no-default-export': ['error'],

      'check-file/filename-naming-convention': [
        'error',
        {'src/**/*.{js,ts,jsx,tsx}': 'KEBAB_CASE'},
      ],

      'max-lines': [
        'error',
        {
          max: 300,
          skipBlankLines: false,
          skipComments: false,
        },
      ],
    },
  },

  {
    files: ['src/app/**/*.{js,ts,jsx,tsx}'],
    rules: {
      'import/no-default-export': 'off',
    },
  },

  {
    files: ['**/_layout.{js,ts,jsx,tsx}'],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },

  {
    rules: {
      'prettier/prettier': ['error', gtsPrettier],
    },
  },
]);
