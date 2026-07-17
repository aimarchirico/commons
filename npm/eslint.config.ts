import eslintPluginToml from 'eslint-plugin-toml';
import eslintPluginYml from 'eslint-plugin-yml';

let tsConfig;
try {
  tsConfig = (await import('@aimarchirico/commons-ts/eslint')).default;
} catch {
  tsConfig = (await import('./packages/commons-ts/eslint.ts')).default;
}

export default [
  ...tsConfig,
  ...eslintPluginToml.configs['flat/recommended'],
  ...eslintPluginYml.configs['flat/recommended'],

  {
    ignores: [
      'packages/**/*',
      'apps/**/*',
      '**/.turbo/**',
      '**/pnpm-lock.yaml',
    ],
  },
  {
    files: ['**/eslint.config.ts'],
    rules: {
      'import/no-default-export': 'off',
      'check-file/filename-naming-convention': 'off',
    },
  },
];
