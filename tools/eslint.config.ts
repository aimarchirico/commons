let tsConfig;
let jsonConfig;
let ymlConfig;
let tomlConfig;

try {
  tsConfig = (await import('@aimarchirico/commons-ts/eslint')).default;
  jsonConfig = (await import('@aimarchirico/commons-tools/eslint/json')).default;
  ymlConfig = (await import('@aimarchirico/commons-tools/eslint/yml')).default;
  tomlConfig = (await import('@aimarchirico/commons-tools/eslint/toml')).default;
} catch {
  tsConfig = (await import('../npm/packages/commons-ts/eslint.ts')).default;
  jsonConfig = (await import('../npm/packages/commons-tools/eslint/json.ts'))
    .default;
  ymlConfig = (await import('../npm/packages/commons-tools/eslint/yml.ts'))
    .default;
  tomlConfig = (await import('../npm/packages/commons-tools/eslint/toml.ts'))
    .default;
}

export default [
  ...tsConfig,
  ...jsonConfig,
  ...ymlConfig,
  ...tomlConfig,
  {
    ignores: [
      '../npm/packages/**/*.{ts,tsx,mts,cts,js,jsx,mjs,cjs}',
      '../**/.turbo/**',
      '../**/pnpm-lock.yaml',
      '../**/commitlint.config.js',
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
