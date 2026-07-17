import checkFile from 'eslint-plugin-check-file';
import eslintPluginImport from 'eslint-plugin-import';
import globals from 'globals';
import gts from 'gts';
import {createRequire} from 'module';
import {execFileSync} from 'node:child_process';

const require = createRequire(import.meta.url);
const gtsPrettier = require('gts/.prettierrc.json');

import eslintPluginJsonc from 'eslint-plugin-jsonc';

// Ignore everything git ignores, honoring nested .gitignore files.
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
      import: eslintPluginImport,
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
    files: [
      '**/eslint.config.js',
      '**/eslint.config.ts',
      '**/eslint.ts',
      '**/eslint/*.ts',
      '**/index.js',
      '**/expo.js',
      '**/json.js',
      '**/yaml.js',
      '**/toml.js',
      '**/*.d.ts',
      '**/*config.ts',
      '**/.*.mjs',
    ],
    rules: {
      'import/no-default-export': 'off',
      'check-file/filename-naming-convention': 'off',
    },
  },
];
