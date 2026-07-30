import eslintPluginEslintComments from '@eslint-community/eslint-plugin-eslint-comments';
import checkFile from 'eslint-plugin-check-file';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginJsdoc from 'eslint-plugin-jsdoc';
import eslintPluginJsonc from 'eslint-plugin-jsonc';
import gts from 'gts';
import {commonsPlugin} from './commons-plugin';
import {DOC_ELIGIBLE_VISITORS} from './comments';
import {execFileSync} from 'node:child_process';
import gtsPrettier from 'gts/.prettierrc.json';
import tseslint from 'typescript-eslint';

/**
 * Node types `jsdoc/require-jsdoc`'s `require` option supports directly. Any
 * `DOC_ELIGIBLE_VISITORS` entry outside this set is passed through
 * `contexts` instead, so the require-side rule targets exactly the same
 * declarations that `commons/public-jsdoc-only` allows to carry a JSDoc
 * block.
 */
const JSDOC_REQUIRE_KEYS = new Set([
  'ArrowFunctionExpression',
  'ClassDeclaration',
  'ClassExpression',
  'FunctionDeclaration',
  'FunctionExpression',
  'MethodDefinition',
]);

const jsdocRequire = Object.fromEntries(
  DOC_ELIGIBLE_VISITORS.filter(type => JSDOC_REQUIRE_KEYS.has(type)).map(
    type => [type, true],
  ),
);
const jsdocContexts = DOC_ELIGIBLE_VISITORS.filter(
  type => !JSDOC_REQUIRE_KEYS.has(type),
);

const gitignored = (cwd: string): string[] => {
  try {
    return execFileSync(
      'git',
      [
        'ls-files',
        '-z',
        '--others',
        '--ignored',
        '--exclude-standard',
        '--directory',
      ],
      {cwd, encoding: 'utf8', maxBuffer: 64 * 1024 * 1024},
    )
      .split('\0')
      .filter(Boolean)
      .map(entry => (entry.endsWith('/') ? `${entry}**` : entry));
  } catch {
    return [];
  }
};

const ignores = gitignored(process.cwd());
const gitignoreConfig = ignores.length ? [{ignores}] : [];

export default [
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
    },
    rules: {
      'import/no-default-export': ['error'],
      'commons/public-jsdoc-only': ['error'],
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
    },
  },
  {
    files: ['**/*.{ts,tsx,mts,cts}'],
    plugins: {
      '@typescript-eslint': tseslint.plugin,
    },
    rules: {
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
    files: ['**/*.config.ts', '**/*.d.ts', '**/tsconfig.build.json'],
    rules: {
      'check-file/filename-naming-convention': 'off',
      'import/no-default-export': 'off',
    },
  },
];
