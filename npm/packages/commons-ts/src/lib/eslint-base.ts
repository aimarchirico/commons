import {defineConfig} from 'eslint/config';
import eslintPluginEslintComments from '@eslint-community/eslint-plugin-eslint-comments';
import checkFile from 'eslint-plugin-check-file';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginJsdoc from 'eslint-plugin-jsdoc';
import eslintPluginJsonc from 'eslint-plugin-jsonc';
import gts from 'gts';
import {commonsPlugin} from './commons-plugin';
import {jsdocContexts, jsdocRequire} from './comments';
import {gitignoreConfig} from './gitignore';
import gtsPrettier from 'gts/.prettierrc.json';
import tseslint from 'typescript-eslint';

/** Shared ESLint base configuration. */
export default defineConfig([
  ...gitignoreConfig,
  ...gts,
  ...eslintPluginJsonc.configs['flat/recommended-with-jsonc'],
  {
    plugins: {
      'check-file': checkFile,
    },
    rules: {
      'prettier/prettier': ['error', gtsPrettier],
      'check-file/filename-naming-convention': [
        'error',
        {
          '**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs,json,jsonc,json5}': 'KEBAB_CASE',
        },
      ],
      'check-file/folder-match-with-fex': [
        'error',
        {
          '**/*.test.*': '**/__tests__/',
        },
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
    files: ['**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}'],
    plugins: {
      import: eslintPluginImport,
      commons: commonsPlugin,
      jsdoc: eslintPluginJsdoc,
      '@eslint-community/eslint-comments': eslintPluginEslintComments,
      '@typescript-eslint': tseslint.plugin,
    },
    rules: {
      'import/no-default-export': ['error'],
      'jsdoc/require-jsdoc': [
        'error',
        {
          publicOnly: true,
          require: jsdocRequire,
          contexts: jsdocContexts,
          enableFixer: false,
        },
      ],
      'jsdoc/check-param-names': ['error'],
      'jsdoc/check-tag-names': ['error'],
      'jsdoc/check-types': ['error'],
      'jsdoc/require-param': ['error'],
      'jsdoc/require-returns': ['error'],
      'jsdoc/valid-types': ['error'],
      '@eslint-community/eslint-comments/no-unlimited-disable': 'error',
      '@eslint-community/eslint-comments/no-unused-disable': 'error',
      '@eslint-community/eslint-comments/require-description': 'error',
      '@typescript-eslint/ban-ts-comment': [
        'error',
        {
          'ts-expect-error': 'allow-with-description',
          minimumDescriptionLength: 10,
          'ts-ignore': true,
          'ts-nocheck': true,
          'ts-check': false,
        },
      ],
    },
  },
  {
    files: [
      '**/*.config.*',
      '**/*.d.*',
      '**/*.test.*',
      '**/tsconfig.build.json',
    ],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },
  {
    files: ['**/*.config.{ts,mts,cts,js,mjs,cjs}'],
    rules: {
      'import/no-default-export': 'off',
      'commons/default-export-shape': ['error'],
    },
  },
]);
