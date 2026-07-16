// @ts-ignore
import checkFile from 'eslint-plugin-check-file';
// @ts-ignore
import eslintPluginImport from 'eslint-plugin-import';
// @ts-ignore
import eslintPluginJsonc from 'eslint-plugin-jsonc';
// @ts-ignore
import eslintPluginYml from 'eslint-plugin-yml';
import globals from 'globals';
import gts from 'gts';
import {createRequire} from 'module';
import {defineConfig} from 'eslint/config';

const require = createRequire(import.meta.url);
const gtsPrettier = require('gts/.prettierrc.json');

export default defineConfig([
  ...gts,
  {
    rules: {
      'prettier/prettier': ['error', gtsPrettier],
    },
  },
  {
    files: ['**/*.{js,cjs}'],
    languageOptions: {
      sourceType: 'commonjs',
      globals: {...globals.node},
    },
  },
  {
    files: ['**/*.mjs'],
    languageOptions: {
      sourceType: 'module',
      globals: {...globals.node},
    },
  },
  {
    files: ['**/*.{js,cjs,mjs,ts,jsx,tsx}'],
    plugins: {
      'check-file': checkFile,
      'import': eslintPluginImport,
    },
    rules: {
      'import/no-default-export': ['error'],
      'check-file/filename-naming-convention': [
        'error',
        {'**/*.{js,cjs,mjs,ts,jsx,tsx}': 'KEBAB_CASE'},
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
    files: ['**/eslint.config.ts', '**/eslint.ts'],
    rules: {
      'import/no-default-export': 'off',
      'check-file/filename-naming-convention': 'off',
    },
  },
  ...eslintPluginJsonc.configs['flat/recommended-with-jsonc'],
  ...eslintPluginYml.configs['flat/recommended'],
  {
    files: ['**/*.{yml,yaml}'],
    rules: {
      // Customize yaml rules if needed
    }
  },
  {
    files: ['**/*.{json,jsonc,json5}'],
    rules: {
      // Customize json rules if needed
    }
  }
]);
