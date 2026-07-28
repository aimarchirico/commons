import checkFile from 'eslint-plugin-check-file';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginJsdoc from 'eslint-plugin-jsdoc';
import eslintPluginJsonc from 'eslint-plugin-jsonc';
import gts from 'gts';
import {commonsPlugin} from './comments';
import {execFileSync} from 'node:child_process';
import gtsPrettier from 'gts/.prettierrc.json';

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
      import: eslintPluginImport,
    },
    rules: {
      'prettier/prettier': ['error', gtsPrettier],
      'import/no-default-export': ['error'],
      'check-file/filename-naming-convention': [
        'error',
        {'**/*.{ts,tsx,json}': 'KEBAB_CASE'},
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
      commons: commonsPlugin,
      jsdoc: eslintPluginJsdoc,
    },
    rules: {
      'commons/no-non-doc-comment': ['error'],
      'jsdoc/require-jsdoc': [
        'error',
        {
          publicOnly: true,
          require: {
            ArrowFunctionExpression: true,
            ClassDeclaration: true,
            ClassExpression: true,
            FunctionDeclaration: true,
            FunctionExpression: true,
          },
          enableFixer: false,
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
