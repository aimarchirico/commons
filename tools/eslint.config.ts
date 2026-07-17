import eslintPluginToml from 'eslint-plugin-toml';
import eslintPluginYml from 'eslint-plugin-yml';

import tsConfig from '@aimarchirico/commons-ts/eslint';

export default [
  ...tsConfig,
  ...eslintPluginToml.configs['flat/recommended'],
  ...eslintPluginYml.configs['flat/recommended'],

  {
    ignores: [
      '**/npm/packages/**',
      '**/node_modules/**',
      '**/dist/**',
      '**/build/**',
      '**/.turbo/**',
      '**/pnpm-lock.yaml',
      '**/*.lock',
      '**/maven/gradle/libs.versions.toml',
    ],
  },
  {
    files: ['**/*.toml'],
    rules: {
      'prettier/prettier': 'off',
    },
  },
];
