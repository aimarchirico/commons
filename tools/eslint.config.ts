import eslintPluginToml from 'eslint-plugin-toml';
import eslintPluginYml from 'eslint-plugin-yml';

let tsConfig;
let jsonConfig;
let ymlConfig;
let tomlConfig;

try {
  tsConfig = (await import('@aimarchirico/commons-ts/eslint')).default;
} catch {
  tsConfig = (await import('../npm/packages/commons-ts/eslint.js')).default;
}

export default [
  ...tsConfig,
  ...eslintPluginToml.configs['flat/recommended'],
  ...eslintPluginYml.configs['flat/recommended'],

  {
    ignores: [
      '../npm/packages/**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}',
      '../**/.turbo/**',
      '**/pnpm-lock.yaml',
      '../**/pnpm-lock.yaml',
      '**/commitlint.config.js',
      '../**/commitlint.config.js',
      '**/test.toml',
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
