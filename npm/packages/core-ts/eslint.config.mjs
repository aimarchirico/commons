import checkFile from 'eslint-plugin-check-file';
import eslintPluginImport from 'eslint-plugin-import';
import globals from 'globals';
import gts from 'gts';
import {createRequire} from 'module';
import {defineConfig} from 'eslint/config';

const require = createRequire(import.meta.url);
const gtsPrettier = require('gts/.prettierrc.json');

export default defineConfig([
  ...gts,

  {
    files: ['bin/**/*.js', 'scripts/**/*.js',],
    languageOptions: {
      sourceType: 'commonjs',
      globals: {...globals.node},
    },
  },

  {
    files: ['**/*.{js,ts,jsx,tsx}'],
    plugins: {
      'check-file': checkFile,
      'import': eslintPluginImport,
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
