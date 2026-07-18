import checkFile from 'eslint-plugin-check-file';
import eslintPluginImport from 'eslint-plugin-import';
import eslintPluginJsonc from 'eslint-plugin-jsonc';
import globals from 'globals';
import gts from 'gts';
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
        {'**/*.{ts,tsx,mjs,cjs}': 'KEBAB_CASE'},
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
    files: ['**/*.mjs'],
    languageOptions: {
      globals: {...globals.node},
    },
  },
  {
    files: ['**/eslint.config.ts', '**/eslint.ts'],
    rules: {
      'check-file/filename-naming-convention': 'off',
      'import/no-default-export': 'off',
    },
  },
  {
    files: ['*.config.{ts,cjs}'],
    rules: {
      'check-file/filename-naming-convention': 'off',
    },
  },
];
